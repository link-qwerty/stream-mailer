# Import
import os
from handlers.json import JSONHandler
from handlers.args import ArgsHandler
from handlers.tasks import TaskManager
from services.mailer import make, Mailer

# Defines
DEBUG = False    # Директива препроцессора (аналог)

# Code
# Получаем аргументы командной строки
args = ArgsHandler("mailer", "Mailer Queue(cl)LQ@2025 Free to use")
if DEBUG:
    # Считываем набор аргументов из JSON
    args_json = JSONHandler()
    args_json.parse("db/args.json")
    # Загружаем набор аргументов в парсер
    args.parse(args_json.get())
else:
    # Загружаем словарь подготовленных аргументов в парсер
    args.parse({
  "address": { "flag": "-a", "help": "SMTP server address", "default": "smtp.mail.ru"},
  "port": {"flag": "-p", "help": "SMTP server port", "default": 465, "type": "int"},
  "cypher": {"flag": "-c", "help": "SMTP server use STARTTLS", "default": False, "action": "store_false"},
  "ssl": {"flag": "-s", "help": "SMTP server use SSL", "default": True, "action": "store_true"},
  "login": {"flag": "-L", "help": "SMTP server login", "default": "user@mail.com"},
  "password": {"flag": "-P", "help": "SMTP server password", "default": "password"},
  "templates-dir": {"flag": "-t", "help": "templates directory", "default": "templates/"},
  "tasks-dir": {"flag": "-w", "help": "tasks directory", "default": "tasks/"},
  "mail-dir": {"flag": "-m", "help": "mail directory", "default": "mail/"},
  "logs-dir": {"flag": "-l", "help": "logs directory", "default": "logs/"}
})

# Создаем директории (если еще не созданы)
os.makedirs(args.get("templates_dir"), exist_ok = True)
os.makedirs(args.get("tasks_dir"), exist_ok = True)
os.makedirs(args.get("tasks_dir") + "complete/", exist_ok = True)
os.makedirs(args.get("mail_dir"), exist_ok = True)
os.makedirs(args.get("mail_dir") + "out/", exist_ok = True)
os.makedirs(args.get("mail_dir") + "send", exist_ok = True)
os.makedirs(args.get("mail_dir") + "bad/", exist_ok = True)
os.makedirs(args.get("logs_dir"), exist_ok = True)

# Создаем объект для обработки заданий
task_manager = TaskManager(args.get("tasks_dir"), args.get("templates_dir"), JSONHandler())
# Создаем объект для отправки почты
mailer = Mailer(args.get("address"), args.get("port"), args.get("login"), args.get("password"),
                args.get("cypher"), args.get("ssl"))
# Создаем генератор списка для файлов заданий
tasks_files = [f for f in os.listdir(args.get("tasks_dir")) if f.endswith('.json')]
# Отрабатываем задания
task_manager.parse(tasks_files)
# Выполняем задания
for i in range(0, task_manager.count()):
    # Выбираем для исполнения только задания на почтовую рассылку
    task_file, task = task_manager.get("mailer")
    # Проходимся по отправителям
    for rcpt, content in task['to'].items():
        # Создаем сообщение
        message_filename =  make(task['from'], rcpt, content['subject'], content['txt_body'], content['html_body'],
                         args.get("mail_dir") + "out/")
        # Отправляем
        mailer.send(args.get("mail_dir") + "out/" + message_filename)
        # Переносим файл почтового сообщения в отправленные
        os.rename(args.get("mail_dir") + "out/" + message_filename, args.get("mail_dir") + "send/" + message_filename)
    # Переносим задание в отработанные
    os.rename(args.get("tasks_dir") + task_file, args.get("tasks_dir") + "complete/" + task_file)