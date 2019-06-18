import requests
import time
import os
import telegram

def send_message(message):
    bot = telegram.Bot(token=os.getenv('TELEGRAM_TOKEN'))
    bot.send_message(chat_id=639083663, text=message)

def get_dvmn_info():
    

    while True:
        try:
            timestamp = None
            headers = {
              'Authorization': os.getenv('DVMN_TOKEN'),
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
            print('время ожидания истекло...перезапускаемся')

            continue
        except requests.exceptions.ConnectionError:
            print('Сервер  недоступен...ожидаем')
            time.sleep(15)
            continue
        except KeyError:
            continue
        except requests.exceptions.HTTPError:
            print(response.text)
            break



if __name__ == "__main__":
    get_dvmn_info()
