## Оглавление

- [Оглавление](#оглавление)
- [Автор](#авторы)
- [Описание](#описание)
- [Технологии](#технологии)
- [Установка и запуск проекта](#установка-и-запуск-проекта)

### Автор

[Максим Савилов](https://github.com/msavilov/)

### Описание

Итоговый проект соцсеть продуктовый помошник. Это полностью рабочий проект, который состоит из бэкенд-приложения на Django и фронтенд-приложения на React.

### Для проверки админки:
сайт http://m-savilov.sytes.net/  и  http://158.160.76.121/
логин - admin
пароль - 1234qwer

### Технологии

![](https://img.shields.io/badge/-Python--3.11-blue)
![](https://img.shields.io/badge/-Django--3.2.16-blue)
![](https://img.shields.io/badge/-Django--Rest--Framework--3.12.4-blue)
![](https://img.shields.io/badge/React-blue)
![](https://img.shields.io/badge/docker-blue)
![](https://img.shields.io/badge/-docker--compose-blue)
![](https://img.shields.io/badge/-CI--CD-blue)


## Установка и запуск проекта

1) Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone https://github.com/msavilov/foodgram-project-react.git
cd foodgram
```

2) Создайте файл .env в папке infra и заполните его своими данными. Перечень данных указан в корневой директории проекта в файле env.example.

4) Создание Docker-образов

```
cd frontend
docker build -t username/foodgram_frontend .
cd ../backend
docker build -t username/foodgram_backend .

Замените username в коде на ваш логин на DockerHub

4) Загрузите образы на DockerHub:

```
docker push username/foodgram_frontend
docker push username/foodgram_backend
```

5) Деплой на сервере
Подключитесь к удаленному серверу и создайте на сервере директорию foodgram через терминал

```
ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера
mkdir foodgram
```

6) Установка docker compose на сервер:

```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

7) В директорию foodgram/ скопируйте файлы docker-compose.production.yml и .env:

```
scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
```

- ath_to_SSH — путь к файлу с SSH-ключом;
- SSH_name   — имя файла с SSH-ключом (без расширения);
- username   — ваше имя пользователя на сервере;
- server_ip  — IP вашего сервера.

8) Запустите docker compose в режиме демона:

```
sudo docker compose -f docker-compose.production.yml up -d
```

9) Выполните миграции, загрузите данные для ингридиентов и тегов, соберите статические файлы бэкенда и сделаем суперпользователя:

```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py add_tags
sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_data
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser

```

10) На сервере в редакторе nano откройте конфиг Nginx:

```sudo nano /etc/nginx/sites-enabled/default
```

Измените настройки location в секции server:

```
location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8000;
}
```

Проверьте работоспособность конфига Nginx:

```
sudo nginx -t
```

Если ответ в терминале такой, значит, ошибок нет:

```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

Перезапускаем Nginx

```
sudo service nginx reload
```

11) Настройка CI/CD

Файл workflow уже написан. Он находится в директории

kittygram/.github/workflows/main.yml

Для адаптации его на своем сервере добавьте секреты в GitHub Actions:

- DOCKER_USERNAME - имя пользователя в DockerHub
- DOCKER_PASSWORD - пароль пользователя в DockerHub
- HOST            - ip_address сервера
- USER            - имя пользователя
- SSH_KEY         - приватный ssh-ключ (cat ~/.ssh/id_rsa)
- SSH_PASSPHRASE  - кодовая фраза (пароль) для ssh-ключа
- TELEGRAM_TO     - id телеграм-аккаунта (можно узнать у @userinfobot, команда /start)
- TELEGRAM_TOKEN  - токен бота (получить токен можно у @BotFather, /token, имя бота)

