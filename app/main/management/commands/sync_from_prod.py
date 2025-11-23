import os
import subprocess
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Синхронизация dev базы данных с prod базой'

    def add_arguments(self, parser):
        pass  # Все параметры убраны - команда всегда делает бэкап и запускается сразу

    def handle(self, *args, **options):
        # Проверка, что мы в dev окружении
        if not settings.DEV:
            self.stdout.write(
                self.style.ERROR('ОШИБКА: Эта команда может выполняться только в DEV окружении!')
            )
            return

        # Получение настроек баз данных
        prod_db = {
            'name': settings.DB_NAME,
            'user': settings.DB_USER,
            'password': settings.DB_PASS,
            'host': settings.DB_HOST,
            'port': settings.DB_PORT,
        }

        dev_db = {
            'name': settings.DB_NAME_DEV,
            'user': settings.DB_USER_DEV,
            'password': settings.DB_PASS_DEV,
            'host': settings.DB_HOST_DEV,
            'port': settings.DB_PORT_DEV,
        }

        logger.info("[SYNC_FROM_PROD] Starting database sync...")
        self.stdout.write(
            self.style.WARNING(
                f'\n🔄 Синхронизация dev базы с prod\n'
                f'   Prod: {prod_db["name"]} → Dev: {dev_db["name"]}\n'
            )
        )

        # Создание директории для бэкапов
        backup_dir = os.path.join(settings.BASE_DIR, '..', 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Пути к файлам дампов
        prod_dump_file = os.path.join(backup_dir, f'prod_dump_{timestamp}.sql')
        dev_backup_file = os.path.join(backup_dir, f'dev_backup_{timestamp}.sql')

        try:
            # Шаг 1: Создание бэкапа dev базы
            self.stdout.write('1. Создание бэкапа dev базы...')
            self._create_dump(dev_db, dev_backup_file)
            self.stdout.write(self.style.SUCCESS(f'   ✓ Бэкап сохранен: {dev_backup_file}'))

            # Шаг 2: Создание дампа prod базы
            self.stdout.write('2. Создание дампа prod базы...')
            self._create_dump(prod_db, prod_dump_file)
            self.stdout.write(self.style.SUCCESS(f'   ✓ Дамп создан: {prod_dump_file}'))

            # Шаг 3: Восстановление данных из prod в dev (с автоматической очисткой)
            self.stdout.write('3. Восстановление данных в dev базу (с очисткой)...')
            self._restore_dump(dev_db, prod_dump_file)
            self.stdout.write(self.style.SUCCESS('   ✓ Данные восстановлены'))

            self.stdout.write(self.style.SUCCESS(f'\n✅ Синхронизация завершена успешно!'))
            self.stdout.write(f'   📦 Бэкап dev базы: {dev_backup_file}')
            self.stdout.write(f'   📦 Дамп prod базы: {prod_dump_file}')

            logger.info("[SYNC_FROM_PROD] Sync completed successfully")

        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Ошибка при выполнении команды: {e}')
            )
            logger.error(f"[SYNC_FROM_PROD] Error: {e}")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Неожиданная ошибка: {e}')
            )
            logger.error(f"[SYNC_FROM_PROD] Unexpected error: {e}")

    def _create_dump(self, db_config, dump_file):
        """Создание дампа базы данных"""
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']

        cmd = [
            'pg_dump',
            '-h', db_config['host'],
            '-p', db_config['port'],
            '-U', db_config['user'],
            '-d', db_config['name'],
            '-F', 'c',  # custom format (более быстрый)
            '-f', dump_file,
        ]

        subprocess.run(cmd, env=env, check=True, capture_output=True)

    def _restore_dump(self, db_config, dump_file):
        """Восстановление дампа в базу данных с автоматической очисткой"""
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']

        cmd = [
            'pg_restore',
            '-h', db_config['host'],
            '-p', db_config['port'],
            '-U', db_config['user'],
            '-d', db_config['name'],
            '--clean',  # Удалить объекты базы данных перед их созданием
            '--if-exists',  # Использовать IF EXISTS при удалении объектов
            '-v',  # verbose
            dump_file,
        ]

        # Выполняем восстановление, игнорируем предупреждения о несуществующих объектах
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        # Проверяем критические ошибки (не предупреждения)
        if result.returncode != 0:
            # Некоторые ошибки допустимы (например, объекты не существуют при первом запуске)
            stderr_lower = result.stderr.lower()
            critical_errors = ['fatal:', 'error: connection', 'permission denied', 'authentication failed']

            if any(err in stderr_lower for err in critical_errors):
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
