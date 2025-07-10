# Imports
import json
import logging
from json import JSONDecodeError

# Defines
class JSONHandler:
    """
    Класс обработчика файлов JSON

    Объект класса хранит данные, загруженные из файлов JSON, и отдает их по запросу. Имеет функционал по сбросу
    данных в файл

    Методы
    ----------------
        __init__(self, logs_directory: str)
            Конструктор: Инициализация
        parse(self, filename:str)
            Парсинг файла
        dump(self, filename: str)
            Запись данных в файл
        set(self, section: str, key: str, value: any)
            Изменение данных
        get(self, section: str, key: str)
            Получение данных
    Атрибуты
    ----------------
        :ivar {any} __data:   Данные JSON
    """

    def __init__(self, logs_directory: str):
        """
        Конструктор: Инициализация

        Инициализирует объект-хендлер. Объявляем переменную объекта для хранения данных и настраиваем логгер
        :param logs_directory: Директория для лога
        """

        # Настраиваем логгер
        self.logs_directory = logs_directory
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)
        logger_handler = logging.FileHandler(f"{logs_directory}/{__name__}.log", mode='a')
        logger_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
        logger_handler.setFormatter(logger_formatter)
        self.__logger.addHandler(logger_handler)
        # Инициализируем данные
        self.__data = dict()

    def parse(self, filename:str):
        """
        Парсинг файла

        Открывает файл JSON, парсит его и сохраняет полученные результаты в переменную объекта
        :param filename:    Имя файла JSON
        :return: None
        """

        # Открываем файл
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                # Записываем данные в переменную класса
                self.__data = json.load(file)
        except FileNotFoundError:
            self.__logger.error("File not found", exc_info=True)
        except IOError:
            self.__logger.error(f"An error occurred while reading the file {filename}", exc_info=True)
        except JSONDecodeError:
            self.__logger.error(f"An error occurred while decode the file {filename}", exc_info=True)

    def dump(self, filename: str):
        """
        Запись данных в файл

        Записывает данные из внутреннего хранилища в файл
        :param filename:    Имя файла JSON
        :return: None
        """

        # Открываем файл на запись
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(self.__data, file, ensure_ascii=False, indent=4)
        except IOError:
            self.__logger.error(f"An error occurred while writing the file {filename}", exc_info=True)
        except KeyError:
            self.__logger.error("Type error occurred", exc_info=True)

    def set(self, value: any, section: str = None, key: str = None):
        """
        Изменение данных

        Изменяет данные в объекте по имени секции и ключу. Если аргументы секции и ключа не заданы, то перезаписывает
        весь массив данных
        :param value:       Новое значение
        :param section:     Секция данных (имя словаря)
        :param key:         Ключ секции (ключ словаря)
        :return: None
        """

        if section is None and key is None:
            self.__data = value
        else:
            self.__data[section][key] = value


    def get(self, section: str = None, key: str = None):
        """
        Получение данных

        Возвращает данные из JSON по имени секции и имени ключа (имени переменной) в ней. Если аргументы не заданы,
        то возвращает весь массив данных
        :param section:     Секция данных (имя словаря)
        :param key:         Ключ секции (ключ словаря)
        :return: Содержимое ключа или весь массив данных
        """

        if section is None and key is None:
            return self.__data
        else:
            try:
                return self.__data[section][key]
            except KeyError:
                self.__logger.error(f"Data not found, section {section}, key {key}", exc_info=True)
            finally:
                return None