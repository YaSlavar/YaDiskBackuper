import json
import os
import os.path
import re
from auth import Server
from yandex_disk import YandexDisk
from logger import log
from multiprocessing import Process


class BackupManager:
    """Класс для резервного копирования локальных файлов на Яндекс.Диск"""

    def __init__(self, project):
        self.project = project
        self.oauth_server = Server()
        # Получение токена и запись в файл настроек
        self.oauth_server.run()
        # Загрузка настроек из файла
        with open("settings.json", "r", encoding="utf-8") as fh:
            data = json.loads(fh.read())
        self.settings = data
        self.access_token = data["YandexDisk"]["access_token"]
        self.YandexDisk = YandexDisk(self.access_token)

    def upload(self, local_path, disk_path):
        log("Копирование файлов!")
        # Проверка: используется ли маска
        if self.settings['projects'][self.project]['options']['template'] is not False:
            log("Копирование по маске {}".format(self.settings['projects'][self.project]['options']['template']))
        # Проверка: существует ли директория в облаке, если нет, создает директорию
        if self.YandexDisk.check_path(disk_path) is False:
            log("Директория {} не найдена! Создание директории".format(disk_path))
            directory_created = self.YandexDisk.add_folder(disk_path)
            if directory_created is not False:
                log("Директория {} успешно создана!".format(disk_path))

        for top, dirs, files in os.walk(local_path):
            for file_name in files:
                path_to_file = "/".join([top, file_name])
                path_to_file = self.YandexDisk.format_path(path_to_file)
                cloud_path_to_file = path_to_file.replace(local_path, disk_path)

                if self.settings['projects'][self.project]['options']['template'] is not False:
                    name_reg = re.findall(self.settings['projects'][self.project]['options']['template'], file_name,
                                          re.MULTILINE)
                    if name_reg:
                        log("Копирование файла {}".format(path_to_file))
                        message = self.YandexDisk.upload_file(path_to_file, cloud_path_to_file)
                        if message is True:
                            log("Файл {} скопирован!".format(path_to_file))
                        else:
                            log(message['message'])
                    else:
                        continue
                else:
                    log("Копирование файла {}".format(path_to_file))
                    message = self.YandexDisk.upload_file(path_to_file, cloud_path_to_file)
                    if message is True:
                        log("Файл {} скопирован!".format(path_to_file))
                    else:
                        log(message['message'])
        log("Копирование завершено!")

    def backup(self):
        """Копирование"""

        try:
            for item in self.settings['projects'][self.project]['folders']:
                if os.path.isdir(item['src']):
                    if self.settings['projects'][self.project]['options']['confirm']:
                        log("Запрос на копирование директории {}!".format(item['src']))
                        confirm = input(
                            "Скопировать файлы директории: {} в дерикторию: {} ?\n(Да/Нет) : ".format(item['src'],
                                                                                                      item['dest']))
                        if confirm.lower() == "да":
                            self.upload(item['src'], item['dest'])
                        else:
                            log("Копирование директории {} отменено!".format(item['src']))
                            continue
                    else:
                        self.upload(item['src'], item['dest'])
                else:
                    log("Директория {} не найдена!".format(item['src']))
                    continue

        except Exception as err:
            log("Произошла ошибка: {}".format(err))
