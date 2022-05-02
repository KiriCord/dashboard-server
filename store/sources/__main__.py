# coding=utf-8
import sys
import os

import logging
import si_logger
import traceback

import socketio

from appconstants import AppConstants

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtGui import QIcon, QTextCursor
from PySide2.QtWidgets import QApplication, QMainWindow

# from grad_api import GChild


Signal = QtCore.Signal
Slot = QtCore.Slot


class Signaller(QtCore.QObject):
    signal = Signal(str, logging.LogRecord)


class QtHandler(logging.Handler):
    def __init__(self, slotfunc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.signaller = Signaller()
        self.signaller.signal.connect(slotfunc)

    def emit(self, record):
        s = self.format(record)
        self.signaller.signal.emit(s, record)


class MainWindow(QtWidgets.QWidget):

    """Logger Colors"""
    COLORS = {
        logging.DEBUG: 'black',
        logging.INFO: 'black',
        logging.WARNING: 'orange',
        logging.ERROR: 'red',
        logging.CRITICAL: 'purple',
    }

    def __init__(self):
        super(MainWindow, self).__init__()

        self.initVars()
        self.initUI()
        self.initLogger()
        self.initServer()

        self.logger.info('Интерфейс приложения инициализирован')

    def closeEvent(self, event):
        self.logger.info('closeevent')

        super(MainWindow, self).closeEvent(event)

    def initVars(self):
        """Инициализация переменных главного окна"""

        # Интегрируемся в ГРАД
        # self.gradWindow = GChild.GradWindow()
        # self.gradWindow.init_grad(self.winId(), 0)

        # self.gradWindow.on_pdmcnotify.bind(func=self.on_pdmc_update)
        # self.gradWindow.on_after_start.bind(
        #     func=self.on_after_start_connect_navigator)

        # self.appFolder = os.path.join(self.gradWindow.path_main(),
        #                               'store', AppConstants.APP_NAME)
        # self.settingsFile = os.path.join(self.appFolder, 'settings.json')

    def initUI(self):
        """Первичная настройка UI"""

        # self.setWindowIcon(QIcon(os.path.join(
        #     self.appFolder, 'icons', 'icon.png')))
        self.setWindowTitle(AppConstants.LOG_APP_NAME),
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        layout = QtWidgets.QGridLayout(self)
        map_run_check_btn = QtWidgets.QPushButton('Проверка карты')
        map_run_check_btn.clicked.connect(self.on_map_check_btn_click)

        self.logEdit = QtWidgets.QTextEdit()
        font = QtGui.QFont()
        font.setPointSize(9)
        self.logEdit.setFont(font)
        self.logEdit.setLineWrapColumnOrWidth(80)
        self.logEdit.setReadOnly(True)

        layout.addWidget(map_run_check_btn, 0, 0)
        layout.addWidget(self.logEdit, 1, 0)

        self.setLayout(layout)

    def initLogger(self):
        # logger_filepath = os.path.join(self.gradWindow.path_main(),
        #                                'store', AppConstants.APP_NAME,
        #                                AppConstants.LOG_FILE)

        # self.logger = setup_logging(uuid=AppConstants.INSTANCE_UUID,
        #                             grad_window=self.gradWindow,
        #                             logger_filepath=logger_filepath)
        self.logger = si_logger.get_logger(scope='common', logfile='info.log')

        self.logToGuiHandler = QtHandler(self.toLog)

        log_formatter = logging.Formatter(
            f'{{asctime}}: {{message}}',
            style='{',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        self.logToGuiHandler.setFormatter(log_formatter)
        self.logToGuiHandler.setLevel(logging.INFO)

        self.logger.addHandler(self.logToGuiHandler)

    def initServer(self):
        self.sio = socketio.AsyncServer()
        self.clients = set()
        self.logger.error('Инициализация сервиса')

    # @sio.event
    # def connect(sid, environ, auth):
    #     print('connect ', sid)

    # @sio.event
    # def disconnect(sid):
    #     print('disconnect ', sid)

    @Slot(str, logging.LogRecord)
    def toLog(self, status, record):
        color = self.COLORS.get(record.levelno, 'black')
        s = '<font color="%s">%s</font><br>' % (color, status)

        self.logEdit.moveCursor(QTextCursor.End)
        self.logEdit.insertHtml(s)
        self.logEdit.moveCursor(QTextCursor.End)

    def on_after_start_connect_navigator(self, *args):
        # Почему-то сюда всегда приходит, даже без навигатора, поэтому игнорим
        # return

        if (len(args) == 1) and (args[0] is None):
            self.logger.info('Режим работы без навигатора')
            return

        self.logger.info('Подключились к навигатору с параметрами {}'
                         .format(', '.join(args)))

    def on_map_check_btn_click(self):
        log_message = 'Карта не запущена'
        # if not self.gradWindow.is_map_running():
            # log_message = 'Карта не запущена'
        self.logger.warn(log_message)

    def on_pdmc_update(self, arg, hwnd, chanel, base, period, data):
        """
        Обработчик события обновления данных навигатора
        Self - значение параметра obj, при задании обработчика события
        from - Win-API Handle окна-источника
        channel - имя канала
        base - изменились месторождения/проекты
        period - изменился период
        data - изменился список скважин, список контуров, сеток и т.д.
        """
        self.gradWindow.update_params_from_pdmc()
        self.logger.info('Параметры навигаторы были изменены:')
        self.logger.info('>> Месторождение/объекты.. {}'.format(bool(base)))
        self.logger.info('>> Дата.. {}'.format(bool(period)))
        self.logger.info('>> Данные в навигаторе.. {}'.format(bool(data)))

        if period:
            self.logger.info('>>> период {}'.format(
                self.gradWindow.gradparams.period_str()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())  # Запуск обработчика цепи событий
