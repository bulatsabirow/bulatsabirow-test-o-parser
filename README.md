# bulatsabirow-test-o-parser
## Требования
1. [Python >= 3.11](https://www.python.org/downloads/)
2. [Poetry](https://pypi.org/project/poetry/)

Также необходимо задать значение переменной окружения `TELEGRAM_BOT_TOKEN`.  
После запуска телеграм бота командой №9 необходимо начать с ним диалог командой `/start`.  
В ответ он отправит id чата, который нужно будет подставить в поле `Telegram id` при создании
пользователя (команда №10).

## Инструкция по запуску
1. Вход в виртуальное окружение:
    `
    poetry shell 
    `
2. Установка зависимостей:
    `
    poetry install
    `
3. Поднятие MySQL и Redis с помощью Docker:
    `
    docker compose -f 'docker-compose.dev.yml' up -d
    `
4. Выполнение миграций:
    `
    python src/manage.py migrate
    `
5. Инициализация линтера:
    `
    pre-commit install
    `
6. Запуск Celery:
    `
    cd src && celery -A test_o_parser worker --loglevel=info
    `
7. Сбор статических файлов:
    `
    python src/manage.py collectstatic --noinput
    `    
8. Запуск сервера для разработки на http://localhost:8000:
    `
    python src/manage.py runserver
    `
9. Запуск Telegram бота:
    `
    python src/manage.py start_bot
    `
10. Создание пользователя:
    `
    python src/manage.py createsuperuser
    `