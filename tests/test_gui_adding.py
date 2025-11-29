import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt5.QtCore import QDateTime
from datetime import datetime
from test_setup import TestSetupMixin


class TestGuiAdding(TestSetupMixin):
    """Тестирование добавления покупок"""

    def test_add_income(self):
        """Пополнение баланса"""
        # Act
        self.window.process_purchase("Фриланс", 5000, "Переводы", QDateTime(datetime(2025, 10, 25)), negative_cost=True)
        self.window.process_purchase("Аванс", 15000, "Зарплата", QDateTime(datetime(2025, 10, 15)), negative_cost=True)
    
        # Assert
        self.assertEqual(float(self.window.balance.text()), 5000 + 15000)
    

    def test_add_purchase(self):
        """Добавление покупки с новой категорией"""
        # Arrange
        model = self.window.category_combobox.model()
        date_qt = QDateTime(datetime(2025, 10, 25))

        # Act
        self.window.process_purchase("Хлеб", 50, "Продукты", date_qt)

        # Assert
        date = QDateTime.fromString(self.window.purchase_list.item(0, 0).text(), "dd-MM-yyyy HH:mm")
        name = self.window.purchase_list.item(0, 1).text()
        cost = float(self.window.purchase_list.item(0, 2).text())
        category = self.window.purchase_list.item(0, 3).text()
        self.assertEqual([name, cost, date, category], 
                         ["Хлеб", 50.0, date_qt, "Продукты"])
        self.assertEqual(float(self.window.total_cost.text()), 50.0)
        category_names = [model.item(i).text() for i in range(model.rowCount())]
        self.assertIn("Продукты", category_names)
    
