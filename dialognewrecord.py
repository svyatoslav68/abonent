#!/usr/bin/env python3
# -*- coding: utf8 -*-
# Модуль диалогового окна, предназначенного для создания новой записи в таблицу БД
from sys import argv, exit
from PyQt5.QtWidgets import QDialog, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit, QComboBox
from PyQt5.QtWidgets import QApplication, QMainWindow
from mysqlconnector import getAdminConnection, getConnection
#from qabonent import MainWindow

class newRecordDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.initUi()
        if isinstance(parent, QMainWindow):
            self.laNameModel.setText(parent.mainTable.model().objectName())


    def initUi(self):
        self.buCancel = QPushButton("Отмена")
        self.buCancel.clicked.connect(self.reject)
        self.buOk = QPushButton("Ok")
        self.buOk.clicked.connect(self.accept)
        self.laNameModel = QLabel()
        bottomLayout = QHBoxLayout()
        bottomLayout.addStretch()
        bottomLayout.addWidget(self.buCancel)
        bottomLayout.addWidget(self.buOk)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.laNameModel)
        mainLayout.addLayout(bottomLayout)
        self.setLayout(mainLayout)

if __name__ == '__main__':
    app = QApplication(argv)
    dialog = newRecordDialog(None)
    dialog.show()

    exit(app.exec_())

