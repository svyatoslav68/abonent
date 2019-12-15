# В модуле создаются виджеты необходимые для реализации модели 
# Модель - представление для программы abonent
from PyQt5.QtWidgets import QTableView, QItemDelegate, QWidget, QHBoxLayout, QVBoxLayout 
from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox
from PyQt5.QtCore import Qt, QSettings, QModelIndex, QSortFilterProxyModel, pyqtSlot
from Models import ModelAbonents
from Delegats import comboDelegate, comboBdDelegate, tableDelegate, functionViewTableEditDelegate, defaultDelegate, functionViewQueryEditDelegate, multiStringsDelegate

#typesOfTable = (tableNumbers, # Таблица отображает
class PhonesTableView(QTableView):
    # Табличное представление для отображения таблицы данных о телефонных аппаратах
    def __init__(self):
        super().__init__()
        self.horizontalHeader().sectionClicked.connect(lambda:self.sortByColumn(self.currentIndex().column(), Qt.AscendingOrder))
        self.verticalHeader().setVisible(True)


    def setTableSizing(self, nameTable):
        """Функция устанавливает размеры окон приложения и ширину столбцов таблиц"""
        settings = QSettings("abonent.ini", QSettings.IniFormat)
        nameSection = "tab_{}".format(nameTable)
        settings.beginGroup(nameSection)
        #print(f"nameGroup={nameSection}")
        if isinstance(self.model(), ModelAbonents):
            innerModel = self.model()
        elif isinstance(self.model(), QSortFilterProxyModel):
            innerModel = self.model().sourceModel()
        for i in range(len(innerModel.namesColumn)):
            self.setColumnWidth(i, int(settings.value(str(i), 100)))
        settings.endGroup()

    def setModel(self, model):
        """Функция переоределяется для того, чтобы была возможность установить делегаты для различных столбцов
        представления. Выбор делегата для столбца определяется в зависимости от того, какая модель подключается"""
        if isinstance(model, ModelAbonents):
            innerModel = model
        elif isinstance(model, QSortFilterProxyModel):
            innerModel = model.sourceModel()
        super().setModel(model)
        nameMainTable = innerModel.getNameMainTable()[0]
        self.setTableSizing(nameMainTable)
        dictDelegats = {} # Словарь, ключ - номер столбца, значение - делегат, связанный со столбцом таблицы
        #numColumn = 0   # Номер столбца
        if nameMainTable in ("numbers"):#, "rooms"):
            for numColumn in range(innerModel.columnCount(QModelIndex())):
                #print(f"from setModel(); name_table={nameMainTable}")
                if numColumn == 3:
                    dictDelegats[numColumn] = comboBdDelegate(self.parent(),'number_status', 'name_status')
                else:
                    dictDelegats[numColumn] = defaultDelegate(self.parent())
                self.setItemDelegateForColumn(numColumn, dictDelegats[numColumn])            
                #print(f"numColumn = {numColumn}")
        if nameMainTable == "rooms":
            for numColumn in range(innerModel.columnCount(QModelIndex())):
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
            for numColumn in range(innerModel.columnCount(QModelIndex())):
                if numColumn == 3:
                    dictDelegats[numColumn] = comboBdDelegate(self.parent(),'types_TA', 'name_type')
                    #self.setItemDelegateForColumn(numColumn, dictDelegats[numColumn])
                elif numColumn == 6:
                    dictDelegats[numColumn] = comboBdDelegate(self.parent(),'phone_status', 'name_status')
                    #self.setItemDelegateForColumn(numColumn, dictDelegats[numColumn])
                elif numColumn == 7:
                    dictDelegats[numColumn] = functionViewTableEditDelegate(self.parent(), 'numbers', lambda row:row['name_net']+'   '+row['number'])
                    dictDelegats[numColumn].listFilters.append(dict(name_field='name_net', alias="Сеть", widget='QComboBox', condition = 'eq', SqlFill = "SELECT DISTINCT name_net FROM numbers") )
                    dictDelegats[numColumn].listFilters.append(dict(name_field='number', alias="Номер", widget='QLineEdit', condition = 'like', SqlFill = "")) 
                    #self.setItemDelegateForColumn(numColumn, dictDelegats[numColumn])
                elif numColumn == 8:
                    dictDelegats[numColumn] = functionViewQueryEditDelegate(self.parent(), 'SELECT r.id_room as `Код`, r.floor as `Этаж`, r.num_room as `№ пом.`, p_r.address as `Адрес` FROM rooms r INNER JOIN rooms p_r ON r.cod_parent = p_r.id_room', lambda row: "{}, пом. {}".format(list(row.values())[3],list(row.values())[2]))
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

