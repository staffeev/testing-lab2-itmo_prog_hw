import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt5.QtCore import QDateTime
from test_setup import TestSetupMixin
from db.db_control_functions import add_category, add_purchase, get_categories, get_products, \
    delete_category_by_name, delete_purcahses


class TestGuiDeleting(TestSetupMixin):
    """Тестирование удаления покупок и категорий через GUI"""

    def test_delete_category(self):
        """Удаление категории и связанных покупок"""
        self.window.process_purchase("Хлеб", 50, "Продукты", QDateTime.currentDateTime())
        self.window.process_purchase("Молоко", 90, "Продукты", QDateTime.currentDateTime())
        self.window.process_purchase("Ноутбук", 30000, "Техника", QDateTime.currentDateTime())
        third_name = self.window.purchase_list.item(2, 0).text()
        self.assertEqual(self.window.purchase_list.rowCount(), 3)

        self.window.delete_categories(["Продукты"])

        self.assertEqual(self.window.purchase_list.rowCount(), 1)
        self.assertEqual(self.window.purchase_list.item(0, 0).text(), third_name)
    

    def test_delete_purchases(self):
        """Удаление покупок"""
        self.window.process_purchase("Хлеб", 50, "Продукты", QDateTime.currentDateTime())
        self.window.process_purchase("Молоко", 90, "Продукты", QDateTime.currentDateTime())
        second_name = self.window.purchase_list.item(1, 0).text()
        self.assertEqual(self.window.purchase_list.rowCount(), 2)

        self.window.delete_from_table([0])

        self.assertEqual(self.window.purchase_list.rowCount(), 1)
        self.assertEqual(self.window.purchase_list.item(0, 0).text(), second_name)