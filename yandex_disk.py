import requests


class YandexDisk:
    """
    Класс для работы с API Яндекс.Диска
    """

    def __init__(self, access_token):
        self.access_token = access_token

    @staticmethod
    def format_path(path):
        """Преобразование '\' в '/' в полученном пути"""
        path = r"{}".format(path)
        path = path.replace("\\", "/")
        return path

    def check_path(self, path):
        """Проверка: существует ли папка по пути 'path'
            Если папка не существует: вернуть False
            Иначе: вернуть путь к существующей папке
        """
        path = self.format_path(path)
        headers = {"Authorization": "OAuth {}".format(self.access_token)}
        params = {"path": path, "fields": "name,path,modified"}
        res = requests.get("https://cloud-api.yandex.net/v1/disk/resources",
                           headers=headers, params=params)
        res = res.json()
        if "error" in res:
            return False
        else:
            return res["path"]

    def add_folder(self, path):
        """Создание каталога по пути 'path'
            Если каталог не создан: вернуть False
            Иначе: вернуть путь к созданному каталогу
        """

        def add(folder_path):
            """Создание папки по пути 'folder_path' """
            headers = {"Authorization": "OAuth {}".format(self.access_token)}
            params = {"path": folder_path}
            response = requests.put("https://cloud-api.yandex.net/v1/disk/resources",
                                    headers=headers, params=params)
            response = response.json()
            if "error" in response:
                return False
            else:
                return response["href"]

        path = self.format_path(path)
        split_path = path.split("/")
        new_path = ""
        res = None
        for item in split_path:
            if new_path == "":
                new_path = item
                continue
            else:
                new_path = "/".join([new_path, item])

            if not self.check_path(new_path):
                res = add(new_path)
        if res is False:
            return False
        else:
            return res

    def upload_file(self, local_path_to_file, cloud_path_to_file, overwrite="false"):
        """Загрузка файла 'local_path_to_file' по пути 'cloud_path_to_file'
            Предварительно создается каталог 'cloud_path' если не существует
            Если 'overwrite' == True, перезаписать имеющийся файл
            Если файл загружен или принят сервером
            (код ответа 201 или 202 соответственно): вернуть True
            Иначе: вернуть False
        """

        def give_upload_url(disk_path, overwrite):
            """Получение ссылки для загрузки файла"""
            headers = {"Authorization": "OAuth {}".format(self.access_token)}
            params = {"path": disk_path, "overwrite": overwrite}
            response = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload",
                                    headers=headers, params=params)
            response = response.json()
            if "error" in response:
                return response
            else:
                return response["href"]

        def upload_file(local_path, upload_url):
            """Загрузка файла на сервер"""
            files = {"file": open(local_path, "rb")}
            response = requests.put(upload_url, files=files)
            return response.status_code

        cloud_path = cloud_path_to_file.split("/")[:-1]
        cloud_path = "/".join(cloud_path)
        self.add_folder(cloud_path)
        response = give_upload_url(cloud_path_to_file, overwrite)

        if isinstance(response, dict) and response['error'] == 'DiskResourceAlreadyExistsError':
            return response

        res = upload_file(local_path_to_file, response)
        if res in [201, 202]:
            return True
        else:
            return False
