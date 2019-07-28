#!/usr/bin/env python3
# -*- coding: utf8 -*-
# Приложение для работы со списками телефонов, номеров и тому подобное
from sys import argv, exit
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit,QVBoxLayout, QHBoxLayout, QCheckBox, QSpinBox
from PyQt5.QtWidgets import QMainWindow, QMenu, QAction, QMessageBox, QItemDelegate, QStyledItemDelegate, QDialog
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot, QSettings, QSortFilterProxyModel
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QModelIndex
from MyWidgets import PhonesTableView, TableWithFiltres
from Models import ModelAbonents, SortedProxyModel
from Delegats import comboDelegate, comboBdDelegate, tableDelegate, functionViewTableEditDelegate
from numberDialog import numberDialog
from dialognewrecord import newRecordDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.abonentModel = ModelAbonents()
        self.abonentModel.setObjectName("abonentModel")
        self.proxyAbonentModel = SortedProxyModel()
        self.proxyAbonentModel.setObjectName("proxyAbonentModel")
        self.proxyAbonentModel.setSourceModel(self.abonentModel)
        self.phonesModel = ModelAbonents()
        self.phonesModel.setObjectName("phonesModel")
        self.roomsModel = ModelAbonents()
        self.roomsModel.setObjectName("roomsModel")
        self.initUI()

    def createActions(self):
        self.actionViewSaveSettings = QAction("Сохранить настройки")
        self.actionViewSaveSettings.triggered.connect(self.slotSaveSettings)
        self.actionViewGetDefault = QAction("Сбросить настройки")
        self.actionViewFilterTab = QAction("Панель фильтрации")
        self.actionViewFilterTab.setShortcut("Ctrl+F")
        self.actionViewFilterTab.setCheckable(True)
        self.actionViewFilterTab.triggered.connect(self.mainTable.hideFilterPanel)
        self.actionExit=QAction("Выход") 
        self.actionExit.triggered.connect(QCoreApplication.instance().quit)
        self.actionNumbers=QAction("Номера")
        self.actionNumbers.setShortcut("Ctrl+N")
        self.actionNumbers.triggered.connect(self.showNumbers)
        self.actionAbonents=QAction("Телефоны")
        self.actionAbonents.setShortcut("Ctrl+T")
        self.actionAbonents.triggered.connect(self.showAbonents)
        self.actionUpdate=QAction("Обновить")
        self.actionUpdate.setShortcut("Ctrl+R")
        #self.actionSelectNumber=QAction("Выбор номера")
        #self.actionSelectNumber.triggered.connect(self.selectNumber)
        self.actionRooms=QAction("Помещения")
        self.actionRooms.setShortcut("Ctrl+P")
        self.actionRooms.triggered.connect(self.showRooms)
        self.actionAddRecord=QAction("Добавить запись")
        self.actionAddRecord.setShortcut("Ctrl+A")
        self.actionAddRecord.triggered.connect(self.addRecord)
        self.actionDeleteRecords=QAction("Удалить записи")
        self.actionDeleteRecords.setObjectName("actionDeleteRecords")
        self.actionDeleteRecords.setShortcut("Ctrl+D")
        #self.actionDeleteRecords.triggered.connect(self.deleteRecord)
        self.actionSaveData=QAction("Сохранить")
        self.actionSaveData.setShortcut("Ctrl+S")
        self.actionLoadData=QAction("Загрузить")
        self.actionLoadData.setShortcut("Ctrl+L")
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
        viewMenu.addSeparator()
        viewMenu.addAction(self.actionViewFilterTab)
        #appMenu.addMenu(fileMenu)
        dataMenu=appMenu.addMenu("&Данные")
        dataMenu.addAction(self.actionNumbers)
        dataMenu.addAction(self.actionAbonents)
        dataMenu.addAction(self.actionRooms)
        #dataMenu.addAction(self.actionSelectNumber)
        tableMenu=appMenu.addMenu("&Таблица")
        tableMenu.addAction(self.actionAddRecord)
        tableMenu.addAction(self.actionDeleteRecords)
        tableMenu.addSeparator()
        tableMenu.addAction(self.actionLoadData)
        tableMenu.addAction(self.actionSaveData)
        tableMenu.addAction(self.actionUpdate)
        helpMenu=appMenu.addMenu("&Помощь")
        helpMenu.addAction(self.actionHelpAbout)
        helpMenu.addAction(self.actionHelpAboutQt)
        #appMenu.addMenu(helpMenu)
        
    def createWidgets(self):
        #self.mainTable = PhonesTableView()
        self.mainTable = TableWithFiltres()
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

    def showNumbers(self):
        """Функция выводит информацию о номерах в главном окне приложения.
        Для QTableView устанавливаются делегаты по умолчанию"""
        SQL="SELECT n.id_number as `Код`, n.name_net as `Сеть`, n.number as `Номер`, IFNULL((SELECT GROUP_CONCAT(CONCAT(tta.name_type, ' №', ph.product_number)) FROM phones ph, types_TA tta WHERE n.id_number = ph.cod_number AND tta.id = ph.cod_type_TA GROUP BY ph.cod_number),'')  as `абонентская установка`, n.port_number as `Номер порта`, n.permit as `Указание`  FROM numbers n LEFT JOIN phones p  ON n.id_number = p.cod_number LEFT JOIN types_TA t ON t.id = p.cod_type_TA"
        #SQL="SELECT n.id_number as `Код`, n.name_net as `Сеть`, n.number as `Номер`, IFNULL(p.product_number, '') as `абонентская установка`, IFNULL(t.name_type, '') as `Тип`, n.port_number as `Номер порта`, n.permit as `Указание`  FROM numbers n LEFT JOIN phones p  ON n.id_number = p.cod_number LEFT JOIN types_TA t ON t.id = p.cod_type_TA"
        self.phonesModel.setQuery(SQL)
        self.mainTable.setModel(self.phonesModel)
        self.mainTable.createWidgetsFiltres()
        self.actionUpdate.triggered.connect(self.phonesModel.resetData)
        self.actionSaveData.triggered.connect(self.phonesModel.saveData)
        self.actionDeleteRecords.triggered.connect(lambda:self.phonesModel.deleteRows(self.mainTable.selectedIndexes()))

    def showAbonents(self):
        SQL="SELECT p.id_phone as `Код`, p.product_number as 'Зав. №', p.inv_number as 'Инв. №', p.cod_type_TA as 'Код типа', p.date_issue as 'Дата выпуска', p.state as 'Состояние', IFNULL(p.cod_number, 'None') as 'Код номера', n.name_net as 'Сеть', n.number as 'Номер', p.cod_room as 'Помещение' from phones p LEFT JOIN types_TA t ON p.cod_type_TA = t.id LEFT JOIN numbers n ON p.cod_number = n.id_number LEFT JOIN rooms r ON p.cod_room = r.id_room ORDER BY p.cod_type_TA"
        self.abonentModel.setQuery(SQL)
        #self.mainTable.setModel(self.abonentModel)
        self.mainTable.setModel(self.proxyAbonentModel)
        self.mainTable.createWidgetsFiltres()
        self.actionUpdate.triggered.connect(self.mainTable.model().sourceModel().resetData)
        #typeDelegate = comboBdDelegate(self,'types_TA', 'name_type')
        #self.mainTable.setItemDelegateForColumn(3, typeDelegate)
        #stateDelegate = comboBdDelegate(self,'phone_status', 'name_status')
        #self.mainTable.setItemDelegateForColumn(5, stateDelegate)
        self.actionSaveData.triggered.connect(self.abonentModel.saveData)
        #tabDelegate = functionViewTableEditDelegate(self, 'numbers', lambda row:row['name_net']+':'+row['number'])
        #self.mainTable.setItemDelegateForColumn(6, tabDelegate)
        self.actionDeleteRecords.triggered.connect(lambda:self.abonentModel.deleteRows(self.mainTable.selectedIndexes()))

    def showRooms(self):
        #SQL="SELECT r.id_room as `Код`, r.num_room as `№ пом`, r.cod_parent as parent, (SELECT address FROM rooms WHERE id_room = parent) as `Объект`, r.floor as `Этаж` FROM rooms r WHERE r.cod_parent > -1 ORDER BY level"
        #SQL="SELECT r.id_room as `Код`, r.num_room as `№ пом`, r.cod_parent as `Объект`, r.floor as `Этаж` FROM rooms r WHERE r.cod_parent > -1 ORDER BY level"
        SQL="SELECT r.id_room as `Код`, r.num_room as `№ пом.`, r.cod_parent as `Объект`, r.floor as `Этаж`,  COUNT(p.id_phone) as `Количество`, GROUP_CONCAT(n.number) as `Номера` from rooms r LEFT JOIN phones p ON r.id_room = p.cod_room LEFT JOIN numbers n ON p.cod_number=n.id_number WHERE r.cod_parent > 0 GROUP BY(r.num_room)"
        self.roomsModel.setQuery(SQL)
        self.mainTable.setModel(self.roomsModel)
        self.mainTable.createWidgetsFiltres()
        self.actionUpdate.triggered.connect(self.roomsModel.resetData)
        self.actionSaveData.triggered.connect(self.roomsModel.saveData)
        self.actionDeleteRecords.triggered.connect(lambda:self.roomsModel.deleteRows(self.mainTable.selectedIndexes()))

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
        if self.mainTable.model():
            if self.mainTable.currentIndex().row() > 0:
                #print(self.mainTable.currentIndex().row())
                self.mainTable.model().insertRows(self.mainTable.currentIndex().row(),1,QModelIndex())

    @pyqtSlot()
    def deleteRecord(self):
        listSelect = self.mainTable.selectedIndexes()
        setDelete = set() # Множество удаляемых записей
        for i in listSelect:
            #print(f"Выбрранный ряд:{i.row()}")
            setDelete.add(self.mainTable.model().content[i.row()][0])
        #print(setDelete)
        deleteSQL = "DELETE FROM {} WHERE {} in {}".format(' '.join(self.mainTable.model().getNameMainTable()), self.mainTable.model().getFieldPrimaryKey(), tuple(setDelete))
        #if QMessageBox.warning(self, "Запрос для удаления записи", deleteSQL, QMessageBox.Ok) == QMessageBox.Ok:


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
        if isinstance(self.mainTable.model(), ModelAbonents):
            innerModel = self.mainTable.model()
        elif isinstance(self.mainTable.model(), QSortFilterProxyModel):
            innerModel = self.mainTable.model().sourceModel()
        if innerModel:
            nameSection = "tab_{}".format(innerModel.getNameMainTable()[0])
            settings.beginGroup(nameSection)
            #print(nameSection)
            for i in range(len(innerModel.namesColumn)):
                #print("i-й столбец; ширина = {}".format(self.mainTable.columnWidth(i)))
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

