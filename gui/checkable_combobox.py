from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt


class ComboBoxWithCheckBoxes(QComboBox):
    """Класс выпадающего списка значений с возможностью отметить несколько
    значений"""
    def __init__(self, names=None):
        """Функция-инициализатор"""
        super().__init__()
        self.changed_value = False
        if names is not None:
            self.names = names
        self.view().pressed.connect(self.press_item)
        self

    def hidePopup(self):
        """Функция, которая будет прятать выпадающий список или
        оставлять открытым"""
        if not self.changed_value:
            super().hidePopup()
        self.changed_value = False

    def is_item_checked(self, i):
        """Функция, возвращающая истину, если элемент с некоторым индексом
        отмечен, иначе ложь"""
        item = self.model().item(i, self.modelColumn())
        if item is not None:
            return item.checkState() == Qt.Checked

    def press_item(self, i):
        """Функция замены отметки на ее отсутствие у элемента или наоборот"""
        item = self.model().itemFromIndex(i)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
            if item.text() == "": # убрать отметки у всех категорий
                for x in range(1, self.count()):
                    it = self.model().item(x, self.modelColumn())
                    it.setCheckState(Qt.Unchecked)
            else:
                self.check_item(0, False)
        else:
            item.setCheckState(Qt.Checked)
            if item.text() == "": # поставить отметки у всех категорий
                for x in range(1, self.count()):
                    it = self.model().item(x, self.modelColumn())
                    it.setCheckState(Qt.Checked)
        self.changed_value = True

    def check_item(self, i, flag=False):
        """Функция для создания отметки у элемента (пустой)"""
        new_item = self.model().item(i, self.modelColumn())
        if not flag:
            new_item.setCheckState(Qt.Unchecked)
        else:
            new_item.setCheckState(Qt.Checked)