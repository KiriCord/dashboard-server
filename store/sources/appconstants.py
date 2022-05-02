import uuid


class AppConstants():
    """Программные константы"""
    APP_NAME = 'LocalWebServer'
    LOG_APP_NAME = 'Локальный веб-сервер'
    LOG_FILE = 'server.log'
    INSTANCE_UUID = str(uuid.uuid4())
