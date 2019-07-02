#!/usr/bin/env python3
# -*- coding: utf8 -*-
# Приложение для работы со списками телефонов, номеров и тому подобное
from sys import argv, exit
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit,QVBoxLayout, QHBoxLayout, QCheckBox, QSpinBox
from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QMessageBox, QItemDelegate, QStyledItemDelegate
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot
from PyQt5.QtGui import QPalette, QColor
from MyWidgets import PhonesTableView
from Models import ModelAbonents
from Delegats import comboDelegate, comboBdDelegate, tableDelegate,functionViewTableEditDelegate
from numberDialog import numberDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.abonentModel = ModelAbonents()
        self.phonesModel = ModelAbonents()
        self.initUI()

    def createActions(self):
        self.actionExit=QAction("Выход") 
        self.actionExit.triggered.connect(QCoreApplication.instance().quit)
        self.actionNumbers=QAction("Номера")
        self.actionNumbers.setShortcut("Ctrl+N")
        self.actionNumbers.triggered.connect(self.showNumbers)
        self.actionAbonents=QAction("Абоненты")
        self.actionAbonents.setShortcut("Ctrl+A")
        self.actionAbonents.triggered.connect(self.showAbonents)
        self.actionUpdate=QAction("Обновить")
        self.actionUpdate.setShortcut("Ctrl+R")
        self.actionSelectNumber=QAction("Выбор номера")
        self.actionSelectNumber.triggered.connect(self.selectNumber)
        self.actionRooms=QAction("Помещения")
        self.actionSaveData=QAction("Сохранить")
        self.actionSaveData.setShortcut("Ctrl+S")
        self.actionLoadData=QAction("Загрузить")
        self.actionHelpAbout=QAction("О программе")
        self.actionHelpAbout.setShortcut(Qt.Key_F1)
        self.actionHelpAbout.triggered.connect(self.helpSlot)
        self.actionHelpAboutQt=QAction("О Qt5")
        self.actionHelpAboutQt.triggered.connect(self.helpQt)

    def createMenu(self):
        appMenu=super().menuBar()
        fileMenu=appMenu.addMenu("&Файл")
        fileMenu.addAction(self.actionExit)
        #appMenu.addMenu(fileMenu)
        dataMenu=appMenu.addMenu("&Данные")
        dataMenu.addAction(self.actionNumbers)
        dataMenu.addAction(self.actionAbonents)
        dataMenu.addAction(self.actionSelectNumber)
        tableMenu=appMenu.addMenu("&Таблица")
        tableMenu.addAction(self.actionLoadData)
        tableMenu.addAction(self.actionSaveData)
        tableMenu.addAction(self.actionUpdate)
        helpMenu=appMenu.addMenu("&Помощь")
        helpMenu.addAction(self.actionHelpAbout)
        helpMenu.addAction(self.actionHelpAboutQt)
        #appMenu.addMenu(helpMenu)
        
    def createWidgets(self):
        self.mainTable = PhonesTableView()
        self.setCentralWidget(self.mainTable)

    def initUI(self):
        self.createWidgets()
        self.createActions()
        self.createMenu()
        super().setWindowTitle("Справочник по телефонным аппаратам")

    def showNumbers(self):
        SQL="SELECT n.id_number as `Код`, n.name_net as `Сеть`, n.number as `Номер`, n.port_number as `Номер порта`, n.permit as `Указание`  FROM numbers n "
        self.phonesModel.setQuery(SQL)
        self.mainTable.setModel(self.phonesModel)
        delegate = QStyledItemDelegate(self)
        self.mainTable.setItemDelegateForColumn(3, delegate)
        self.actionUpdate.triggered.connect(self.phonesModel.resetData)
        self.actionSaveData.triggered.connect(self.phonesModel.saveData)

    def showAbonents(self):
        SQL="SELECT p.id_phone as `Код`, p.product_number as 'Зав. №', p.inv_number as 'Инв. №', p.cod_type_TA as 'Код типа', p.date_issue as 'Дата выпуска', p.state as 'Состояние', p.cod_number as 'Код номера', n.name_net as 'Сеть', n.number as 'Номер' from phones p LEFT JOIN types_TA t ON p.cod_type_TA = t.id LEFT JOIN numbers n ON p.cod_number = n.id_number"
        self.mainTable.setModel(self.abonentModel)
        self.abonentModel.setQuery(SQL)
        self.actionUpdate.triggered.connect(self.mainTable.model().resetData)
        #cboxDelegate = comboDelegate(self)
        #cboxDelegate.fillContent("SELECT name_type as value, id as id FROM types_TA")
        #self.mainTable.setItemDelegateForColumn(3, cboxDelegate)
        typeDelegate = comboBdDelegate(self,'types_TA', 'name_type')
        #print("id of typeDelegate = {}\ncontent = {}".format(id(typeDelegate), typeDelegate.content))
        #print("id of typeDelegate = ",id(typeDelegate))
        self.mainTable.setItemDelegateForColumn(3, typeDelegate)
        stateDelegate = comboBdDelegate(self,'phone_status', 'name_status')
        #print("id of typeDelegate = {}\ncontent = {}".format(id(typeDelegate), typeDelegate.content))
        #print("id of stateDelegate = {}\ncontent = {}".format(id(stateDelegate), stateDelegate.content))
        self.mainTable.setItemDelegateForColumn(5, stateDelegate)
        self.actionSaveData.triggered.connect(self.abonentModel.saveData)

        #tabDelegate = tableDelegate(self)
        tabDelegate = functionViewTableEditDelegate(self, 'numbers', lambda row:row['name_net']+':'+row['number'])
        #tabDelegate.fillContent()
        self.mainTable.setItemDelegateForColumn(6, tabDelegate)

        #dateDelegate = QItemDelegate(self)
        #self.mainTable.setItemDelegateForColumn(5, dateDelegate)
        #self.mainTable.setItemDelegateForColumn(6, dateDelegate)

    @pyqtSlot()
    def helpSlot(self):
        QMessageBox.warning(self, "О программе", "Это хорошая программа", QMessageBox.Ok)

    @pyqtSlot()
    def helpQt(self):
        QMessageBox.aboutQt(self, "О библиотеке Qt")

    @pyqtSlot()
    def selectNumber(self):
        listFlters = []
        listFlters.append(dict(name_field='name_net', alias="Сеть", widget='QComboBox', condition = 'eq', SqlFill = "SELECT DISTINCT name_net FROM numbers") )
        listFlters.append(dict(name_field='number', alias="Номер", widget='QLineEdit', condition = 'like', SqlFill = "")) 
        dialog = numberDialog(self, listFlters)
        dialog.setNameTable("numbers")
        dialog.exec()

if __name__ == '__main__':
    #app = QApplication(sys.argv)
    app = QApplication(argv)
    desktop = QApplication.desktop()

    w = MainWindow()
    w.move(0,0)
    w.resize(desktop.width(), desktop.height())
    w.show()

    #sys.exit(app.exec_())
    exit(app.exec_())

