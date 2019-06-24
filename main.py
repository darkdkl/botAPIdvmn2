import requests
import time
import os
import telegram
import logging


class TelegramBotLogsHandler(logging.Handler):

    def emit(self, record):
        send_message(self.format(record),os.environ['TELEGRAM_LOGBOT_TOKEN'])
        




def send_message(message,token=os.environ['TELEGRAM_TOKEN']):
    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=639083663, text=message)

def get_dvmn_info():
    
    logger = logging.getLogger("Logs To Telegram")
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramBotLogsHandler())

    logger.info("Бот запущен")
    
  

    while True:
        try:
            
            timestamp = None
            headers = {
              'Authorization': os.environ['DVMN_TOKEN'],
              'timestamp': timestamp
                    }
            response = requests.get(
                'https://dvmn.org/api/long_polling/', headers=headers)
            if not response.ok:
                raise requests.exceptions.HTTPError()

            response_json = response.json()

            if 'timestamp_to_request' in response_json:
                timestamp = response_json['timestamp_to_request']

            negative = response_json['new_attempts'][0]['is_negative']

            lesson_title = response_json['new_attempts'][0]['lesson_title']
            lesson_url = response_json['new_attempts'][0]['lesson_url']

            if negative:
                send_message(f'''У Вас проверили работу "{lesson_title}"
                         К сожалению в ней найдены ошибки."https://dvmn.org{lesson_url}" ''')

            if not negative:
                send_message(f'''У Вас проверили работу "{lesson_title}"
                         Преподаватель одобрил Вашу работу,можете приступать к следующему уроку ''')
            

        except requests.exceptions.ReadTimeout:
            logger.info('Время ожидания от dvmn.org истекло...перезапускаемся')

            continue
        except requests.exceptions.ConnectionError:
            logger.error('Сервер  dvmn.org недоступен...ожидаем')
            time.sleep(15)
            continue
        except KeyError:
            logger.error('Зафиксированны ошибки',exc_info=1)
            continue
        except requests.exceptions.HTTPError:
            logger.error("Бот упал с ошибкой : "+response.text)
            break
        except:
            logger.critical('Бот упал с ошибкой',exc_info=1)
            time.sleep(30)


if __name__ == "__main__":
    get_dvmn_info()
