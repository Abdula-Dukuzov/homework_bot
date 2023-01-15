import logging
import os
import sys
import time
from http import HTTPStatus
from json.decoder import JSONDecodeError

import requests
import telegram
from dotenv import load_dotenv

import exceptions

logger = logging.getLogger(__name__)
load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


success = 0


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        logger.info('Начало отправки')
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
    except telegram.error.TelegramError as error:
        logger.error(f'Error: {error}')
    else:
        logger.debug(f'Сообщение отправлено {message}')
        global success
        success += 1
        return success


def get_api_answer(current_timestamp):
    """Получить статус домашней работы."""
    timestamp = current_timestamp or int(time.time())
    params_request = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp},
    }
    try:
        logger.info(
            'Начало запроса: url = {url},'
            'headers = {headers},'
            'params = {params}'.format(**params_request))
        homework_statuses = requests.get(**params_request)
        if homework_statuses.status_code != HTTPStatus.OK:
            logging.error('Эндпойнт не доступен')
            raise exceptions.InvalidResponseCode(
                'Не удалось получить ответ API, '
                f'ошибка: {homework_statuses.status_code}'
                f'причина: {homework_statuses.reason}'
                f'текст: {homework_statuses.text}')
    except Exception:
        raise exceptions.ConnectionError(
            'Не верный код ответа параметры запроса: url = {url},'
            'headers = {headers},'
            'params = {params}'.format(**params_request))
    try:
        homework_statuses.json()
    except JSONDecodeError:
        logging.error("Ответ не преобразован в JSON")
        raise JSONDecodeError("Ответ не преобразован в JSON")
    return homework_statuses.json()


def check_response(response):
    """Проверить валидность ответа."""
    logger.debug('Начало проверки')
    if not isinstance(response, dict):
        raise TypeError('Ошибка в типе ответа API')
    if 'homeworks' not in response or 'current_date' not in response:
        raise exceptions.EmptyResponseFromAPI('Пустой ответ от API')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Homeworks не является списком')
    return homeworks


def parse_status(homework):
    """Распарсить ответ."""
    if 'homework_name' not in homework:
        raise KeyError('В ответе отсутсвует ключ homework_name')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус работы - {homework_status}')
    return (
        'Изменился статус проверки работы "{homework_name}" {verdict}'
    ).format(
        homework_name=homework_name,
        verdict=HOMEWORK_VERDICTS[homework_status]
    )


def check_tokens():
    """Проверка доступности переменных окружения."""
    return all([TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствует необходимое кол-во'
                        ' переменных окружения')
        sys.exit('Отсутсвуют переменные окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    current_report = {
        'name': '',
        'output': ''
    }
    prev_report = current_report.copy()
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get(
                'current_data', current_timestamp)
            new_homeworks = check_response(response)
            if new_homeworks:
                homework = new_homeworks[0]
                current_report['name'] = homework.get('homework_name')
                current_report['output'] = homework.get('status')
            else:
                current_report['output'] = 'Нет новых статусов работ.'
            if current_report != prev_report and success > 0:
                message = parse_status(homework)
                send_message(bot, message)
                prev_report = current_report.copy()
                current_timestamp = response.get(
                    'current_date',
                    current_timestamp
                )
            else:
                logger.debug('Статус не поменялся')
        except exceptions.NotForSending as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            current_report['output'] = message
            logger.error(message)
            if current_report != prev_report:
                send_message(bot, message)
                prev_report = current_report.copy
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format=(
            '%(asctime)s, %(levelname)s, Путь - %(pathname)s, '
            'Файл - %(filename)s, Функция - %(funcName)s, '
            'Номер строки - %(lineno)d, %(message)s'
        ),
        handlers=[logging.FileHandler('log.txt', encoding='UTF-8'),
                  logging.StreamHandler(sys.stdout)])
    main()
