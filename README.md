# CI/CD для проекта API YAMDB. ![example workflow](https://github.com/redbull7214/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

Примеры запросов:
http://51.250.88.241/redoc/

## _Запуск проекта:_
Клонировать репозиторий и перейти в него в командной строке:
```sh
git clone https://github.com/redbull7214/yamdb_final.git
cd api_yamdb/
```
Cоздать и активировать виртуальное окружение:
```sh
python3 -m venv env source env/bin/activate python3 -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```sh
pip install -r requirements.txt
```
Запустить приложение из директории infra/
```sh
docker-compose up -d --build
```
Выполнить миграции из директории infra/
```sh
docker-compose exec web python manage.py migrate
```
Собрать статику из директории infra/
```sh
docker-compose exec web python manage.py collectstatic --no-input
```
