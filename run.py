# Import
import os
from handlers.json import JSONHandler
from handlers.args import ArgsHandler
from services.mailer import make, MailSender


# Defines
DEBUG = True    # Директива препроцессора

# Code

# Получаем аргументы командной строки
if DEBUG:
    args = ArgsHandler("mailer", "Mailer Queue(cl)LQ@2025 Free to use", JSONHandler("db/args.json").get())
else:
    args = ArgsHandler("mailer", "Mailer Queue(cl)LQ@2025 Free to use", JSONHandler("db/args.json").get())

# Создаем директории
os.makedirs(args.get("templates_dir"), exist_ok = True)
os.makedirs(args.get("tasks_dir"), exist_ok = True)
os.makedirs(args.get("mail_dir"), exist_ok = True)
os.makedirs(os.path.join(args.get("mail_dir"), "out"), exist_ok = True)
os.makedirs(os.path.join(args.get("mail_dir"), "send"), exist_ok = True)
os.makedirs(os.path.join(args.get("mail_dir"), "bad"), exist_ok = True)
os.makedirs(args.get("logs_dir"), exist_ok = True)

# Создаем объект для отправки почты
mailer = MailSender(args.get("address"), args.get("port"), args.get("login"), args.get("password"),
                    args.get("cypher"), args.get("ssl"))
# Создаем сообщение
with open(args.get("templates_dir") + "message-zero.html", "r", encoding='utf-8') as file:
    html_body = file.read()
file.close()

with open(args.get("templates_dir") + "message-zero.txt", "r", encoding='utf-8') as file:
    text_body = file.read()
file.close()

filename = make("t.bondarenko@prointegra.ru", "link.qwerty@gmail.com",
                       "ИБ-субподрядчик для [Название компании] – без найма и соцпакетов",
                       text_body,
                       html_body,
                       args.get("mail_dir") + "out/")
mailer.send(args.get("mail_dir") + "out/" + filename)

