# Проект: Сервис микроблогов
Добро пожаловать в проект "Сервис микроблогов"! 
Это веб-приложение, разработанное с помощью Python и других технологий, 
предназначено для реализации собственного корпоративного сервиса микроблогов. 
Оно предоставляет пользователям платформу для обмена краткими сообщениями, похожими на те, что можно найти в 
Твиттере или других подобных сервисах. В этом файле README вы найдете обзор структуры проекта, 
инструкции по установке и другие полезные сведения.

## Структура проекта
Проект организован в следующие каталоги и файлы:
* **app/:** Содержит основную логику приложения, включая маршрутизаторы и схемы.
* **conf.d/:** содержит файлы конфигурации для web сервера nginx;
* **config_app/:** содержит основную конфигурацию и настройки для приложения;
* **db/:** содержит код, связанный с базой данных, включая подключение к базе данных и модели;
* **env.template:** шаблон переменных окружения, которые используются в приложении
* **docker-compose.yml:** файл конфигурации Docker Compose;
* **Dockerfile:** файл конфигурации Docker, для создания образа приложения;
* **main.py:** точка входа в приложение;
* **pytest.ini:** файл конфигурации для фреймворка pytest;
* **requirements.txt:** список необходимых пакетов Python;
* **static/:** каталог для хранения статических файлов, таких как изображения, CSS и JavaScript;
* **tests/:** каталог для хранения тестов и другого кода, связанного с тестированием.


## Установка
1. Склонируйте репозиторий: git clone https:
```shell
git clone https://gitlab.skillbox.ru/baikov_petr/python_advanced_diploma.git
```
2. Перейдите в каталог проекта:
```shell
cd python_advanced_diploma
```
3. Создайте виртуальное окружение:
```shell
python3 -m venv venv
```
4. Активируйте виртуальное окружение:
```shell
source venv/bin/activate
```
5. Создайте файл .env с переменными окружения (на примере шаблона .env.template)
6. Разверните приложение (см. раздел "Развертывание")


## Использование
Чтобы использовать приложение, просто перейдите по адресу http://localhost:8000 в вашем веб-браузере. 


## Тестирование
В проекте включен ряд модульных тестов, которые можно запустить с помощью фреймворка pytest. 
Чтобы запустить тесты, просто перейдите в каталог проекта и выполните команду pytest в терминале.
```shell
pytest tests/
```

### Развертывание
Проект можно развернуть на платформе контейнеризации, такой как Docker. 
В проекте включены файлы Dockerfile и docker-compose.yml, которые помогут в контейнеризации и развертывании. 
Выполните в корне проекта команду:
```shell
docker compose up --build
```