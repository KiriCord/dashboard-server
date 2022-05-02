"""Класс простого журнала в виде синглтона для обращений из разных модулейучш"""

import logging

__all__ = ['get_logger']


class SingletonType(type):
    """Класс для синглтонов"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonType,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SiLogger(object, metaclass=SingletonType):
    """
    Класс логирования на основе синглтона и библиотеки logging
    Можно использовать один экзмепляр логгера в разных модулях проекта

    Примеры использования:
    import si_logger
    logger = si_logger.get_logger(scope='common', logfile='info.log')

    # Варианты сообщений info|debug|warning|error из модуля logging
    logger.info('info message')
    logger.debug('debug message')
    logger.warning('warning message')
    logger.error('error message)

    # Создаем еще один логгер для дебага в другой файл
    dlogger = si_logger.get_logger(scope='debug', 'debug.log')
    dlogger.info('info to debug scope')

    # В другом модуле получаем экземпляр логгера для пространства common
    # При первом вызове:
    # -- если файл не указан, логгер будет вещать только в консоль
    # -- если указан файл в первый раз и не указан второй раз для одного scope,
    #      то будет писать в тот же файл, вернется экземпляр первого вызов
    #      для одного и того же scope
    import si_logger
    logger = si_logger.get_logger(scope='common', logfile='info.log')
    logger.info('info message in another module')
    """
    # __metaclass__ = SingletonType   # python 2 Style
    _logger = {}

    def __create_logger(self, scope='common', logfile=None):
        is_rewrite = True  # если True, то файл журнала будет перезатираться
        is_console = True  # если True, то логгер будет сообщать и в консоль

        log_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        root_logger = logging.getLogger(scope)
        root_logger.setLevel(logging.DEBUG)

        if logfile:
            if is_rewrite:
                file_mode = 'w'
            else:
                file_mode = 'a'
            file_handler = logging.FileHandler(logfile,
                                               mode=file_mode,
                                               encoding='utf8')
            file_handler.setFormatter(log_formatter)
            root_logger.addHandler(file_handler)

        if is_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formatter)
            root_logger.addHandler(console_handler)

        root_logger.setLevel(logging.INFO)
        root_logger.info(f'Created a logger in scope "{scope}"')
        self._logger[scope] = root_logger
        return root_logger

    def __init__(self, scope='common', logfile=None):
        self.__create_logger(scope, logfile)

    def get_logger(self, scope, logfile):
        """Создадим или вернем ранее созданный объект логгера"""
        if scope not in self._logger:
            self.__create_logger(scope, logfile)

        return self._logger[scope]


def get_logger(scope='common', logfile=None):
    """
    Получение или создание логгера
    :param scope: Пространство логгера, уникальное имя логгера в рамках проекта
    :param logfile: Путь или имя файла на диске для сохранения сообщений
    :return: Возвращается экземпляр нового или существующего логгера
    """
    return SiLogger.__call__(scope, logfile).get_logger(scope, logfile)