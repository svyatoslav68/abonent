# В модуле создаются виджеты необходимые для реализации модели 
# Модель - представление для программы abonent
from PyQt5.QtWidgets import QTableView, QItemDelegate
from Models import comboDelegate

#typesOfTable = (tableNumbers, # Таблица отображает
class PhonesTableView(QTableView):
    # Табличное представление для отображения таблицы данных о телефонных аппаратах
    def __init__(self):
        super().__init__()

class AbonentsTableView(QTableView):
    # Табличное представление для отображения таблицы данных о телефонных номерах
    def __init__(self):
        super().__init__()

