#!/usr/bin/env python3
# -*- coding: utf8 -*-
from PyQt5.QtWidgets import QAbstractItemDelegate, QStyledItemDelegate 
from PyQt5.QtWidgets import QComboBox, QMessageBox
from mysqlconnector import getAdminConnection, getConnection
from PyQt5.QtCore import Qt
from numberDialog import numberDialog

class comboDelegate(QStyledItemDelegate):
    def __init__(self,parent):
        self.content={}
        print("comboDelegate is created")
        super().__init__(parent)

    def fillContent(self, query):
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        while row is not None:
            self.content[row['id']]=row['value']
            row = cursor.fetchone()
        connection.close()

    def paint(self, painter, option, index):
        #print("Ячейка {0}.{1}:{2}".format(index.row(), index.column(), type(index.data())))
        #print("comboDelegate paint()")
        painter.save()
        #model = index.model()
        painter.drawText(option.rect, Qt.AlignCenter, index.data())
        painter.restore()

    def createEditor(self, parent, option, index):
        widgetEditor = QComboBox(parent)
        widgetEditor.addItems(self.content.values())
        print("Editor for delegate is created")
        return widgetEditor

    def setModelData(self, editor, model, index):
        pass
        #model.setData(index, 

    def setEditorData(self, editor, index):
        print("setEditorData run")
        #text=index.model().data(index, Qt.EditRole)#.toString()
        #index.model().setChangedData(True)
        if index.model().data(index, Qt.DisplayRole):
            editor.setCurrentIndex(list(self.content.keys()).index(index.model().data(index.sibling(index.row(),index.column()+1), Qt.DisplayRole)))
        #editor.setCurrentIndex(list(self.content.keys()).index(index.sibling(index.row(),index.column()+1), Qt.DisplayRole))

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class comboBdDelegate(QAbstractItemDelegate):
    """Делегат будет использоваться для работы с внешними ключами таблицы. 
    В конструктор передается название таблицы и название поля значения"""
    def __init__(self, parent, name_table, name_field):
        self.content = {} # Словарь имеет ключом первичный ключ подчиненной таблицы, а значением передаваемое в конструкторе поле таблицы
        super().__init__(parent)
        #print("relationDelegate is created")
        self.tb_name = name_table
        self.fd_name = name_field
        self.fill_content()
        #print(self.content)

    def fill_content(self):
        self.content.clear()
        self.content[0]='-----'
        con = getConnection()
        strSQL = "SELECT * FROM {}".format(self.tb_name)
        cursor = con.cursor()
        result = 0
        try:
            cursor.execute(strSQL)
            row = cursor.fetchone()
            while row is not None:
                result += 1
                self.content[row[list(row.keys())[0]]] = row[self.fd_name]
                row = cursor.fetchone()
        except:
            QMessageBox.critical(None, "Сообщение об ошибке", "Ошибка при выполнении запроса\n{}".format(strSQL))
        con.close()
        #print(self.content)
        return result

    def paint(self, painter, option, index):
        #print("relationDelegate paint()\nrow={}, column={}, data = {}".format(index.row(), index.column(), str(index.data())))
        #import ipdb; ipdb.set_trace()
        painter.save()
        #print("Ячейка {0}.{1}-Тип:{2},Данные:{3}".format(index.row(), index.column(), type(index.data()), index.data()))
        if index.data():
            pass
            #model = index.model()
            try:
                painter.drawText(option.rect, Qt.AlignCenter, self.content[int(index.data())])
            except:
               print("Error from relationDelegate.paint.",index.data())
        painter.restore()

    def createEditor(self, parent, option, index):
        widgetEditor = QComboBox(parent)
        widgetEditor.addItems(self.content.values())
        #print("Editor for delegate is created")
        return widgetEditor

    def setEditorData(self, editor, index):
        #print("setEditorData for relationDelegate")
        if index.model().data(index, Qt.DisplayRole):
            editor.setCurrentIndex(list(self.content.keys()).index(int(index.model().data(index, Qt.DisplayRole))))
        #editor.setCurrentIndex(list(self.content.keys()).index(index.model().data(index, Qt.DisplayRole)))

    def setModelData(self, editor, model, index):
        data = list(self.content.keys())[editor.currentIndex()]
        #if data:
        model.setData(index, data, Qt.EditRole)
        #strSQL = "UPDATE {'table'} SET 
        #print(data)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)
    
