# -*- coding: utf8 -*-
# Модели данных. Модели создаются с помощью SQL-запросов к БД
# Здесь же описываются делегаты, используемые в приложении
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QAbstractItemModel, Qt, QVariant, QModelIndex, QSortFilterProxyModel
from mysqlconnector import getAdminConnection, getConnection
from pymysql import IntegrityError
from PyQt5.QtWidgets import QComboBox, QMessageBox
from datetime import date
import re
from numberDialog import numberDialog
from Delegats import comboDelegate, comboBdDelegate, tableDelegate

class ModelAbonents(QAbstractItemModel):
    def __init__(self):
        self.namesColumn = []#('тип ТА', 'заводской №', 'цвет')
        self.content = []   # Список списков. Заполняется с помощью запроса.
        self.modifiedIndexes = [] # Список индексов, модифицированных, после очередного сохранения в базе данных
        self.deletedIndexes = [] # Список индексов, удаляемых записей
        self.savedFields = {} # Словарь содержит сохраняемые поля. Ключ - номер поля в `content`, значение - название поля в БД
        super().__init__()
        #self.connect = self.connectBD()

    @pyqtSlot()
    def resetData(self):
        if self.query:
            self.setQuery(self.query)

    def setQuery(self, strSQL):
        """ Метод принимает запрос к базе данных. Поле `content` заполняется результатами выполнения запроса.
        Поле `namesColumn` заполняется названиями полей запроса. Запрос записывается в поле `query`"""
        super().beginResetModel()
        self.query=strSQL;
        connect=getConnection()
        try:
            cursor=connect.cursor()
            cursor.execute(self.query)
        finally:
            connect.close()
        #print(self.query)
        # Заполнение списка названий колонок таблицы.
        # Определяется по значению параметра `as` из SQL-запроса
        self.namesColumn.clear()
        for i in range(len(cursor.description)):
            self.namesColumn.append(cursor.description[i][0])
        self.fillSavedFields(self.getNameMainTable())
        # Заполнения поля content экземпляра класса.
        self.content.clear()
        row=cursor.fetchone()
        while row is not None:
            list_value = list(row.values())
            result_value = []   # Список значений одной записи результатов запроса
            for result in list_value:
                if isinstance(result,date):  #  Если тип данных datetime, то преобразовать их в строку
                    result_value.append(str(result))
                else:
                    result_value.append(result)
            self.content.append(result_value)
            #self.content.append(list(row.values()))
            #print(self.content)
            row=cursor.fetchone()
        super().endResetModel()
            
    def getNameMainTable(self):
        """Метод анализирует строку запроса и определяет главную таблицу, название которое возвращается.
        Если поле `query` не заполнено возвращается пустая строка. Главная таблица определяется по имени
        таблицы непосредственно следующей за словом `From` запроса. После имени главное таблицы через 
        пробел должен следовать псевдоним и затем запятая, пробел или знак табуляции"""
        if not self.query:
            return ()
        else:
            modifyQuery = re.sub("\(SELECT.+\)","",self.query, flags=re.I)
            str_names = re.search("(?<=from)\s+\w+\s+\w+(?=[, \t])", modifyQuery, flags=re.I).group().lstrip().rstrip()
            name_table = tuple(str_names.split(" "))
            #print("name_table = ", name_table)
            return name_table

    def getFieldPrimaryKey(self):
        """Метод возвращает название поля первичного ключа главной таблицы. Определяется по имени первого 
        поля в запросе `query`"""
        if not self.query:
            return ""
        else:
            return re.search("(?<=\w\.).+?(?=as)", self.query).group().rstrip()

    def fillSavedFields(self, name_main_table):
        """Метод заполняет список, содержащий пары номер поля в `contents`:название поля"""
        self.savedFields = {}
        if not self.query:
            return 
        modifyQuery = re.sub("\(SELECT.+\)","i.result",self.query, flags=re.I)
        #print(f"modifyQuery={modifyQuery}")
        str_fields = re.search("(?<=select).+(?=from)", modifyQuery, flags=re.I).group().lstrip().rstrip()
        ind=0
        #print("list_fields=",list_fields)
        for s in re.findall("\w+\.\w+", str_fields):
            #print("field",ind,"=",s)
            pair_field = s.split('.')
            if pair_field[0]==name_main_table[1]:
                self.savedFields[ind] = pair_field[1]
                #results.append((ind, pair_field[1]))
            ind+=1
        #print(f"Сохраняемые поля:{self.savedFields}, ключи:{self.savedFields.keys()}")
        return 

    # Функции наследуемые из базового класса
    def flags(self, index):
        theFlags = super().flags(index)
        if index.column() == 0:
            theFlags = Qt.ItemIsEnabled
        else:
            if index.column() in self.savedFields.keys():
                theFlags = Qt.ItemIsEnabled|Qt.ItemIsEditable|Qt.ItemIsSelectable
            else:
                theFlags = Qt.ItemIsEnabled
        #print("model.flags() is work. theFlags={}. Column = {}".format(theFlags, index.column()))
        return theFlags
        
    def index(self, row, column, index):
        #print("model.index() is work, row={}, column={}".format(row, column))
        return super().createIndex(row, column)

    def data(self, index, role=Qt.DisplayRole):
        #import ipdb; ipdb.set_trace()
        if not index.isValid():
            return ""
        if (role == Qt.DisplayRole) or (role == Qt.EditRole):
            value = self.content[index.row()][index.column()]
            if not value:
                return ""
            if isinstance(value,tuple):
                #return "{}:{}".format(value[1],value[2])
                return(value[0])
            return value

    def parent(self, index):
        return QModelIndex()

    def rowCount(self, index):
        if index.isValid():
            return 0
        else:
            return len(self.content)

    def columnCount(self, index):
        if index.isValid():
            return 0
        else:
            return len(self.namesColumn)

    def headerData(self, section, orientation, role):
        if (orientation == Qt.Horizontal) and (role == Qt.DisplayRole):
            #print(self.namesColumn)
            return QVariant(self.namesColumn[section])
        if (orientation == Qt.Vertical) and (role == Qt.DisplayRole):
            return QVariant(section)

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        else:
            if role == Qt.EditRole:
                self.content[index.row()][index.column()] = value
                # Кроме запомининая данных в поле content, мы добавляем номер модифицированной строки в 
                # список модифицированных строк, чтобы потом обновить соответствующие записи в БД
                modifyIndex = index.row()#self.content[index.row()][0] # Идентификатор редактируемой записи
                if not(modifyIndex in self.modifiedIndexes):
                    self.modifiedIndexes.append(modifyIndex)
                # Посылаем сигнал, по которому обновится редактируемое поле в представлении
                self.dataChanged.emit(index, index)
                return True
            else:
                return False

    def insertRows(self, row, count, index):
        """Переопределенный метод, служит для изменения размера модели при вставке строк """
        super().beginInsertRows(QModelIndex(), row, row+count-1)
        for i in range(count):
            new_row=['',]
            for j in range(len(self.namesColumn) - 1):
                new_row.append('None')
            self.content.insert(row, new_row)
        super().endInsertRows()

    @pyqtSlot(list)
    def deleteRows(self, listSelect):
        """Слот удаляет выделенные записи. В качестве параметра получает список выделенных строк таблицы."""
        setDelete = set() # Множество удаляемых записей
        for i in listSelect:
            #print(f"Выбрранный ряд:{i.row()}")
            setDelete.add(str(self.content[i.row()][0]))
        #print(setDelete)
        if setDelete:
            deleteSQL = "DELETE FROM {} WHERE {} in ({})".format(self.getNameMainTable()[0], self.getFieldPrimaryKey(), ','.join(setDelete))
            print(deleteSQL)
            connect=getConnection()
            try:
                cursor=connect.cursor()
                cursor.execute(deleteSQL)
                connect.commit()
            finally:
                connect.close()
            self.resetData() 

    @pyqtSlot()
    def saveData(self):
        """Метод сохраняет содержимое модели в таблицу базы данных.
        для этого используется SQL-оператор, определяемый в переменной updateSQL """
        #print("modifiedIndexes={}".format(self.modifiedIndexes))
        updateSQL = "UPDATE {} SET {} WHERE {}"
        insertSQL = "INSERT {} SET {}"
        connect=getConnection()
        try:
            for record in self.modifiedIndexes:
                list_for_str = []
                name_main_table = self.getNameMainTable()
                for i in self.savedFields:#(self.fillSavedFields(name_main_table)[1:]):
                    value = self.content[record][i]#[0]]
                    if (value == None) or (value == 'None'):
                        #print(f"from saveData - {i}; value = {value}")
                        # Если подчиенная запись не выбрана, то соответствующее поле заполняем значением NULL
                        value = 'NULL'
                    elif isinstance(value, tuple):
                        # Если сохраняемые данные представляют собой tuple, значит это данные из подчиненной таблицы
                        # тогда сохраняем только первичный ключ записи подчиненной таблицы
                        value = value[0]
                    else:
                        value = "'{}'".format(value)
                    list_for_str.append("{} = {}".format(self.savedFields[i], value))
                    #list_for_str.append("{} = {}".format(i[1], value))
                if self.content[record][0]:
                    SQL=updateSQL.format(name_main_table[0], ", ".join(list_for_str), "{}={}".format(self.getFieldPrimaryKey(), self.content[record][0]))
                else:
                    SQL=insertSQL.format(name_main_table[0], ", ".join(list_for_str))
                print(SQL)
                cursor=connect.cursor()
                ignoreExec = False
                successExec = False # Переменная содержит результат выполнения SQL-запроса (успешно, неуспешно)
                while (not successExec) and (not ignoreExec):
                    try:
                        cursor.execute(SQL)
                    except IntegrityError as e:
                        print(e.args) 
                        resDialog=QMessageBox.critical(None, "Ошибка", f"Ошибка\n{e.args}",QMessageBox.Retry|QMessageBox.Ignore)
                        print(f"resDialog = {resDialog}")
                        if resDialog == QMessageBox.Ignore:
                            ignoreExec = True
                    else:
                        successExec = True
            connect.commit()
        finally:
            connect.close()
        self.modifiedIndexes.clear()

    def sort(self, column, order):
        print(f"From sort(), column = {column}, order = {order}")
        
