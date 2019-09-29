import cgi
import json
import os
"""CGI-скрипт получающий 'code' из URL"""
form = cgi.FieldStorage()
code = form.getvalue('code')

with open(os.path.join(os.getcwd(), "settings.json"),
          encoding="utf-8") as fh:
    data = json.loads(fh.read())

data["YandexDisk"]["access_token"] = int(code)

with open(os.path.join(os.getcwd(), "settings.json"),
          "w", encoding="utf-8") as fh:
    fh.write(json.dumps(data, ensure_ascii=False, indent=4))

print("Content-type:text/html\r\n\r\n")
print('<meta charset="utf-8">')
print("<h1>Эту вкладку можно закрыть</h1>")
