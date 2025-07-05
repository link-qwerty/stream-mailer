# Imports
import json

# Defines
class JSONHandler:
    """
    Класс обработчика файлов JSON

    Объект класса хранит данные, загруженные из файлов JSON, и отдает их по запросу

    Методы
    ----------------
        __init__(self)
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
        :ivar {any} __data__: Данные JSON
    """

    def __init__(self):
        """
        Конструктор: Инициализация

        Инициализирует объект-хендлер
        """

        self.__data = dict()

    def parse(self, filename:str):
        """
        Парсинг файла

        Открывает файл JSON, парсит его и сохраняет полученные результаты в переменную объекта
        :param filename:    Имя файла JSON
        :return: None
        """

        # Открываем файл
        with open(filename, 'r', encoding='utf-8') as file:
            # Записываем данные в переменную класса
            self.__data = json.load(file)

    def dump(self, filename: str):
        """
        Запись данных в файл

        Записывает данные из внутреннего хранилища в файл
        :param filename:    Имя файла JSON
        :return: None
        """

        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(self.__data, file, ensure_ascii=False, indent=4)

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

        return self.__data if (section is None and key is None) else self.__data[section][key]
