#!/usr/bin/env python3
# -*- coding: utf8 -*-
from PyQt5.QtWidgets import QAbstractItemDelegate, QStyledItemDelegate , QItemDelegate
from PyQt5.QtWidgets import QComboBox, QMessageBox
from PyQt5.QtGui import QPalette
from mysqlconnector import getAdminConnection, getConnection
from PyQt5.QtCore import Qt, QSize, QRect, QRectF
from numberDialog import numberDialog
import re

class defaultDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.model().data(index, Qt.EditRole) == 'None':
            pass
        else:
            super().paint(painter, option, index)

    def setEditorData(self, editor, index):
        if index.model().data(index, Qt.EditRole) == 'None':
            editor.setText("") 
        else:
            super().setEditorData(editor, index)

    
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
        if index.data() and (not index.data() == 'None'):
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
        if index.model().data(index, Qt.DisplayRole) and (not index.model().data(index, Qt.DisplayRole) == 'None'):
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
        self.listFilters = []
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
        formEditor = numberDialog(self.parent(), self.listFilters)
        formEditor.setNameTable("numbers")
        formEditor.signalEndEdit.connect(self.closeAndCommitEditor)
        return formEditor

    def setModelData(self, editor, model, index):
        """Если строка в таблице не выбрана, то в модель возвращается -1,
        если строка выбрана, то возвращается строка содержащая номер строки"""
        #print("run setModelData(); currentIndex = {}".format(editor.mainTable.currentRow()))
        #print("from setModelData. Index = {}".format(editor.mainTable.currentRow()))
        indexOfEditor = editor.tableQuery.currentRow()
        if indexOfEditor == -1:
            self.result = 'None'
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

    def createEditor(self, parent, option, index):
        #super().createEditor(parent, option, index)
        formEditor = numberDialog(self.parent(), self.listFilters)
        formEditor.setNameTable(self._name_slave_table)
        formEditor.signalEndEdit.connect(self.closeAndCommitEditor)
        return formEditor

    def paint(self, painter, option, index):
        painter.save()
        if (index.data()) and (not (index.data() == 'None')):
            SqlSelect = self._SqlSelectSlaveRecord.format(index.data())
            #print(SqlSelect)
            connect = getConnection()
            cursor = connect.cursor()
            cursor.execute(SqlSelect)
            row = cursor.fetchone()
            connect.close()
            painter.drawText(option.rect, Qt.AlignCenter, str(self._function_view(row)))
        painter.restore()

class functionViewQueryEditDelegate(tableDelegate):
    """Делегат который для отображения и редактирования данных в ячейке таблицы использует
    форму, содержащую результат выполнения запроса к БД. Остальное все так же, как и
    в functionViewTableEditDelegate"""
    def __init__(self, parent, query, function_view):
        """В таблицу передаются строка запроса и функция к строке 
        результатов, использующаяся для вывода значения"""
        self._function_view = function_view
        self._query = query
        self._primary_key = self.getFieldPrimaryKey()
        super().__init__(parent)

    def getFieldPrimaryKey(self):
        """Метод возвращает название поля первичного ключа главной таблицы. Определяется по имени первого 
        поля в запросе `query`"""
        if not self._query:
            return ""
        else:
            return re.search("(?<=SELECT\s)\w\..+?(?=as)", self._query, flags=re.I).group().rstrip().lstrip().split('.')
            #return re.search("(?<=SELECT.+)\w\..+?(?=as)", self._query, flags=re.I).group().rstrip()

    def paint(self, painter, option, index):
        painter.save()
        if (index.data()) and (not (index.data() == 'None')) and (self._primary_key):
            connect = getConnection()
            cursor = connect.cursor()
            selectSQL = self._query+" WHERE {} = {}".format('.'.join(self._primary_key), index.data())
            #print(f"selectSQL={selectSQL}")
            cursor.execute(selectSQL)
            row = cursor.fetchone()
            connect.close()
            painter.drawText(option.rect, Qt.AlignCenter, str(self._function_view(row)))
        painter.restore()

    def createEditor(self, parent, option, index):
        #super().createEditor(parent, option, index)
        formEditor = numberDialog(self.parent(), self.listFilters)
        formEditor.setQuery(self._query)#"SELECT r.id_room, r.num_room as `№ пом`, r.cod_parent as parent, (SELECT address FROM rooms WHERE id_room = parent) as `Объект`, r.floor as `Этаж` FROM rooms r WHERE r.cod_parent > -1 ORDER BY level")
        formEditor.signalEndEdit.connect(self.closeAndCommitEditor)
        return formEditor

class multiStringsDelegate(QItemDelegate):
    """Делегат для отбражение в ячейке таблицы содержимого в несколько строк. Делегат служит для
    отображения данных из связанной таблицы при отношении многие к одному."""
    def __init__(self, parent):
        super().__init__(parent)

    #def sizeHint(self, option, index):
    #    return QSize(100, 200)

    #def paint(self, painter, option, index):
    #    painter.save()
    #    if index.data():
    #        #print("paint from multiStringsDelegate")
    #        listStrings = str(index.data()).split(',')
    #        #painter.drawText(option.rect, Qt.AlignCenter, f"<<{str(index.data())}>>")
    #        painter.drawText(option.rect, Qt.AlignCenter, '\n'.join(listStrings))
    #        #painter.drawText(option.rect.adjusted(0,0,0,300), Qt.AlignCenter, '\n'.join(listStrings))
    #    painter.restore()

    def drawDisplay(self, painter, option, rect, text):
        #print("drawDisplay()")
        if text:
            cg=option.state
            painter.save()
            #painter.setPen(option.palette.color(cg, QPalette::Text));
            #listStrings = str(index.data()).split(',')
            listStrings = text.split(',')
            #painter.setPen(option.palette.color(cg, QPalette.Text));
            painter.drawText(QRectF(rect.adjusted(0, 0, 0, 500)), '\n'.join(listStrings))#, option)
            painter.restore()
        
