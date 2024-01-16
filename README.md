## Бот-ассистент для проверки статуса домашней работы


### Описание проекта:

Данный бот предназначен для информирования о статусе проверки домашней работы. Он опрашивает API сервиса Практикум.Домашка и, проанализировав ответ, присылает соответствующее уведомление в Telegram. 

---

### Используемые технологии и библиотеки:
* [Python](https://www.python.org/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)
* [python-telegram-bot](https://pypi.org/project/python-telegram-bot/)
* [requests](https://pypi.org/project/requests/)

---

### Как запустить проект:

- Клонируйте репозиторий на локальную машину

```
git clone git@github.com:Abdula-Dukuzov/homework_bot.git
```

- Перейдите в папку с проектом

```
cd homework_bot
```

- Создайте и активируйте виртуальное окружение

```
python -m venv venv
source venv/Scripts/activate
```

- Обновите pip и установите зависимости из requirements.txt

```
pip install --upgrade pip
pip install -r requirements.txt
```

- В корневой папке проекта создайте файл .env. Пример содержания файла:

```
PRACTICUM_TOKEN=" "
TELEGRAM_TOKEN=" "
TELEGRAM_CHAT_ID=" "

```


- Активируйте бота:

```
python homework.py
```

---

### Авторы проекта:

    Абдула Дукузов