class tableDelegate(QAbstractItemDelegate):
    """Делегат для редактирования и отображения данных из подчиненной таблицы. При этом 
    данные выбираются с помощью таблицы и элементов управления, с помощью которых 
    осуществляется фильтрация данных в таблице.
    В качестве данных (data) из модели получаем кортеж, содержащий всю строку подчиенной таблицы.
    для отображения данных используется функция от этой строки-function_draw."""
    def __init__(self, parent):
        self.result = -1, "None", "None"
        super().__init__(parent)

    def setSlaveTable(self, name_table):
        """ Установка названия подчиненной таблицы. Кроме того определяется названия поля, 
        являющегося первичным ключом подчиненной таблицы"""
        indexSQL = 'SHOW INDEX FROM {} WHERE Key_name="PRIMARY"'.format(name_table)
        connect = getConnection()
        cursor = connect.cursor()
        cursor.execute(indexSQL)
        row=cursor.fetchone()
        self.slave_index = row['Column_name']
        #selectSQL = "SELECT * from {} WHERE {} = {}".format(name_table, name_key, key)
        #print(selectSQL)

    def createEditor(self, parent, option, index):
        #super().createEditor(parent, option, index)
        listFlters = []
        listFlters.append(dict(name_field='name_net', alias="Сеть", widget='QComboBox', condition = 'eq', SqlFill = "SELECT DISTINCT name_net FROM numbers") )
        listFlters.append(dict(name_field='number', alias="Номер", widget='QLineEdit', condition = 'like', SqlFill = "")) 
        formEditor = numberDialog(self.parent(), listFlters)
        formEditor.setNameTable("numbers")
        formEditor.signalEndEdit.connect(self.closeAndCommitEditor)
        return formEditor
        
    def setModelData(self, editor, model, index):
        """Сохраняться должен список из 3-х значений. Первое значение обозначает идентификатор 
        записи в подчиненной таблице. Второе значение - отображаемое в таблице значение. """
        #print("run setModelData(); currentIndex = {}".format(editor.mainTable.currentRow()))
        #print("from setModelData. Index = {}".format(editor.mainTable.currentRow()))
        indexOfEditor = editor.tableQuery.currentRow()
        if indexOfEditor == -1:
            self.result = ()
        else:
            self.result = editor.tableQuery.item(indexOfEditor,0).text()
            #self.result = editor.mainTable.item(indexOfEditor,0).text(),editor.mainTable.item(indexOfEditor,1).text(),editor.mainTable.item(indexOfEditor,2).text()
        model.setData(index, self.result, Qt.EditRole)
        
    def closeAndCommitEditor(self):
        formEditor = self.sender()
        print("closeAndCommitEditor")
        self.commitData.emit(formEditor)
        self.closeEditor.emit(formEditor)

    def setEditorData(self, editor, index):
        pass 

    def paint(self, painter, option, index):
        painter.save()
        if index.data():
            painter.drawText(option.rect, Qt.AlignCenter, str(index.data()))
        painter.restore()

    def updateEditorGeometry(self, editor, option, index):
        """Размер прямоугольника должен быть чуть меньше, чем размер отображения"""
        #print("type of self of delegate:{}".format(type(self)))
        editor.setGeometry(300, 300, 500, 300)#option.rect)

class functionViewTableEditDelegate(tableDelegate):
    """Делегат для отображения и редактирования столбца таблицы, который содержит
    поле для связи с подчиненной таблицей. Отображение производится с помощью функции, 
    передаваемой в конструктор делегата. Редактирование производится с помощью 
    диалового окна, в котором отображаетс подчиненная таблица. """
    def __init__(self, parent, name_table, function_view):
        """ В конструктор передаются имя подчиенной таблицы и функция над 
        связанной записью в подчиненной таблице"""
        self._function_view = function_view
        self._name_slave_table = name_table
        indexSQL = 'SHOW INDEX FROM {} WHERE Key_name="PRIMARY"'.format(name_table)
        connect = getConnection()
        cursor = connect.cursor()
        cursor.execute(indexSQL)
        row=cursor.fetchone()
        slave_index = row['Column_name']
        connect.close()
        self._SqlSelectSlaveRecord = "SELECT * FROM {} WHERE {} = {{}}".format(self._name_slave_table, slave_index) 
        super().__init__(parent)

    def paint(self, painter, option, index):
        painter.save()
        if index.data():
            SqlSelect = self._SqlSelectSlaveRecord.format(index.data())
            connect = getConnection()
            cursor = connect.cursor()
            cursor.execute(SqlSelect)
            row = cursor.fetchone()
            connect.close()
            painter.drawText(option.rect, Qt.AlignCenter, str(self._function_view(row)))
        painter.restore()

