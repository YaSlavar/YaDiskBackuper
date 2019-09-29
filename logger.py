import datetime


def log(string):
    """
    Вывод даты и сообщения на экран и запись в файл 'log.txt'
    """
    time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    string = time + " " + string
    print(string)
    string = string + "\n"
    with open("log.txt", "a", encoding="utf-8") as fh:
        fh.write(string)
