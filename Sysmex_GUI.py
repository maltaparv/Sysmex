from PyQt5 import QtCore, QtGui, QtWidgets

from mydesign import Ui_MainWindow, QtGui, QtCore  # импорт нашего сгенерированного файла
import sys
# doc: https://python-scripts.com/pyqt5#pyqt5-designer
import socket
import pyodbc  # для MS SQL SERVER - рекомендовано Microsoft
from Parsing import parse_xn350, record
from ProcLib import write_log, write_errlog, read_ini
from ClassLib import const
from Sysmex_XN import create_socket, sql_insert, transfer, mainloop
from threading import Thread
#import _thread


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # self.ui.label.setFont(QtGui.QFont('SansSerif', 30))  # Изменение шрифта и размера
        # self.ui.label.setGeometry(QtCore.QRect(10, 10, 200, 200))  # изменить геометрию ярлыка
        # self.ui.btn_run.clicked.connect(self.btnClicked)  # подключение клик-сигнал к слоту btnClicked
        self.ui.btn_run.clicked.connect(btn_click)  # подключение клик-сигнал к слоту btnClicked
        self.ui.btn_test_1.clicked.connect(btn_test1)
        self.ui.btn_test_2.clicked.connect(btn_test2)

def btn_click():
    msg = 'Старт прослушки порта. '
    print(msg)
    application.ui.plainTextEdit.appendPlainText(msg)
    # thread1 = Thread(target=mainloop())
    # thread1.start()
    # _thread.start_new_thread(mainloop())
    # mainloop()

    daemonThread.start()

def btn_test1():
    print('test1')
    application.ui.plainTextEdit.appendPlainText('test1')


def btn_test2():
    msg = 'закрыть прослушку порта. '
    print(msg)
    application.ui.plainTextEdit.appendPlainText(msg)
    #thread1.join()
    daemonThread.join()


if __name__ == '__main__':
    # ToDo_done read_ini
    # const = CONST()  # to fill from ini
    # fn_ini = 'sysmex350.ini'
    fn_ini = 'sysmex.ini'
    read_ini(fn_ini)
    write_log(f'Run {const.analyser_name}, analyser_id={const.analyser_id}, ' +
              f'analyser_location={const.analyser_location}, listening IP:{const.host}:{const.port}.')


    app = QtWidgets.QApplication([])
    application = mywindow()
    application.show()

    daemonThread = Thread(target=mainloop())
    daemonThread.setDaemon(True)

    sys.exit(app.exec())
