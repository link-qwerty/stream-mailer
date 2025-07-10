# Import
import datetime
import os
from handlers.json import JSONHandler
from handlers.args import ArgsHandler
from handlers.tasks import TaskManager
from services.mailer import make, Mailer
import logging

# Defines
DEBUG = False    # Директива препроцессора (аналог)

# Code
# Получаем аргументы командной строки
args = ArgsHandler("mailer", "Mailer Queue(cl)LQ@2025 Free to use")
if DEBUG:
    # Считываем набор аргументов из JSON
    args_json = JSONHandler("/logs")
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
os.makedirs(args.get("templates_dir") + "files/images/", exist_ok = True)
os.makedirs(args.get("tasks_dir") + "complete/", exist_ok = True)
os.makedirs(args.get("tasks_dir") + "suspend/", exist_ok = True)
os.makedirs(args.get("mail_dir") + "out/", exist_ok = True)
os.makedirs(args.get("mail_dir") + "send", exist_ok = True)
os.makedirs(args.get("mail_dir") + "bad/", exist_ok = True)
os.makedirs(args.get("logs_dir"), exist_ok = True)

# Настраиваем логгер
logging.basicConfig(level=logging.INFO, filename=args.get("logs_dir") + 'mail.log', filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")
# Создаем объект для обработки заданий
task_manager = TaskManager(args.get("tasks_dir"), args.get("templates_dir"), JSONHandler(args.get("logs_dir")))
# Создаем объект для отправки почты
mailer = Mailer(args.get("address"), args.get("port"), args.get("login"), args.get("password"), args.get("logs_dir"),
                args.get("cypher"), args.get("ssl"))

# Создаем генератор списка для файлов отложенных заданий
suspend_task_files = [f for f in os.listdir(args.get("tasks_dir") + 'suspend/')
                      if f.endswith('.json') and f[0:8] == datetime.datetime.now().strftime('%d%m%Y')]
# Переносим файлы отложенных заданий в рабочий каталог
for suspend_file in suspend_task_files:
    os.rename(args.get("tasks_dir") + f'suspend/{suspend_file}', args.get("tasks_dir") + suspend_file)
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
                                 args.get('templates_dir') + "files/", args.get("mail_dir") + "out/",
                                 task['images'] if 'images' in task else None,
                                 task['attachments'] if 'attachment' in task else None)
        # Отправляем
        result = mailer.send(args.get("mail_dir") + "out/" + message_filename)
        if result:
            # Переносим файл почтового сообщения в отправленные
            os.rename(args.get("mail_dir") + "out/" + message_filename,
                      args.get("mail_dir") + "send/" + message_filename)
            # Вносим запись в логгер об успешной отправке письма
            logging.info(f'Message was sent from {task['from']} '
                         f'to {content['replaces']['Название компании']}<{rcpt}>, '
                         f'project {content['replaces']['Проект']}, message file {message_filename}')
        else:
            # Переносим файл почтового сообщения в ошибки
            os.rename(args.get("mail_dir") + "out/" + message_filename,
                      args.get("mail_dir") + "bad/" + message_filename)
            # Вносим запись в логгер об ошибке
            logging.error(f'Message from {task['from']} '
                          f'to {content['replaces']['Название компании']}<{rcpt}> was not sent, '
                          f'project {content['replaces']['Проект']}, message file {message_filename}')
    # Переносим задание в отработанные
    os.rename(args.get("tasks_dir") + task_file, args.get("tasks_dir") + "complete/" + task_file)