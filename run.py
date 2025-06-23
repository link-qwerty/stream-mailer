# Import
import os
from handlers.json import JSONHandler
from handlers.args import ArgsHandler
from handlers.tasks import TaskManager
from utils.mailer import make, Mailer

# Defines
DEBUG = True    # Директива препроцессора (аналог)

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
    args.parse(dict())

# Создаем директории (если еще не созданы)
os.makedirs(args.get("templates_dir"), exist_ok = True)
os.makedirs(args.get("tasks_dir"), exist_ok = True)
os.makedirs(args.get("mail_dir"), exist_ok = True)
os.makedirs(os.path.join(args.get("mail_dir"), "out"), exist_ok = True)
os.makedirs(os.path.join(args.get("mail_dir"), "send"), exist_ok = True)
os.makedirs(os.path.join(args.get("mail_dir"), "bad"), exist_ok = True)
os.makedirs(args.get("logs_dir"), exist_ok = True)

# Создаем парсер для файлов заданий
task_json = JSONHandler()
# Создаем объект (синглетон) для обработки заданий
task_manager = TaskManager(args.get("tasks_dir"), args.get("templates_dir"))
# Создаем объект для отправки почты
mailer = Mailer(args.get("address"), args.get("port"), args.get("login"), args.get("password"),
                args.get("cypher"), args.get("ssl"))
# Создаем генератор списка для файлов заданий
tasks = [f for f in os.listdir(args.get("tasks_dir")) if f.endswith('.json')]
# Отрабатываем задания
task_manager.parse(tasks, task_json)
# Создаем генератор списка заданий (отбираем задания по условию
tasks = [x for x in task_manager.get("mailer") if not x is None]
# Проходимся по отобранным заданиям и выполняем их
for task in tasks:
    # Перебираем список получателей
    print(task['to'])
    """
    recipients = task['to'].split(',')
    for recipient in recipients:
        # Читаем поток из текстового файла
        with open(task['template_txt_files'][recipient], "r+t", encoding="utf-8") as file:
            body_text = file.read()
        file.close()
        # Удаляем временный файл
        os.remove(task['template_txt_files'][recipient])

        # Читаем поток из файла html
        with open(task['template_html_files'][recipient], "r+t", encoding="utf-8") as file:
            body_html = file.read()
        file.close()
        # Удаляем временный файл
        os.remove(task['template_html_files'][recipient])

        # Создаем сообщение
        message_file =  make(task['from'], recipient, task['subjects'][recipient], body_text, body_html,
                             args.get("mail_dir") + "out/")
        print(message_file)
        """

"""

message_filename = make("t.bondarenko@prointegra.ru", "link.qwerty@gmail.com",
                       "ИБ-субподрядчик для [Название компании] – без найма и соцпакетов",
                        text_body,
                        html_body,
                        args.get("mail_dir") + "out/")
mailer.send(args.get("mail_dir") + "out/" + message_filename)
"""

