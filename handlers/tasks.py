# Imports

# Defines
def transform(text: str, replaces: dict):
    """
    Обработка текста

    Обрабатывает текст, заменяя ключевые слова значениями из словаря замены
    :param text:        Текст для отработки
    :param replaces:    Словарь замен
    :return: Обработанный текст
    """

    # Производим обработку текста, заменяя ключевые слова из значения из списка замены
    for old, new in replaces.items():
        text = text.replace('[' + old + ']', new)

    # Возвращаем обработанный текст
    return text

class TaskManager:
    """
    Класс обработчика заданий (синглетон)

    Объект класса обрабатывает задания из рабочего каталога и создает очередь заданий. В процессе формирования
    очереди выполняются операции, специфичные для каждого задания определенного типа

    Методы
    ----------------
        __new__(cls, *args, **kwargs)
            Конструктор: Создание
        __init__(self, tasks_directory: str, templates_directory: str, parser
            Конструктор: Инициализация
        parse(self, files: list)
            Парсинг заданий
        get(self, service: str = None)
            Получение содержимого задания
        count(self)
            Количество заданий
        __from_template(self, template_file: str, replaces: dict)
            Считывание шаблона и подготовка текста
    Атрибуты
    ----------------
        :cvar {any} __instance:                 Экземпляр класса (синглетон)
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

    def __init__(self, tasks_directory: str, templates_directory: str, parser):
        """
        Конструктор: Инициализация

        Инициализирует объект класса путями рабочего каталога и каталога шаблонов, создаем переменную класса для
        хранимых данных. В объект передается экземпляр стороннего парсера для обработки связанных данных
        :param tasks_directory:     Директория заданий
        :param templates_directory: Директория шаблонов
        :param parser:              Сторонний обработчик
        """

        self.__tasks_directory = tasks_directory
        self.__templates_directory = templates_directory
        self.__parser = parser
        self.__tasks = dict()

    def parse(self, files: list):
        """
        Парсинг заданий

        Парсит рабочую директорию и отрабатывает задания, находящиеся в ней. Работа по чтению файлов заданий и
        их первичная обработка передается стороннему парсеру
        :param files:   Список файлов заданий
        :return: None
        """

        # Парсим список файлов и разбираем задания
        for file in files:
            # Получаем содержимое задания
            self.__parser.parse(self.__tasks_directory + file)
            content = self.__parser.get()

            # Определяем контекст задания
            if content["service"] == "mailer":
                # Собираем задание из существующих полей генератором словаря
                task = dict({x: content[x] for x in ['service', 'from', 'to', 'subject', 'template', 'template_repeat',
                                                    'repeat', 'replaces'] if x in content})
                # Загружаем персональный словарь замен
                self.__parser.parse("db/persons.json")
                persons = self.__parser.get()
                # Разделяем получателей
                recipients = dict()
                for rcpt in task['to'].replace(' ', '').split(','):
                    # Формируем индивидуальные блоки под каждого получателя
                    recipients[rcpt] = {'subject': task['subject'], 'replaces': persons[rcpt],
                                        'txt_body': '', 'html_body': ''}
                # Записываем блоки получателей
                task['to'] = recipients
                # Удаляем элемент с общей темой сообщения
                task.pop('subject')
                # Помещаем задание в очередь
                self.__tasks[file] = task

    def get(self, service: str = None):
        """
        Получение содержимого задания

        Возвращает первое задание, которое отвечает условию (задание убирается из очереди). В процессе производится
        обработка дополнительных полей задания в зависимости от контекста. Если контекст задания не указан,
        то возвращает первое задание в очереди без его отработки
        :param service: Имя сервиса
        :return: Отработанное задание в виде пары {имя_фала | задание}
        """

        # Отбираем задание по имени сервиса
        for task_file, task in self.__tasks.items():
            if task['service'] == service:
                # Если контекст задания почтовая рассылка
                if task['service'] == "mailer":
                    for rcpt in task['to']:
                        # Обрабатываем тему письма
                        task['to'][rcpt]['subject'] = transform(task['to'][rcpt]['subject'],
                                                                task['to'][rcpt]['replaces'])
                        # Загружаем шаблоны (текстовой и html) и производим обработку текста
                        task['to'][rcpt]['txt_body'] = self.__from_template(task['template'] + '.txt',
                                                                            task['replaces'] | task['to'][rcpt][
                                                                                'replaces'])
                        task['to'][rcpt]['html_body'] = self.__from_template(task['template'] + '.html',
                                                                             task['replaces'] | task['to'][rcpt][
                                                                                 'replaces'])
                    # Возвращаем отработанное задание
                    return task_file, self.__tasks.pop(task_file)
                else:
                    # Возвращаем задание без отработки
                    return task_file, self.__tasks.pop(task_file)

    def count(self):
        """
        Количество заданий

        Возвращает количество заданий в списке
        :return: Количество заданий
        """

        return len(self.__tasks)
    def __from_template(self, template_file: str, replaces: dict):
        """
        Считывание шаблона и подготовка текста

        Открывает файл-шаблон, считывает из него информацию и заменяет в ней значения согласно словарю замен
        :param template_file: Исходный файл шаблона
        :param replaces: Словарь замен
        :return: Обработанный текст
        """

        # Открываем файл шаблона
        with open(self.__templates_directory + template_file, "r", encoding="utf-8") as template:
            content = template.read()
        template.close()
        # Производим его обработку, заменяя значения из списка замены
        content = transform(content, replaces)
        # Возвращаем обработанный текст
        return content
