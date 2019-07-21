# -*- coding: utf8 -*-
#Модуль диалогового окна вывода содержимого подчиненной таблицы
from PyQt5.QtWidgets import QDialog, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit, QComboBox
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView 
from mysqlconnector import getAdminConnection, getConnection
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSlot, pyqtSignal
import re

class numberDialog(QDialog):
    """Класс предназначен для отображения диалога с подчиненной таблицей. Диалог используется в качестве
    редактора делегата для связанных внешним ключем полей. Диалог содержит панель фильтрации для быстрого 
    поиска нужной строки. Данные в таблице заполняются результатами запроса к БД, который можнет передаваться
    явно или запрос формируется выбором всех полей переданной соответствующим методом имени таблицы"""
    signalEndEdit = pyqtSignal()
    def __init__(self, parent, listFilters):
        self.fieldFilters = [] # Список кортежей, описывающей поля запроса, используемые для фильтрации содержимого таблицы
        #print(listFilters)
        for itemFilter in listFilters:
            #print(itemFilter)
            self.addFieldFilter(itemFilter)
        #self.filters = {}    # Поле содержит словарь, который используется для фильтрации содержимого таблицы
        super().__init__(parent)
        self.setWindowTitle("Содержимое подчиненной таблицы")
        self.initUi()

    def addFieldFilter(self, args):
        """В словаре args содержится описание добавляемых фильтров.
        name_field - название поля по которому будет проводиться фильтрация, добавляется в SQL-запрос после WHERE;
        alias - псевдоним поля, его будет содержать метка перед соответствующим виджетом в панели фильтрации;
        widget - название виджета из библиотеки Qt (может быть QLineEdit или QComboBox);
        condition - условие, соотвествие которому будет условием для фильтрации записей;
        SqlFill - запрос, результатами которого заполняется выпадающий список QComboBox"""
        self.fieldFilters.append((args['name_field'], args['alias'], args['widget'], args['condition'], args['SqlFill']))
        #print(self.fieldFilters)

    def setNameTable(self, name_table):
        self._name_table = name_table
        self.setWindowTitle("Содержимое таблицы {}".format(name_table))
        self.setQuery("SELECT * FROM `{}`".format(name_table))

    def setQuery(self, query):
        """Заголовки таблицы будут содержать имена полей запроса или их псевдонимы """
        self.query = query
        self.tableQuery.clear()
        connect = getConnection()      
        try:
            cursor=connect.cursor()
            numberRows = cursor.execute(self.query)
            descQuery = cursor.description # Здесь сохраняем описание полей запроса
            numberCols = len(descQuery)
            self.tableQuery.setRowCount(numberRows)
            self.tableQuery.setColumnCount(numberCols)
            content = cursor.fetchall()
            for i in range(len(content)):
                for j in range(len(content[i])):
                    self.tableQuery.setItem(i,j,QTableWidgetItem(str(list(content[i].values())[j])))
            self.tableQuery.setHorizontalHeaderLabels([field[0] for field in descQuery])
        finally:
            connect.close()

    def createTable(self):
        connect = getConnection()      
        self.query = "SELECT id_number, name_net, number FROM numbers" 
        tableQuery = QTableWidget()
        try:
            cursor=connect.cursor()
            numberRows = cursor.execute(self.query)
            tableQuery.setRowCount(numberRows)
            tableQuery.setColumnCount(3)
            content = cursor.fetchall()
            for i in range(len(content)):
                for j in range(len(content[i])):
                    #print(content[i][j])
                    tableQuery.setItem(i,j,QTableWidgetItem(str(list(content[i].values())[j])))
            tableQuery.setHorizontalHeaderLabels(("№", "Сеть", "Номер"))
        finally:
            connect.close()
        return tableQuery

    def createFilterWidgets(self, layout):
        """Создание виджетов панели фильтрации. Виджеты создаются на основе содержимого fieldFilters"""
        if not self.fieldFilters:
            return
        #listLabels = []
        self.listWidgets = []
        for itemFilter in self.fieldFilters:
            print(itemFilter)
            layout.addWidget(QLabel(itemFilter[1]))
            if itemFilter[2] == "QComboBox":
                comboBox = QComboBox()
                comboBox.setObjectName("comboBox_"+itemFilter[0])
                comboBox.addItem('')
                self.listWidgets.append(comboBox)
                layout.addWidget(comboBox)
                connect = getConnection()      
                try:
                    cursor=connect.cursor()
                    cursor.execute(itemFilter[4])
                    result_row = cursor.fetchone()
                    #print("result_row = ", result_row)
                    while result_row is not None:
                        comboBox.addItem(list(result_row.values())[0])
                        result_row = cursor.fetchone()
                finally:
                    connect.close()
                comboBox.currentIndexChanged.connect(self.setFilter)#lambda:self.setFilter(comboBox.currentText()))
            elif itemFilter[2] == 'QLineEdit':
                lineEdit = QLineEdit()
                lineEdit.setObjectName("lineEdit_"+itemFilter[0])
                layout.addWidget(lineEdit)
                lineEdit.editingFinished.connect(self.setFilter)#lambda:self.setFilter(lineEdit.text()))
                self.listWidgets.append(lineEdit)
            elif itemFilter[2] == 'value':
                self.listWidgets.append(str(itemFilter[4]))
        return

    def initUi(self):
        self.buCancel = QPushButton("Отмена")
        self.buCancel.clicked.connect(self.buttonSlot)
        self.buCancel.clicked.connect(self.reject)
        self.buOk = QPushButton("Ok")
        self.buOk.clicked.connect(self.buttonSlot)
        self.buOk.clicked.connect(self.accept)
        filtersLayout = QHBoxLayout()
        self.createFilterWidgets(filtersLayout)
        #laNet = QLabel("Сеть:")
        #self.cbNet = QComboBox()
        #self.cbNet.addItem('')
        #connect = getConnection()      
        #try:
        #    cursor=connect.cursor()
        #    cursor.execute("SELECT DISTINCT name_net from numbers")
        #    result_row = cursor.fetchone()
        #    while result_row is not None:
        #        self.cbNet.addItem(result_row['name_net'])
        #        result_row = cursor.fetchone()
        #finally:
        #    connect.close()
        #self.cbNet.currentIndexChanged.connect(self.changedNet)
        #laNumber = QLabel("Номер:")
        #self.leNumber = QLineEdit()
        #self.leNumber.editingFinished.connect(self.changeNumber)
        #filtersLayout.addWidget(laNet)
        #filtersLayout.addWidget(self.cbNet)
        #filtersLayout.addWidget(laNumber)
        #filtersLayout.addWidget(self.leNumber)
        bottomLayout = QHBoxLayout()
        bottomLayout.addStretch()
        bottomLayout.addWidget(self.buCancel)
        bottomLayout.addWidget(self.buOk)
        mainLayout = QVBoxLayout()
        #self.mainTable = self.createTable()
        self.tableQuery = QTableWidget()
        self.tableQuery.setSelectionBehavior(QAbstractItemView.SelectRows)
        mainLayout.addLayout(filtersLayout)
        mainLayout.addWidget(self.tableQuery)
        mainLayout.addLayout(bottomLayout)
        self.setLayout(mainLayout)
        
    @pyqtSlot()
    def buttonSlot(self):
        print("exec buttonSlot()")
        self.signalEndEdit.emit()

    @pyqtSlot()#tuple, str)
    def setFilter(self):#, tuple_filter, text):
        """Слот связан с сигналами от виджетов панели фильтрации.
        Из содержимого словаря filters создается предложение с ключевым словом WHERE,
        которое добавляется к запросу. Условия соединяются оператором 'AND'."""
        #print("from {} received {},{}".format(self.sender().objectName(), text, tuple_filter))
        WhereSQL = ''
        dict_conditions = {"eq": '="{}"',"ne": '<>"{}"',"like": 'like "%{}%"'}
        "Вырежем из SQL-запроса все, что после `WHERE`"
        query = re.split('where', self.query, flags=re.IGNORECASE)[0].rstrip()
        listArgs=[]
        for (filter, widget) in zip(self.fieldFilters, self.listWidgets):
            if filter[2] == 'QLineEdit':
                filter_value = widget.text()
            if filter[2] == 'QComboBox':
                filter_value = widget.currentText()
            #if filter[2] == 'value':
            #    filter_value = 
            if filter_value:
                condition = "{} {}".format(filter[0], dict_conditions[filter[3]].format(filter_value))
                listArgs.append(condition)
        if listArgs:
            WhereSQL = ' WHERE {}'.format(' AND '.join(listArgs))
            query += WhereSQL
        print(query)
        self.setQuery(query)
        #return result

