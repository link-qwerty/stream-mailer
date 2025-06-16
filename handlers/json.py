# Imports
import json

# Defines
class JSONHandler:
    """
    Класс обработчика файлов JSON

    Объект класса хранит данные, загруженные из файлов JSON, и отдает их по запросу

    Методы
    ----------------
        __init__(self, filename: str)
            Конструктор: Инициализация
        get(self, section: str, key: str)
            Получение данных
    Атрибуты
    ----------------
        :ivar {str} filename: Имя файла JSON
        :ivar {any} __data__: Данные JSON
    """

    def __init__(self, filename: str):
        """
        Конструктор: Инициализация

        Инициализирует объект-хендлер именем файла, открывает указанный файл и загружает данные из него в переменную
        объекта
        :param str filename: Имя файла JSON
        """

        self.__filename = filename
        with open(self.__filename, 'r', encoding= 'utf-8') as file:
            self.__data = json.load(file)

    def get(self, section: str = None, key: str = None):
        """
        Получение данных

        Возвращает данные из JSON по имени секции и имени ключа (имени переменной) в ней. Если аргументы не заданы,
        то возвращает весь массив данных
        :param section: Секция данных (имя словаря)
        :param key: Ключ секции (ключ словаря)
        :return: Содержимое ключа или весь массив данных
        """

        return self.__data if (section is None and key is None) else self.__data[section][key]
