# Import
import os
from handlers.json import JSONHandler
from handlers.args import ArgsHandler
from services.sendmail import MessageBodyContainer
from services.sendmail import MailSender


# Code

# Получаем аргументы командной строки
args = ArgsHandler("mailer", "Mailer Queue(cl)LQ@2025 Free to use", JSONHandler("db/args.json").get())
# Создаем директории
os.makedirs(args.get("templates_dir"), exist_ok = True)
os.makedirs(args.get("tasks_dir"), exist_ok = True)
os.makedirs(args.get("mail_dir"), exist_ok = True)
os.makedirs(os.path.join(args.get("mail_dir"), "out"), exist_ok = True)
os.makedirs(os.path.join(args.get("mail_dir"), "send"), exist_ok = True)
os.makedirs(os.path.join(args.get("mail_dir"), "bad"), exist_ok = True)
os.makedirs(args.get("logs_dir"), exist_ok = True)

