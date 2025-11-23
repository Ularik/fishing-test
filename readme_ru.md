# Стартовый проект Django

Ознакомьтесь с [документом "О проекте"](about_ru.md).

# Установка

## back

### запуск
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd app
python manage.py runserver
```
доп. команды вирт. окружения
```
source venv/bin/activate
deactivate
```
Для livereload запустить дополнительно
```
python manage.py livereload
```

### Скрипт деплоя

Для автодеплоя можно запускать сприпт **deploy.sh**

Дать доступ для запуска
```
chmod ugo+x deploy.sh
```


### Пример баш скрипта запуска скрипта деплоя.
Данный скрипт можно расположить в домашней дирректории пользователя, для быстрого запуска деплоя.

Узнать путь к папке можно командой
>pwd

Пройти в доманю дирректорию
>cd ~

Для создания файла
>touch {file_name}

#### Создание скрипта деплоя

Файл скрипта запуска деплоя лучше называть по имени проекта или пользователя.
Что бы не ошибиться когда много проектов и не задеплоить не то, то есть все файлы запуска должны иметь разные имена.
Универсальные названия **prod** или **dev**

Создать файл скрипта деплоя
>touch prod

Дать права
> chmod ugo+x prod

Скрипт запуска скрипта деплоя из домашней дирректории
```
#!/bin/bash
cd  {путь_к_папке_проекта}
chmod ugo+x deploy.sh
./deploy.sh
```

Запуск
>./prod

Таким образом будет запущен деплой, но при этом Вы остаетесь в домашней дирректории.

### Пример скрипта перехода в окружение

Важно! Не забудьте предварительно создать папку окружения и установить зависимости!
Из папки проекта выполнить:
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**venv** (или другое имя папки окружения)\
Данный скрипт лучше расположить в домашней дирректории пользователя для быстрого перехода в окружение python проекта.
Как вариант называние можно установить **go**
> touch go

Дать права
> chmod ugo+x go

Скрипт перехода
```
#!/bin/bash
. {путь_к_папке_проекта}/venv/bin/activate
cd {путь_к_папке_проекта}/
```
Запуск перехода из домашней дирректории
>. go


### Пример копирования базы на чистую бд
```
#!/bin/bash
echo 'exp bd_prod'
PGPASSWORD=111111 pg_dump -U user_bd my_bd -f the_backup.sql

echo 'imp bd_dev'
PGPASSWORD=22222 psql -U user_dev -d bd_dev -f  the_backup.sql

```

### Ипользование скрипта деплоя

Перед использованием нужно поставить git на сервере.
После нужно в корень проекта склонировать репозиторий.

Ниже пример копирования из gitlab с помощью личного токена доступа.

Для клонирования используйте следующий шаблон.
1. **group** - группа репозиториев видно в части урл если кликнуть на репозиторий
gitlab.com/{group}/my_app
2. **token** - Токен личного доступа\
Можно получить тут (Настройки -> токены доступа)
https://gitlab.com/-/user_settings/personal_access_tokens
Создайте и сохраните, если его нет.
3. **app_name** - имя репозитория

>git clone https://{group}:{token}@gitlab.com/{group}/{app_name}.git .

точка в конце означает что гит будет клонирован в туже папку где сейчас находитесь,
при этом папка должна быть пустой.


***ВАЖНО!!!***
Нужно сделать **checkout** ну нужную ветку. В будущем скрипт будет работать с ней.

Информация о ветках
>git branch -a

Имя текущей ветки
>git rev-parse --abbrev-ref HEAD

скачать все ветки
>git fetch --all

Переключиться на ветку
>git checkout {branchname}

При запуске скрипта.
1. Скрипт подготавливает локальный git убираяя все лишнее, дальшее скачивает ветку.
2. После предлагается установить зависимости requirements.txt.
3. Предлагается установить migrate.
4. Запускаются автотесты.
5. Нужно просмотреть в консоли лог работы скрипта.\
6. Если все хорошо просто перезапустите докер композ и ли пересоберите.


## Основные моменты

1. Все файлы из папок app, meida, logs прокинуты в докер.
```
    volumes:
      - ./app:/usr/www/app/
      - ./media:/usr/www/media/
      - ./logs:/usr/www/logs/
```
Это означает, что, например заменив файл *.py в приложении app,
изменение попадает сразу в докер без перезапуска.
И наоборот видим логи из докера и файлы media.

2. Порты выставляемые наружу настраиваются в env.
3. Есть режимы запуска Django через переменную DEV.
4. Докер поддерживает Django(app), Celery (worker, beats), Redis, Postgres, Flower, PGAdmin.\
Ненужное просто закоментировать.

Для запуска докера нужен файл **.env**
```
DEV=true
APP_PORT=8001
FLOWER_USERNAME=user
FLOWER_PASSWORD=1
FLOWER_PORT=9090

# DEV DB
POSTGRES_DB: mydb
POSTGRES_USER: root
POSTGRES_PASSWORD: root
POSTGRES_PORT: 5432
PGADMIN_EMAIL: admin@example.com
PGADMIN_PASSWORD: admin
PGADMIN_PORT: 5050
```

**DEV** имеет значения *true*, *false*, *local*
Это настройка режимов запуска проекта: *true* - uvicorn с режимом горячей перезагрузки при изменении файлов.
Это означает что при изменении файлов py, html сервер сам перезагружается. Это удобно при разработке.
*local* - запуск в режиме runserver, удобно когда используется локальный докер без nginx.
*false* - боевой запуск в проде.

APP_PORT - порт приложения по которому оно будет доступно.

FLOWER_* - настройка веб интерфейса flower

Раздел DEV DB для запуска базы в докере с вебинтерфейсом pgadmin.




Пример конфигурации nginx
нужно установить порт из .env и путь к сайту

```
location /static {
    alias $root_path/app/static;
	}
