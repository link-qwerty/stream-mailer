# Imports
from tempfile import NamedTemporaryFile

# Defines
class TaskManager:
    """
    Класс обработчика заданий (синглетон)

    Объект класса обрабатывает задания из рабочего каталога и создает очередь заданий. В процессе формирования
    очереди выполняются операции, специфичные для каждого задания определенного типа

    Методы
    ----------------
        __new__(cls, *args, **kwargs)
            Конструктор: Создание
       _init__(self, tasks_directory: str, templates_directory: str)
            Конструктор: Инициализация
        parse(self, files:list, parser)
            Парсинг заданий
        get(self, service: str)
            Получение содержимого задания
        __rewrite(self, template_file: str, replaces: str)
            Перезапись файла шаблона
    Атрибуты
    ----------------
        :cvar {any} __instance: Экземпляр класса (синглетон)
        :ivar {str} __tasks_directory:          Директория заданий
        :ivar {str} __templates_directory:      Директория шаблонов
        :ivar {dict} __tasks:                   Очередь заданий
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

    def __init__(self, tasks_directory: str, templates_directory: str):
        """
        Конструктор: Инициализация

        Инициализирует объект класса путями рабочего каталога и каталога шаблонов, создаем переменную класса для
        хранимых данных
        :param tasks_directory: Директория заданий
        :param templates_directory: Директория шаблонов
        """

        self.__tasks_directory = tasks_directory
        self.__templates_directory = templates_directory
        self.__tasks = dict()

    def parse(self, files:list, parser):
        """
        Парсинг заданий

        Парсит рабочую директорию и отрабатывает задания, находящиеся в ней. Работа по чтению файлов заданий и
        их первичная обработка передается стороннему парсеру
        :param files:   Список файлов заданий
        :param parser:  Сторонний обработчик
        :return: None
        """

        # Парсим список файлов и разбираем задания
        for file in files:
            # Получаем содержимое задания
            parser.parse(self.__tasks_directory + file)
            content = parser.get()

            # Определяем сервис задания
            if content["service"] == "mailer":
                # Собираем задание из существующих полей генератором (проверка поля на лету)
                task = dict({x: content[x] for x in ['service', 'from', 'to', 'subject', 'template', 'template_repeat',
                                                  'repeat', 'replaces'] if x in content})
                # Обрабатываем файл текстового шаблона и сохраняем результат во временный файл
                task['template_txt_files'] = self.__from_template(task['template'] + '.txt', task['replaces'])
                # Обрабатываем файл шаблона html и сохраняем результат во временный файл
                task['template_html_files'] = self.__from_template(task['template'] + '.html', task['replaces'])

                # Производим замену в теме сообщения
                for rcpt, replaces in task['replaces'].items():
                    for old, new in replaces.items():
                        task['subjects'] = {rcpt, task['subject'].replace('[' + old + ']', new)}
                # Помещаем задание в очередь
                self.__tasks[file] = task

    def get(self, service: str):
        """
        Получение содержимого задания

        Возвращает первое задание, которое отвечает условию (задание убирается из очереди)
        :param service: Имя сервиса
        :return: Задание
        """

        # Отбираем задание по имени сервиса
        for task_file, task in self.__tasks.items():
            if task['service'] == service:
                print(self.__tasks[task_file])
                return self.__tasks.pop(task_file)

    def __from_template(self, template_file: str, replaces: dict):
        """
        Считывание шаблона и подготовка текста

        Открывает файл-шаблон, считывает из него информацию и заменяет в ней значения согласно списку замены.
        Обработанный текст записывается во временный файл
        :param template_file: Исходный файл шаблона
        :param replaces: Словарь замен
        :return: Список имен временных файлов
        """
        # Создаем список имен временных файлов
        names = list()
        # Открываем файл шаблона
        with open(self.__templates_directory + template_file, "r", encoding="utf-8") as template:
            content = template.read()
        template.close()
        # Производим его обработку, заменяя значения из списка замены
        for replace in replaces.keys():
            for old, new in replaces[replace].items():
                content = content.replace('[' + old + ']', new)
            # Создаем временный именованный файл с отключенными флагами удаления
            tmp_file = NamedTemporaryFile("w+t", encoding="utf-8", delete=False)
            # Записываем в файл обработанный текст
            tmp_file.write(content)
            # Закрываем файл
            tmp_file.close()
            # Записываем имя файла в список
            names.append(tmp_file.name)
        # Возвращаем имя файла
        return names






