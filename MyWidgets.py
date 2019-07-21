# В модуле создаются виджеты необходимые для реализации модели 
# Модель - представление для программы abonent
from PyQt5.QtWidgets import QTableView, QItemDelegate
from PyQt5.QtCore import Qt, QSettings, QModelIndex
from Models import ModelAbonents
from Delegats import comboDelegate, comboBdDelegate, tableDelegate, functionViewTableEditDelegate, defaultDelegate, functionViewQueryEditDelegate, multiStringsDelegate

#typesOfTable = (tableNumbers, # Таблица отображает
class PhonesTableView(QTableView):
    # Табличное представление для отображения таблицы данных о телефонных аппаратах
    def __init__(self):
        super().__init__()


    def setTableSizing(self, nameTable):
        """Функция устанавливает размеры окон приложения и ширину столбцов таблиц"""
        settings = QSettings("abonent.ini", QSettings.IniFormat)
        nameSection = "tab_{}".format(nameTable)
        settings.beginGroup(nameSection)
        #print(f"nameGroup={nameSection}")
        for i in range(len(self.model().namesColumn)):
            self.setColumnWidth(i, int(settings.value(str(i), 100)))
        settings.endGroup()
    
    def setModel(self, model):
        if isinstance(model, ModelAbonents):
            super().setModel(model)
            nameMainTable = model.getNameMainTable()[0]
            self.setTableSizing(nameMainTable)
            dictDelegats = {} # Словарь, ключ - номер столбца, значение - делегат, связанный со столбцом таблицы
            #numColumn = 0   # Номер столбца
            if nameMainTable in ("numbers"):#, "rooms"):
                for numColumn in range(model.columnCount(QModelIndex())):
                    #print(f"from setModel(); name_table={nameMainTable}")
                    dictDelegats[numColumn] = defaultDelegate(self.parent())
                    self.setItemDelegateForColumn(numColumn, dictDelegats[numColumn])            
                    #print(f"numColumn = {numColumn}")
            if nameMainTable == "rooms":
                for numColumn in range(model.columnCount(QModelIndex())):
                    if numColumn == 2:
                        #dictDelegats[numColumn] = functionViewQueryEditDelegate(self.parent(), 'SELECT r.id_room as `Код`, r.floor as `Этаж`, r.num_room as `№ пом.`, p_r.address as `Адрес` FROM rooms r INNER JOIN rooms p_r ON r.cod_parent = p_r.id_room', lambda row: list(row.values())[3])
                        dictDelegats[numColumn] = functionViewQueryEditDelegate(self.parent(), 'SELECT r.id_room as `Cod`, r.address as `Address`, r.num_room as `number` FROM rooms r', lambda row:row['Address'])
                    #elif numColumn == 5:
                    #    dictDelegats[numColumn] = multiStringsDelegate(self.parent())
                    else:
                        dictDelegats[numColumn] = defaultDelegate(self.parent())
                    self.setItemDelegateForColumn(numColumn, dictDelegats[numColumn])            
                #print(dictDelegats)
            if nameMainTable == "phones":
                for numColumn in range(model.columnCount(QModelIndex())):
                    if numColumn == 3:
                        dictDelegats[numColumn] = comboBdDelegate(self.parent(),'types_TA', 'name_type')
                        #self.setItemDelegateForColumn(numColumn, dictDelegats[numColumn])
                    elif numColumn == 5:
                        dictDelegats[numColumn] = comboBdDelegate(self.parent(),'phone_status', 'name_status')
                        #self.setItemDelegateForColumn(numColumn, dictDelegats[numColumn])
                    elif numColumn == 6:
                        dictDelegats[numColumn] = functionViewTableEditDelegate(self.parent(), 'numbers', lambda row:row['name_net']+'   '+row['number'])
                        dictDelegats[numColumn].listFilters.append(dict(name_field='name_net', alias="Сеть", widget='QComboBox', condition = 'eq', SqlFill = "SELECT DISTINCT name_net FROM numbers") )
                        dictDelegats[numColumn].listFilters.append(dict(name_field='number', alias="Номер", widget='QLineEdit', condition = 'like', SqlFill = "")) 
                        #self.setItemDelegateForColumn(numColumn, dictDelegats[numColumn])
                    elif numColumn == 9:
                        dictDelegats[numColumn] = functionViewQueryEditDelegate(self.parent(), 'SELECT r.id_room as `Код`, r.floor as `Этаж`, r.num_room as `№ пом.`, p_r.address as `Адрес` FROM rooms r INNER JOIN rooms p_r ON r.cod_parent = p_r.id_room', lambda row: list(row.values())[2])
                    else:
                        dictDelegats[numColumn] = defaultDelegate(self.parent())
                    self.setItemDelegateForColumn(numColumn, dictDelegats[numColumn])            

    def keyPressEvent(self, event):
        #print(f"Press Enter;{event.key()}\nQt.Key_Enter = {Qt.Key_Enter}")
        if event.key() == Qt.Key_Return:
            if self.model():
                #print("Press Enter")
                self.edit(self.currentIndex())
        else:
            super().keyPressEvent(event)

class AbonentsTableView(QTableView):
    # Табличное представление для отображения таблицы данных о телефонных номерах
    def __init__(self):
        super().__init__()