class TableWithFiltres(QWidget):
    """Виджет, который содержит табличное представление и соответствующую содержанию панель фильтрации.
    Является потомком QWidget. В качестве табличного представления используется PhonesTableView"""
    def __init__(self):
        super().__init__()
        hboxlayout = QHBoxLayout()
        self.table = PhonesTableView()
        self.filterWidget = QWidget()
        #self.filterWidget.maximumWidth = 100#self.width()/3
        self.filterWidget.setVisible(False)
        self.filterlayout = QVBoxLayout()
        self.filterWidget.setLayout(self.filterlayout)
        hboxlayout.addWidget(self.filterWidget, 1)
        hboxlayout.addWidget(self.table,3)
        self.setLayout(hboxlayout)

    @pyqtSlot(bool)
    def hideFilterPanel(self, hide):
        """Слот предназначен для показа|скрытия панели фильтрации.
        Скрытие происходит при значении параметра hide=True."""
        #print(hide)
        #def hideWidgets(layout, hide):
        #    """Рекурсивная функция скрытия виджетов, содержащихся в layout"""
        #    for i in range(layout.count()):
        #        item = layout.itemAt(i)
        #        if item.layout():
        #            hideWidgets(item.layout(), hide)
        #            continue
        #        if item.widget():
        #            item.widget().setVisible(hide)
        #hideWidgets(self.filterlayout, hide)
        self.filterWidget.setVisible(hide)

    def setTableSizing(self, nameTable):
        self.table(nameTable)

    def setModel(self, model):
        self.table.setModel(model)

    def model(self):
        return self.table.model()

    def currentIndex(self):
        return self.table.currentIndex()

    def selectedIndexes(self):
        return self.table.selectedIndexes()

    def createWidgetsFiltres(self):
        """Создание виджета панели фильтрации. Тип виджета для фильтрации по значению 
        поля определяется из анализа типа делегата установленного для соответсвующего
        столбца представления"""
        def clearLayout(layout):
            """Рекурсивная функция для очистки layout'а"""
            while layout.count():
                item = layout.takeAt(0)
                if item.layout():
                    clearLayout(item.layout())
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        clearLayout(self.filterlayout)
        if isinstance(self.model(), ModelAbonents):
            innerModel = self.model()
        elif isinstance(self.model(), QSortFilterProxyModel):
            innerModel = self.model().sourceModel()
        #count = 0
        for i in range(len(innerModel.namesColumn)):
            label = QLabel(innerModel.namesColumn[i])
            delegateForColumn = self.table.itemDelegateForColumn(i)
            if isinstance(delegateForColumn, defaultDelegate): # Для делегата по умолчанию выбирается QLineEdit
                itemFilter = QLineEdit()
                if isinstance(self.model(), QSortFilterProxyModel):
                    itemFilter.textChanged.connect(self.model().changeParametrsFiltrering)
            elif isinstance(delegateForColumn, comboDelegate):
                itemFilter = QComboBox()
                itemFilter.addItems(delegateForColumn.content.values())
            elif isinstance(delegateForColumn, comboBdDelegate): 
                # Для delegateForColumn выбирается QComboBox, items которого заполняется из поля content делегата
                itemFilter = QComboBox()
                itemFilter.addItems(delegateForColumn.content.values())
                if isinstance(self.model(), QSortFilterProxyModel):
                    itemFilter.currentIndexChanged.connect(self.model().changeIndexFiltrering)
            else:
                continue
            itemFilter.setObjectName(str(i))#innerModel.savedFields[i])
            fieldlayout = QHBoxLayout()
            fieldlayout.addWidget(label,1)
            fieldlayout.addWidget(itemFilter,2)
            self.filterlayout.addLayout(fieldlayout)
        self.filterlayout.addStretch()
        self.hideFilterPanel(False)


class AbonentsTableView(QTableView):
    # Табличное представление для отображения таблицы данных о телефонных номерах
    def __init__(self):
        super().__init__()

