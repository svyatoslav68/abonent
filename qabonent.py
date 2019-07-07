#!/usr/bin/env python3
# -*- coding: utf8 -*-
# Приложение для работы со списками телефонов, номеров и тому подобное
from sys import argv, exit
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit,QVBoxLayout, QHBoxLayout, QCheckBox, QSpinBox
from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QMessageBox, QItemDelegate, QStyledItemDelegate, QDialog
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot, QSettings
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QModelIndex
from MyWidgets import PhonesTableView
from Models import ModelAbonents
from Delegats import comboDelegate, comboBdDelegate, tableDelegate,functionViewTableEditDelegate
from numberDialog import numberDialog
from dialognewrecord import newRecordDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.abonentModel = ModelAbonents()
        self.abonentModel.setObjectName("abonentModel")
        self.phonesModel = ModelAbonents()
        self.phonesModel.setObjectName("phonesModel")
        self.initUI()

    def createActions(self):
        self.actionViewSaveSettings = QAction("Сохранить настройки")
        self.actionViewSaveSettings.triggered.connect(self.slotSaveSettings)
        self.actionViewGetDefault = QAction("Сбросить настройки")
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
        self.actionAddRecord=QAction("Добавить запись")
        self.actionAddRecord.triggered.connect(self.addRecord)
        self.actionDeleteRecord=QAction("Удалить запись")
        self.actionDeleteRecord.triggered.connect(self.deleteRecord)
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
        viewMenu=appMenu.addMenu("&Вид")
        viewMenu.addAction(self.actionViewSaveSettings)
        viewMenu.addAction(self.actionViewGetDefault)
        #appMenu.addMenu(fileMenu)
        dataMenu=appMenu.addMenu("&Данные")
        dataMenu.addAction(self.actionNumbers)
        dataMenu.addAction(self.actionAbonents)
        dataMenu.addAction(self.actionRooms)
        dataMenu.addAction(self.actionSelectNumber)
        tableMenu=appMenu.addMenu("&Таблица")
        tableMenu.addAction(self.actionAddRecord)
        tableMenu.addAction(self.actionDeleteRecord)
        tableMenu.addSeparator()
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
        desktop = QApplication.desktop()
        self.createWidgets()
        settings = QSettings("abonent.ini", QSettings.IniFormat)
        settings.beginGroup("MainWindow")
        self.setGeometry(int(settings.value("window_x", 0)), int(settings.value("window_y", 0)), int(settings.value("window_width",desktop.width())), int(settings.value("window_height", desktop.height())))
        settings.endGroup()
        self.createActions()
        self.createMenu()
        super().setWindowTitle("Справочник по телефонным аппаратам")

    def setTableSizing(self, nameTable):
        settings = QSettings("abonent.ini", QSettings.IniFormat)
        nameSection = "tab_{}".format(nameTable)
        settings.beginGroup(nameSection)
        #print(f"nameGroup={nameSection}")
        for i in range(len(self.mainTable.model().namesColumn)):
            self.mainTable.setColumnWidth(i, int(settings.value(str(i), 100)))
        settings.endGroup()

    def showNumbers(self):
        """Функция выводит информацию о номерах в главном окне приложения.
        Для QTableView устанавливаются делегаты по умолчанию"""
        SQL="SELECT n.id_number as `Код`, n.name_net as `Сеть`, n.number as `Номер`, IFNULL(p.product_number, '') as `абонентская установка`, IFNULL(t.name_type, '') as `Тип`, n.port_number as `Номер порта`, n.permit as `Указание`  FROM numbers n LEFT JOIN phones p  ON n.id_number = p.cod_number LEFT JOIN types_TA t ON t.id = p.cod_type_TA"
        self.phonesModel.setQuery(SQL)
        self.mainTable.setModel(self.phonesModel)
        self.setTableSizing(self.phonesModel.getNameMainTable()[0])
        threedelegate = QStyledItemDelegate(self)
        self.mainTable.setItemDelegateForColumn(3, threedelegate)
        fivedelegate = QStyledItemDelegate(self)
        self.mainTable.setItemDelegateForColumn(5, fivedelegate)
        sixdelegate = QStyledItemDelegate(self)
        self.mainTable.setItemDelegateForColumn(6, sixdelegate)
        self.actionUpdate.triggered.connect(self.phonesModel.resetData)
        self.actionSaveData.triggered.connect(self.phonesModel.saveData)

    def showAbonents(self):
        SQL="SELECT p.id_phone as `Код`, p.product_number as 'Зав. №', p.inv_number as 'Инв. №', p.cod_type_TA as 'Код типа', p.date_issue as 'Дата выпуска', p.state as 'Состояние', IFNULL(p.cod_number, 'None') as 'Код номера', n.name_net as 'Сеть', n.number as 'Номер' from phones p LEFT JOIN types_TA t ON p.cod_type_TA = t.id LEFT JOIN numbers n ON p.cod_number = n.id_number"
        self.mainTable.setModel(self.abonentModel)
        self.abonentModel.setQuery(SQL)
        self.setTableSizing(self.abonentModel.getNameMainTable()[0])
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

    @pyqtSlot()
    def addRecord(self):
        self.mainTable.model().insertRows(self.mainTable.currentIndex().row(),1,QModelIndex())
        #dialogNewRecord = newRecordDialog(self)
        #if dialogNewRecord.exec() == QDialog.Accepted:
        #    insertSQL = "INSERT into {} SET {}"
        #    print(insertSQL)

    @pyqtSlot()
    def deleteRecord(self):
        deleteSQL = "DELETE FROM {} WHERE {} = {}"
        QMessageBox.warning(self, "Запрос для удаления записи", deleteSQL, QMessageBox.Ok)

    @pyqtSlot()
    def slotSaveSettings(self):
        """Сохранение настроек приложения"""
        settings = QSettings("abonent.ini", QSettings.IniFormat)
        settings.beginGroup("MainWindow")
        settings.setValue("window_height", self.height())
        settings.setValue("window_width", self.width())
        settings.setValue("window_x", self.geometry().x())
        settings.setValue("window_y", self.geometry().y())
        settings.endGroup()
        if self.mainTable.model():
            nameSection = "tab_{}".format(self.mainTable.model().getNameMainTable()[0])
            settings.beginGroup(nameSection)
            #print(nameSection)
            for i in range(len(self.mainTable.model().namesColumn)):
                print("i-й столбец; ширина = {}".format(self.mainTable.columnWidth(i)))
                settings.setValue(str(i), format(self.mainTable.columnWidth(i)))
            settings.endGroup()

if __name__ == '__main__':
    #app = QApplication(sys.argv)
    app = QApplication(argv)

    w = MainWindow()
    #w.move(0,0)
    #w.resize(desktop.width(), desktop.height())
    w.show()

    #sys.exit(app.exec_())
    exit(app.exec_())