class SortedProxyModel(QSortFilterProxyModel):
    def __init__(self):
        print("constructor ProxyModel")
        self.dict_ordering = {}
        self.dict_filtering = {} # Словарь для фильтрации. Ключ-название поля таблицы, значение-параметр фильтрации 
        super().__init__()
        #savedFields = sourceModel().savedFields

    def sort(self, column, order):
        #print(f"From {self.sender()} sort(), column = {column}, order = {order}")
        self.dict_ordering[column] = int(not self.dict_ordering.get(column)) if column in self.dict_ordering else Qt.AscendingOrder
        super().sort(column, self.dict_ordering[column])

    @pyqtSlot(str)
    def changeParametrsFiltrering(self, value_filter):
        """Слот вызывается, когда изменяется содержимое соответствующего
        элемента управления. При этом вызывается защищенная функция
        invalidateFilter()"""
        #print(f"key={self.sender().objectName()}; value={value_filter}")
        self.dict_filtering[int(self.sender().objectName())]=value_filter
        print(self.dict_filtering)
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        if bool(self.dict_filtering):
            for i in range(len(self.sourceModel().namesColumn)):
                #print(f"filterAcceptRow.column={i}")
                if bool(self.dict_filtering.get(i)):
                    index = self.sourceModel().index(sourceRow, i, sourceParent)
                    #print(f"{self.dict_filtering[i]};{self.sourceModel().data(index)}")
                    try:
                        if not (self.dict_filtering[i] in str(self.sourceModel().data(index))):
                            return False
                    except:
                        print(f"{self.dict_filtering[i]};{self.sourceModel().data(index)}")
        #if O
        return True;

class simpleTableModel(QAbstractItemModel):
    def __init__(self, strSQL):
        super().__init__()
        #self.bdConnect = getConnection()
        