location /media {
	alias $root_path/media;
	}
	
location / {
	proxy_pass http://127.0.0.1:{порт app из env};
	proxy_http_version 1.1;
	proxy_set_header Upgrade $http_upgrade;
	proxy_set_header Connection "upgrade";
	proxy_redirect off;
	proxy_set_header Host $host;
	proxy_set_header X-Real-IP $remote_addr;
	proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	proxy_set_header X-Forwarded-Host $server_name;
	location ~* ^.+\.(jpg|jpeg|gif|png|svg|js|css|mp3|ogg|mpe?g|avi|zip|gz|bz2?|rar|swf|webp|woff|woff2)$ {
		expires 24h;
	    }
	}
```

В папке project
settings_local.py

в нем константы для запуска проекта, пример в settings_local.py.txt


## front

В папке **/front**
стартовый проект на vue.js на базе primevue
https://primevue.org/


В папке **/front-template**
Стартовый шаблон на базе Metronic 8
https://preview.keenthemes.com/metronic8/demo1/index.html?mode=light

он же в шаблоне Django


```
Данные папки для фронта являются дополнительными но не обязательными.
```

# Дополнительно

## Частые команды Django

```
django-admin startproject project .
python manage.py startapp company
python manage.py createsuperuser

python manage.py makemigrations
python manage.py migrate

python manage.py runserver
python manage.py collectstatic

python manage.py inspectdb


python manage.py test --keepdb
python manage.py test company.tests.test_dis --keepdb
```

## Смена версии Python
Обновление Python
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12-full
```

Доп модули
```
sudo apt install python3.12-{tk,dev,dbg,venv,gdbm,distutils}
```

Полная установка
```
sudo apt install python3.12-full
```
После обновления Python сопоставить Python с новым Python3
```
ls /usr/bin/python*

rm /usr/bin/python
ln -s /usr/bin/python3.12 /usr/bin/python

sudo rm /usr/bin/pip
sudo ln -s /usr/bin/pip3.12 /usr/bin/pip
```

## Docker
Основные команды
```
docker ps
docker exec -it my_app_1 bash

docker-compose restart
docker-compose up --build
docker-compose build --no-cache
docker-compose up -d
docker-compose down
docker-compose ps
docker ps --filter "name=app" --format "table {{.ID}}\t{{.Names}}\t{{.Ports}}"
```
Чистка ненужных файлов докера

>docker system prune -f

-f не задавать вопрос Y. Таким образом можно запускать периодически в crone

Права на запуск докера (выполнять из под рута). После смена прав перезайти.
```
sudo usermod -aG docker {new_user}

sudo chmod +666 /var/run/docker.sock

ls -l /var/run/docker.sock
```
Зеркало для докера
```
nano /etc/docker/daemon.json

{ "registry-mirrors" : [ "https:\/\/mirror.gcr.io" ] }

sudo service docker restart
```

## Запуск без докера

Запуск как служба
```
sudo nano /etc/systemd/system/uvicorn.service
```
```
[Unit]
Description=Uvicorn API
After=network.target

[Service]
User=vds
Group=vds
WorkingDirectory=/var/www/api-express/app
ExecStart=/var/www/api-express/venv/bin/uvicorn project.asgi:application --host 127.0.0.1 --port 8001 --reload --reload-include *.html
Restart=always
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```
systemctl daemon-reload

sudo systemctl status api-express.service

sudo journalctl -u api-express.service -f


```
Дать права на запуск службы
```
sudo visudo

user_web ALL=(ALL) NOPASSWD: /bin/systemctl start unicorn_my_app.service
user_web ALL=(ALL) NOPASSWD: /bin/systemctl stop unicorn_my_app.service
user_web ALL=(ALL) NOPASSWD: /bin/systemctl restart unicorn_my_app.service
```

Запуск через sudo, но пароль просить не будет


```
tail -f uvicorn.log

```

## Redis
Очистка задач
`docker exec -i cpexpcardru-redis-1 redis-cli FLUSHALL`

## Postgresql
Подключение плагинов
под рутом
>sudo -u postgres psql -d tanos_test

>CREATE EXTENSION IF NOT EXISTS pg_trgm;

## Используемы плагины
1. Изветсные библиотеки: djangorestframework, django-cors-headers, psycopg2-binary, django-filter, requests
Их описание можно найти в интернете, тут нет, т.к. они известны.

Ниже не очень известные библиотеки.

2. **livereload** - плагин автоматической перезагрузки страницы при изменении кода.
https://pypi.org/project/django-livereload-server/
Удобно для верстки. Но замедляет работу.\
ВНИМАНИЕ! на проде выключать **livereload.middleware.LiveReloadScript**

3. **db_logger** - пишет логи в базу данных, и выводит в админке.
https://pypi.org/project/db-logger/
Подключен к проекту в виде приложения (папки) напрямую.
Настраивается в settings в разделе LOGGING
'db_log'
Доп. библиотека **six** нужна для db_logger
Удобно писать мониторинг подцепившись к БД, плюс удобно следить персоналу за ошибками и логами.

4. **djangorestframework-simplejwt** - библиотека для работы с JWT токенами через DRF.

5. **django-ninja** - быстрая библиотека для API - аналог DRF но быстрее и поддерживает асинхронность.

6. **django-ninja-jwt** - реализация JWT для ninja
https://pypi.org/project/django-ninja-jwt/