import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt5.QtCore import QDateTime
from datetime import datetime
from test_setup import TestSetupMixin


class TestGuiEditing(TestSetupMixin):
    """Тестирование изменения покупок"""

    def test_change_purchase_existing_category(self):
        """Изменение данных о покупке"""
        # Arrange
        date_qt = QDateTime(datetime(2025, 10, 15))
        date_qt2 = QDateTime(datetime(2025, 10, 16))
        self.window.process_purchase("Хлеб", 50, "Продукты", date_qt)

        # Act
        self.window.process_purchase("Батон", 45, "Продукты", date_qt2, id_to_update=1)
    
        # Assert
        date = QDateTime.fromString(self.window.purchase_list.item(0, 0).text(), "dd-MM-yyyy HH:mm")
        name = self.window.purchase_list.item(0, 1).text()
        cost = float(self.window.purchase_list.item(0, 2).text())
        category = self.window.purchase_list.item(0, 3).text()
        self.assertEqual([name, cost, date, category], 
                         ["Батон", 45.0, date_qt2, "Продукты"])
        self.assertEqual(float(self.window.total_cost.text()), 45.0)
    
    def test_change_purchase_new_category(self):
        """Изменение данных о покупке с добавлением новой категории"""
        # Arrange
        date_qt = QDateTime(datetime(2025, 10, 15))
        model = self.window.category_combobox.model()
        self.window.process_purchase("Хлеб", 50, "Техника", date_qt)

        # Act
        self.window.process_purchase("Хлеб", 50, "Продукты", date_qt, id_to_update=1)
    
        # Assert
        category = self.window.purchase_list.item(0, 3).text()
        self.assertEqual(category, "Продукты")
        category_names = [model.item(i).text() for i in range(model.rowCount())]
        self.assertIn("Продукты", category_names)