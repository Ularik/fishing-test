import os
import subprocess
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Синхронизация dev базы данных с prod базой'

    def add_arguments(self, parser):
        pass  # Все параметры убраны - команда всегда делает бэкап и запускается сразу

    def handle(self, *args, **options):
        # Проверка, что мы в dev окружении
        if not settings.DEV:
            print('ОШИБКА: Эта команда может выполняться только в DEV окружении!')
            return

        # Получение настроек баз данных из settings
        prod_db = {
            'name': settings.DB_NAME,
            'user': settings.DB_USER,
            'password': settings.DB_PASS,
            'host': settings.DB_HOST,
            'port': '5432',
        }

        dev_db = {
            'name': settings.DB_NAME_DEV,
            'user': settings.DB_USER_DEV,
            'password': settings.DB_PASS_DEV,
            'host': settings.DB_HOST_DEV,
            'port': '5432',
        }

        print(f'\nСинхронизация dev базы с prod')
        print(f'Prod: {prod_db["name"]} -> Dev: {dev_db["name"]}\n')

        # Создание директории для бэкапов
        backup_dir = os.path.join(settings.BASE_DIR, '..', 'backups')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Пути к файлам дампов
        prod_dump_file = os.path.join(backup_dir, f'prod_dump_{timestamp}.sql')
        dev_backup_file = os.path.join(backup_dir, f'dev_backup_{timestamp}.sql')

        try:
            # Шаг 1: Создание бэкапа dev базы
            print('1. Создание бэкапа dev базы...')
            self._create_dump(dev_db, dev_backup_file)
            print(f'   Бэкап сохранен: {dev_backup_file}')

            # Шаг 2: Создание дампа prod базы
            print('2. Создание дампа prod базы...')
            self._create_dump(prod_db, prod_dump_file)
            print(f'   Дамп создан: {prod_dump_file}')

            # Шаг 3: Очистка dev базы
            print('3. Очистка dev базы...')
            self._clean_database(dev_db)
            print('   База очищена')

            # Шаг 4: Восстановление данных из prod в dev
            print('4. Восстановление данных в dev базу...')
            self._restore_dump(dev_db, prod_dump_file)
            print('   Данные восстановлены')

            print(f'\nСинхронизация завершена успешно!')
            print(f'Бэкап dev базы: {dev_backup_file}')
            print(f'Дамп prod базы: {prod_dump_file}')

        except subprocess.CalledProcessError as e:
            print(f'\nОшибка при выполнении команды: {e}')
        except Exception as e:
            print(f'\nНеожиданная ошибка: {e}')

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

    def _clean_database(self, db_config):
        """Полная очистка базы данных"""
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']

        # Удаляем все таблицы, sequences, типы и функции
        clean_sql = """
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            -- Удаляем все таблицы
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;

            -- Удаляем все sequences
            FOR r IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public') LOOP
                EXECUTE 'DROP SEQUENCE IF EXISTS public.' || quote_ident(r.sequence_name) || ' CASCADE';
            END LOOP;

            -- Удаляем все типы (enums)
            FOR r IN (SELECT t.typname FROM pg_type t JOIN pg_namespace n ON t.typnamespace = n.oid WHERE n.nspname = 'public' AND t.typtype = 'e') LOOP
                EXECUTE 'DROP TYPE IF EXISTS public.' || quote_ident(r.typname) || ' CASCADE';
            END LOOP;
        END $$;
        """

        cmd = [
            'psql',
            '-h', db_config['host'],
            '-p', db_config['port'],
            '-U', db_config['user'],
            '-d', db_config['name'],
            '-c', clean_sql,
        ]

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0 and result.stderr:
            stderr_lower = result.stderr.lower()
            if 'fatal:' in stderr_lower:
                raise Exception(f"Ошибка очистки базы:\n{result.stderr}")

    def _restore_dump(self, db_config, dump_file):
        """Восстановление дампа в базу данных"""
        env = os.environ.copy()
        env['PGPASSWORD'] = db_config['password']

        cmd = [
            'pg_restore',
            '-h', db_config['host'],
            '-p', db_config['port'],
            '-U', db_config['user'],
            '-d', db_config['name'],
            '--no-owner',  # Не восстанавливать владельца объектов
            '--no-privileges',  # Не восстанавливать права доступа
            dump_file,
        ]

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        # pg_restore возвращает код 1 даже при некритичных предупреждениях
        # Проверяем только критические ошибки
        if result.returncode != 0 and result.stderr:
            stderr_lower = result.stderr.lower()
            critical_errors = [
                'fatal:',
                'could not connect',
                'authentication failed',
                'password authentication failed',
                'no such file',
                'is not a directory',
            ]

            if any(err in stderr_lower for err in critical_errors):
                raise Exception(f"Критическая ошибка pg_restore:\n{result.stderr}")
