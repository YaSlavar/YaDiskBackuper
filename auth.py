import webbrowser
from http.server import HTTPServer, CGIHTTPRequestHandler
import http.client
import urllib.parse
import os
import json
import random
import datetime


class RequestError(Exception):
    """Класс исключение"""
    pass


class Server:
    """Класс для автоизации OAuth YandexDisk"""

    def __init__(self):
        self.access_token = None
        self.expires_in = None
        self.date_of_receipt = None
        self.client_id = None
        self.client_secret = None
        self.httpd = None
        self.open_settings()

    def open_settings(self, key=None):
        """Загрузка настроек из файла settings.json
            Если 'key' == None, то инициальзация класса Server
            Если 'key' == "All", то вернуть содержимое файла
            Если 'key' иное, то вернуть знвчение по ключу из файла
        """
        with open(os.path.join(os.getcwd(), "settings.json"),
                  encoding="utf-8") as fh:
            data = json.loads(fh.read())
        if key is None:
            self.access_token = data["YandexDisk"]["access_token"]
            self.client_id = data["YandexDisk"]["client_id"]
            self.client_secret = data["YandexDisk"]["client_secret"]
            self.expires_in = datetime.timedelta(seconds=data["YandexDisk"]["expires_in"])
            self.date_of_receipt = datetime.datetime.strptime(data["YandexDisk"]["date_of_receipt"], "%d/%m/%Y %H:%M")
        elif key == "All":
            return data
        else:
            return data["YandexDisk"][key]

    def save_settings(self, key="test", value=None):
        """Сохранение настроек в файл settings.json
            ["YandexDisk"][key] - ключ параметра
            'value' - значение параметра
        """
        data = self.open_settings("All")
        data["YandexDisk"][key] = value
        with open(os.path.join(os.getcwd(), "settings.json"),
                  "w", encoding="utf-8") as fh:
            fh.write(json.dumps(data, ensure_ascii=False, indent=4))

    def get_token(self):
        """Получение токена в обмен на code"""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {"grant_type": "authorization_code",
                  "code": self.open_settings("access_token"),
                  "client_id": self.client_id,
                  "client_secret": self.client_secret,
                  "device_id": str(random.randint(1000000, 10000000)),
                  "device_name": str(random.randint(1000000, 10000000))}
        params = urllib.parse.urlencode(params)
        connection = http.client.HTTPSConnection('oauth.yandex.ru')
        connection.request('POST', '/token', params, headers)
        response = connection.getresponse()
        result = response.read()
        connection.close()
        result = result.decode("utf-8")

        data = json.loads(result)
        if "error" in data:
            raise RequestError(data)
            print(err)
        self.save_settings(key="access_token", value=data["access_token"])
        self.save_settings(key="expires_in", value=data["expires_in"])
        self.save_settings(key="date_of_receipt", value=datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))

    def run(self):
        """Открытие окна браузера со ссылкой авторизации
            Запуск/закрытие веб-сервера
        """

        td = self.date_of_receipt + self.expires_in - datetime.timedelta(days=5)
        if td <= datetime.datetime.now() or self.access_token == "":
            webbrowser.open_new("https://oauth.yandex.ru/authorize?"
                                "response_type=code&client_id={}".format(self.client_id))
            server_address = ('localhost', 8000)
            self.httpd = HTTPServer(server_address, CGIHTTPRequestHandler)
            try:
                self.httpd.handle_request()
            except KeyboardInterrupt:
                pass
            self.httpd.server_close()
            self.get_token()
        else:
            return False
