# Imports
import uuid
import smtplib
from email.message import EmailMessage
from email.policy import default
from email.parser import BytesParser
from email.utils import make_msgid
import mimetypes

# Defines
def make(from_sender:str, to_rcpt:str, subject:str, plain: str, html: str,
         files_directory: str, mail_directory: str, images: dict = None, attachments: dict = None):
    """
    Создание сообщения

    Формирует файл сообщения, записывает его в каталог для отправки и возвращает имя сформированного файла
    :param from_sender:     Адрес отправителя
    :param to_rcpt:         Адреса получателей
    :param subject:         Тема письма
    :param plain:           Тест без разметки (замещающий)
    :param html:            Текст в разметке html (основной)
    :param files_directory: Директория c прикрепляемыми файлами
    :param mail_directory:  Директория для сохранения файла почтового сообщения
    :param images:          Словарь изображений
    :param attachments:     Словарь вложений
    :return: Имя файла сформированного почтового сообщения
    """

    # Создаем контейнер письма
    message = EmailMessage()
    # Указываем кодировку
    message.set_charset("utf-8")
    # Формируем заголовок письма
    message['From'] = from_sender
    message['To'] = to_rcpt
    message['Subject'] = subject

    # Прикрепляем текстовое содержимое тела письма
    message.set_content(plain)

    # Внедряем в тело письма изображения (если они есть)
    if not images is None:
        for cid, image_name in images.items():
            # Генерируем ид изображения
            image_cid = make_msgid(domain="prointegra.ru")
            # Внедряем ид в содержимое html сообщения
            html = html.replace('{' + cid + '}', image_cid[1:-1])
            message.add_alternative(html, subtype="html")
            # Читаем файл изображения
            with open(files_directory + image_name, "r+b") as img_file:
                # Определяем по заголовку тип файла
                _maintype, _subtype = mimetypes.guess_type(img_file.name)[0].split('/')
                # Прикрепляем файл изображения
                message.get_payload()[1].add_related(img_file.read(), maintype=_maintype, subtype=_subtype, cid=image_cid)
    else:
        # Встроенных изображений нет - просто прикрепляем html содержимое Без файлов
        message.add_alternative(html, subtype="html")

    # Прикрепляем файлы (если есть)
    if not attachments is None:
        for alt, attach_name in attachments.items():

            # Читаем файл вложения
            with open(files_directory + attach_name, "r+b") as attach_file:
                # Определяем по заголовку тип файла
                _maintype, _subtype = mimetypes.guess_type(attach_file.name)[0].split('/')
                # Прикрепляем файл изображения
                message.get_payload()[1].add_related(attach_file.read(), maintype=_maintype, subtype=_subtype)

    # Генерируем имя файла сообщения в виде UUID
    filename = str(uuid.uuid4()) + ".msg"
    # Запись сообщения в файл
    with open(mail_directory + filename, 'w+b') as msg_file:
        msg_file.write(message.as_bytes())

    # Возвращаем имя сгенерированного файла
    return filename

class Mailer:
    """
    Класс для отправки почтовых сообщений

    Объекты класса отправляют почтовые сообщения в виде чистого текста и текста HTML-разметки

    Методы
    ----------------
        __init__(self, address:str, port:int, user:str, password:str, tls:bool = False, ssl:bool = True)
            Конструктор: Инициализация
        send(self, msg_path: str)
            Отправка почты
    Атрибуты
    ----------------
        :ivar {str} __address:      Адрес сервера
        :ivar {int} __port:         Порт сервера
        :ivar {str} __user:         Пользователь сервера
        :ivar {str} __password:     Пароль пользователя
        :ivar {bool} __starttls:    Признак использования протокола STARTTLS
        :ivar {bool} __ssl:         Признак использования протокола SSL
    """

    def __init__(self, address:str, port:int, user:str, password:str, tls:bool = False, ssl:bool = True):
        """
        Конструктор: Инициализация

        Инициализирует объект класса настройками подключения к серверу отправки электронной почты. Создает очередь
        сообщений
        :param address:     Адрес сервера
        :param port:        Порт сервера
        :param user:        Пользователь сервера
        :param password:    Пароль пользователя
        :param tls:         Сообщения шифруются
        :param ssl:         Соединение происходит через протокол SSL
        """

        self.__address = address
        self.__port = port
        self.__user = user
        self.__password = password
        self.__tls = tls
        self.__ssl = ssl

    def send(self, msg_path: str):
        """
        Отправка почты

        Отправляет почту из файла почтового сообщения
        :param msg_path: Путь до файла почтового сообщения
        :return: True в случае успешной отправки и объект SMTPException в случае ошибки
        """

        # Загрузка сообщения из файла
        with open(msg_path, "r+b") as file:
            message = BytesParser(policy=default).parse(file)

        # Соединение с сервером
        try:
            # Установлен флаг SSL
            if self.__ssl:
                server = smtplib.SMTP_SSL(self.__address, self.__port)
            else:
                server = smtplib.SMTP(self.__address, self.__port)
            # Установлен флаг STARTTLS
            if self.__tls:
                server.starttls()
            # Вход на сервер
            server.login(self.__user, self.__password)
            # Отправка сообщения
            server.send_message(message, message["From"], message["To"])
            # Выход
            server.quit()
        except smtplib.SMTPException as err:
            return err
        else:
            return True