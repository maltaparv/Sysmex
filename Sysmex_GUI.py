from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor

#from mydesign import Ui_MainWindow, QtGui, QtCore  # импорт нашего сгенерированного файла
from mydesign import Ui_MainWindow  # импорт нашего сгенерированного файла
import sys
import socket
import pyodbc  # для MS SQL SERVER - рекомендовано Microsoft
from Parsing import parse_xn350, record
from ProcLib import write_log, write_errlog, read_ini
from ClassLib import const
from Sysmex_XN import create_socket, sql_insert, transfer, mainloop
from threading import Thread
import time


# doc: https://python-scripts.com/pyqt5#pyqt5-designer
# https://evileg.com/ru/post/579/  - Использование QThread с применением moveToThread
# Объект, который будет перенесён в другой поток для выполнения кода
class BrowserHandler(QtCore.QObject):
    # running = False
    newTextAndColor = QtCore.pyqtSignal(str, object)

    # метод, который будет выполнять алгоритм в другом потоке
    def run(self):
        while True:
            # посылаем сигнал из второго потока в GUI поток
            self.newTextAndColor.emit(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - thread 2 var 1.\n', QColor(0, 150, 0))
            QtCore.QThread.msleep(1000)
        # mainloop()


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('Sysmex550.ico'))  # ToDo а для 550-го нужно ли измнять иконку?
        self.statusBar().showMessage('Состояние: готов.')
        # self.ui.btn_run.clicked.connect(self.btnClicked)  # подключение клик-сигнал к слоту btnClicked
        self.ui.btn_run.clicked.connect(btn_click)  # подключение клик-сигнал к слоту btnClicked
        self.ui.btn_test_1.clicked.connect(btn_test1)
        self.ui.btn_test_2.clicked.connect(btn_test2)

        # создадим поток
        self.thread = QtCore.QThread()
        # создадим объект для выполнения кода в другом потоке
        self.browserHandler = BrowserHandler()
        # перенесём объект в другой поток
        self.browserHandler.moveToThread(self.thread)
        # после чего подключим все сигналы и слоты
        self.browserHandler.newTextAndColor.connect(self.addNewTextAndColor)
        # подключим сигнал старта потока к методу run у объекта, который должен выполнять код в другом потоке
        self.thread.started.connect(self.browserHandler.run)
        # запустим поток
        self.thread.start()

    @QtCore.pyqtSlot(str, object)
    def addNewTextAndColor(self, string, color):
        self.ui.textBrowser.setTextColor(color)
        self.ui.textBrowser.append(string)

    def closeEvent(self, event):
        """ Предупреждение при закрытии окна

        :param event:
        :return:
        """
        _QMessageBox = QtWidgets.QMessageBox
        reply = _QMessageBox.question(self, ' Последнее предупреждение: ',
                                      'Вы действительно хотите закрыть программу?',
                                      _QMessageBox.Yes | _QMessageBox.No, _QMessageBox.No)
        if reply == _QMessageBox.Yes:
            event.accept()
            write_log('Завершение работы.')
        else:
            event.ignore()
            write_log('Передумали выходить.')


def btn_click():
    msg = 'Старт прослушки порта. '
    print(msg)
    application.ui.textBrowser.setTextColor(QColor(0, 0, 150))
    application.ui.textBrowser.append(msg)


def btn_test1():
    msg = 'test1.'
    application.ui.textBrowser.setTextColor(QColor(150, 0, 0))
    application.ui.textBrowser.append(msg)


def btn_test2():
    msg = 'закрыть прослушку порта. '
    # print(msg)
    application.ui.textBrowser.setTextColor(QColor(0, 0, 150))
    application.ui.textBrowser.append(msg)


def write_form(msg):
    application.ui.textBrowser.setTextColor(QColor(0, 150, 0))
    application.ui.textBrowser.append(msg)


if __name__ == '__main__':
    fn_ini = 'sysmex.ini'
    read_ini(fn_ini)
    write_log(f'Run {const.analyser_name}, analyser_id={const.analyser_id}, ' +
              f'analyser_location={const.analyser_location}, listening IP:{const.host}:{const.port}.')

    app = QtWidgets.QApplication(sys.argv)
    application = MyWindow()
    application.show()

    sys.exit(app.exec())
