import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from test_setup import TestSetupMixin
from datetime import datetime
from PyQt5.QtCore import QDateTime


class TestGuiDeleting(TestSetupMixin):
    """Тестирование удаления покупок и категорий через GUI"""

    def test_delete_category(self):
        """Удаление категории и связанных покупок"""
        # Arrange
        date_qt = QDateTime(datetime(2025, 10, 15))
        self.window.process_purchase("Хлеб", 50, "Продукты", date_qt)
        self.window.process_purchase("Молоко", 90, "Продукты", date_qt)
        self.window.process_purchase("Ноутбук", 30000, "Техника", date_qt)
        third_name = self.window.purchase_list.item(2, 1).text()
        model = self.window.category_combobox.model()
        self.assertEqual(self.window.purchase_list.rowCount(), 3)

        # Act
        self.window.delete_categories(["Продукты"])

        # Assert
        self.assertEqual(self.window.purchase_list.rowCount(), 1)
        self.assertEqual(self.window.purchase_list.item(0, 1).text(), third_name)
        category_names = [model.item(i).text() for i in range(model.rowCount())]
        self.assertNotIn("Продукты", category_names)
    
    def test_delete_purchases(self):
        """Удаление покупок"""
        # Arrange
        date_qt = QDateTime(datetime(2025, 10, 15))
        self.window.process_purchase("Хлеб", 50, "Продукты", date_qt)
        self.window.process_purchase("Молоко", 90, "Продукты", date_qt)
        second_name = self.window.purchase_list.item(1, 1).text()
        self.assertEqual(self.window.purchase_list.rowCount(), 2)

        # Act
        self.window.delete_from_table([0])

        # Assert
        self.assertEqual(self.window.purchase_list.rowCount(), 1)
        self.assertEqual(self.window.purchase_list.item(0, 1).text(), second_name)