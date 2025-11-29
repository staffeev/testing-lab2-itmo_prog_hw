from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QComboBox
from PyQt5.QtCore import QDateTime
from PyQt5.uic import loadUi
import os


class AddForm(QDialog):
    """Класс формы для добавления покупки"""
    def __init__(self, categories: list[str], ui_file="add_purchase_form.ui", max_cost=10**6):
        super().__init__()
        # loadUi(os.path.join(os.path.dirname(__file__), "ui", ui_file))
        print(ui_file)
        loadUi(f"gui/ui/{ui_file}", self)
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: #000000; border: 0px; }")
        self.setLayout(self.gridLayout)
        self.cost_spinbox.setMaximum(max_cost)
        self.category_choice.addItems(sorted(map(str, categories)))
        self.category_choice.setInsertPolicy(QComboBox.NoInsert)
        self.calendar.setDateTime(QDateTime.currentDateTime())
        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)
    
    def set_data(self, purchase):
        """Установка значений (изменение созданной записи)"""
        self.product_name.setText(purchase.name)
        self.cost_spinbox.setValue(purchase.cost)
        self.category_choice.setCurrentText(purchase.category.name)
        self.calendar.setDateTime(QDateTime.fromSecsSinceEpoch(int(purchase.date.timestamp())))


    def get_data(self):
        """Возвращает данные из формы"""
        product_name = self.product_name.text()
        cost = self.cost_spinbox.value()
        category_name = self.category_choice.currentText()
        date = self.calendar.dateTime()
        return product_name, cost, category_name, date
    
    def accept(self):
        """Проверка корректности введенных данных"""
        product_name = self.product_name.text()
        category = self.category_choice.currentText()
        if not product_name and not category:
            QMessageBox.critical(self, "Ошибка", "Название товара и категория отсутствуют")
            return
        if not product_name:
            QMessageBox.critical(self, "Ошибка", "Название товара отсутствует")
            return
        elif not category:
            QMessageBox.critical(self, "Ошибка", "Категория товара не выбрана")
            return
        elif len(category) > 1000:
            QMessageBox.critical(self, "Ошибка", "Слишком длинное название категории")
        self.done(1)
