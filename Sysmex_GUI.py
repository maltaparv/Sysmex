from PyQt5 import QtWidgets
from mydesign import Ui_MainWindow, QtGui, QtCore  # импорт нашего сгенерированного файла
import sys


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # self.ui.label.setFont(QtGui.QFont('SansSerif', 30))  # Изменение шрифта и размера
        # self.ui.label.setGeometry(QtCore.QRect(10, 10, 200, 200))  # изменить геометрию ярлыка
        # self.ui.btn_run.clicked.connect(self.btnClicked)  # подключение клик-сигнал к слоту btnClicked
        # self.ui.btn_run.clicked.connect(btn_click)  # подключение клик-сигнал к слоту btnClicked


def btn_click():
    print('Click!')


app = QtWidgets.QApplication([])
application = mywindow()
application.show()
sys.exit(app.exec())
