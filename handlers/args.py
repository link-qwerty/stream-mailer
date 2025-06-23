# Imports
import argparse
import builtins

# Defines

class ArgsHandler:
    """
    Класс обработчика параметров командной строки (синглетон)

    Объект класса предназначен для конструирования параметров командной строки и их обработки

    Методы
    ----------------
        __new__(cls, *args, **kwargs)
            Конструктор: Создание
        __init__(self, name:str, description: str)
            Конструктор: Инициализация
        parse(self, dict_args: dict)
            Парсинг аргументов
        get(self, name:str = None)
            Получение аргументов командной строки
    Атрибуты
    ----------------
        :cvar {any} __instance: Экземпляр класса (синглетон)
        :ivar {any} __cmd:      Экземпляр класса парсера
        :ivar {any} __args:     Переданные аргументы командной строки
    """

    __instance = None

    def __new__(cls, *args, **kwargs):
        """
        Конструктор: Создание

        Размещает в памяти объект-хендлер и записывает ссылку на него в переменную класса. При следующем вызове
        конструктора новый объект не будет создаваться, вместо него будет использоваться существующий
        :param args:    Список позиционных аргументов
        :param kwargs:  Словарь именованных аргументов
        """

        # Формируем из объекта синглетон
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, name:str, description: str):
        """
        Конструктор: Инициализация

        Инициализирует объект-хендлер, создает парсер аргументов командной строки и инициализирует пустой список
        аргументов
        :param name:        Имя программы
        :param description: Описание программы
        """

        self.__cmd = argparse.ArgumentParser(prog=name, description=description)
        self.__args = list()

    def parse(self, dict_args: dict):
        """
        Парсинг аргументов

        Разбирает словарь аргументов на секции, инициализирует ими парсер и получает список аргументов из
        командной строки
        :param dict_args:   Словарь аргументов
        :return: None
        """

        # Разбираем словарь на секции и создаем список аргументов
        for section, content in dict_args.items():
            # Подменяем строковое описание встроенного класса на его тип
            if 'type' in content:
                content['type'] = getattr(builtins, content['type'])

            # Описываем генератор списка именованных аргументов
            named_args = {x: content[x] for x in ['help', 'action', 'type', 'default', 'required'] if x in content}
            # Передаем словарь именованных аргументов в вызов функции
            self.__cmd.add_argument(content["flag"], f'--{section}', **named_args)

        # Сохраняем аргументы командной строки в переменную класса
        self.__args = vars(self.__cmd.parse_args())

    def get(self, name:str = None):
        """
        Получение аргументов командной строки

        Возвращает значение аргумента командной стоки по имени. Если метод вызван без аргументов, то возвращает весь
        список переданных аргументов
        :param name: Имя аргумента командной строки
        :return: Значение выбранного аргумента или весь список
        """

        return self.__args if name is None else self.__args[name]

