# Imports
import uuid
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.policy import default
from email.parser import BytesParser

# Defines
def make(from_sender:str, to_rcpt:str, subject:str, plain: str, html: str, mail_directory: str):
    """
    Создание сообщения

    Формирует файл сообщения, записывает его в каталог для отправки и возвращает имя сформированного файла
    :param from_sender:     Адрес отправителя
    :param to_rcpt:         Адреса получателей
    :param subject:         Тема письма
    :param plain:           Тест без разметки (замещающий)
    :param html:            Текст в разметке html (основной)
    :param mail_directory:  Директория для сохранения файла почтового сообщения
    :return: Имя файла сформированного почтового сообщения
    """

    #  Формируем заголовок письма
    message = MIMEMultipart("alternative")
    message['From'] = from_sender
    message['To'] = to_rcpt
    message['Subject'] = subject

    # Добавляем содержимое тела письма (добавленный последним блок считается приоритетным)
    message.attach(MIMEText(plain, "plain"))
    message.attach(MIMEText(html, "html"))

    # Генерируем имя сообщения в виде UUID
    filename = str(uuid.uuid4()) + ".msg"
    # Запись сообщения в файл
    with open(mail_directory + filename, 'w+b') as file:
        file.write(message.as_bytes())
    file.close()

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
        file.close()

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
            server.sendmail(message["From"], message['To'], message.as_string())
            # Выход
            server.quit()
        except smtplib.SMTPException as err:
            return err
        else:
            return True