# Imports
from queue import Queue
import re
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes

# Defines
class MessageBodyContainer:
    """
    Класс контейнера сообщения e-mail

    Объекты класса содержат тело сообщения, поделенное на функциональные блоки. Сообщение передается в виде строки.
    Если строка содержит html-разметку, то объект преобразует текст с разметкой в чистый текст

    Методы
    ----------------
        __init__(self, plain: str, html: str)
            Конструктор: Инициализация
    Атрибуты
    ----------------
        :ivar {str} __message_body_plain: Текстовое тело сообщения
        :ivar {str} __message_body_html:  Тело сообщения в формате HTML
        :ivar {dict} __images:            Словарь изображений
    """

    def __init__(self, text: str):
        """
        Конструктор: Инициализация

        Инициализирует объект начальными данными, преобразует текст с разметкой html в чистый
        :param text: Текст сообщения
        """

        if text.find("<html>"):
            self.__message_body_plain = re.sub(r'<[^<]+?>', '', text)
            self.__message_body_html = text
        else:
            self.__message_body_plain = text
            self.__message_body_html = None

    def get_plain(self):
        return self.__message_body_plain

    def get_html(self):
        return self.__message_body_html


class MailSender:
    """
    Класс для отправки почтовых сообщений

    Объекты класса формируют и отправляют почтовые сообщения в виде чистого текста и в формате HTML (изображения
    прикрепляются в тело сообщения). При формировании сообщения e-mail использует контейнер MessageBodyContainer

    Методы
    ----------------
        __init__(self, address:str, port:int, user:str, password:str, tls:bool = False, ssl:bool = True)
            Конструктор: Инициализация
        make(self, from_sender:str, to_rcpt:str, cc:str, bcc:str, subject:str, message_body: MessageBodyContainer, filename: str)
            Создание сообщения
    Атрибуты
    ----------------
        :ivar {str} __address:      Адрес сервера
        :ivar {int} __port:         Порт сервера
        :ivar {str} __user:         Пользователь сервера
        :ivar {str} __password:     Пароль пользователя
        :ivar {bool} __starttls:    Признак использования протокола STARTTLS
        :ivar {bool} __ssl:         Признак использования протокола SSL
        :ivar {any} __q_messages:   Очередь сообщений
    """

    def __init__(self, address:str, port:int, user:str, password:str, tls:bool = False, ssl:bool = True):
        """
        Конструктор: Инициализация

        Инициализирует объект класса начальными значениями, которые впоследствии будут использоваться для
        соединения с сервером SMTP и отправки сообщений
        :param address:     Адрес сервера
        :param port:        Порт сервера
        :param user:        Пользователь сервера
        :param password:    Пароль пользователя
        :param tls:         Сообщения шифруются
        :param ssl:         Используется протокол SSL
        """

        self.__address = address
        self.__port = port
        self.__user = user
        self.__password = password
        self.__starttls = tls
        self.__ssl = ssl
        self.__q_messages = Queue()

    def make(self, from_sender:str, to_rcpt:str, cc:str, bcc:str, subject:str, message_body: MessageBodyContainer, path: str):
        """
        Создание сообщения

        Формирует файл сообщения, записывает его в каталог для отправки и помещает путь до файла в очередь на
        отправку
        :param from_sender: Отправитель
        :param to_rcpt: Получатель
        :param cc: Копия
        :param bcc: Скрытая копия
        :param subject: Тема письма
        :param message_body: Тело сообщения
        :param path: Путь до файла, где будет сохранено сообщение
        :return: None
        """

        #  Создание заголовка сообщения
        message = EmailMessage()
        message['From'] = from_sender
        message['To'] = to_rcpt.split(',')
        message['Cc'] = cc
        message['Bcc'] = bcc
        message['Subject'] = subject

        # Создание тела сообщения (замещающий текст)
        message.set_content(message_body.get_plain())
        # Создание тела сообщения (основной текст)
        message.add_alternative(message_body.get_html())

        # Запись сообщения в файл
        with open(path, 'w+b') as file:
            file.write(message.as_bytes())

        # Запись сообщения на отправку в очередь
        self.__q_messages.put(path)

    def send(self):
        """

        :return:
        """

        for path in self.__q_messages.get():
            with open(path, 'r') as file:
                message = file.read()

                if self.__ssl:
                    with smtplib.SMTP(self.__address, self.__port) as server:
                        if self.__starttls:
                            server.starttls()





