import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from test_setup import TestSetupMixin
from db.db_control_functions import add_category, add_purchase, get_categories, get_products, \
    delete_category_by_name, delete_purcahses
from PyQt5.QtCore import QDateTime


class TestCRUD(TestSetupMixin):
    """Тестирование CRUD-функций для БД"""

    def test_add_category(self):
        cat = add_category(self.window.session, "Транспорт")
        self.assertIn(cat, get_categories(self.window.session))

    def test_add_purchase(self):
        cat_name = "Техника"
        cat = add_category(self.window.session, cat_name)
        purchase = add_purchase(self.window.session, "Ноутбук", 30000, self.cur_date, cat)
        self.assertIn(purchase, get_products(self.window.session))
        self.assertTrue(any(c.name == cat_name for c in get_categories(self.window.session)))

    def test_delete_category(self):
        cat_name = "Продукты"
        add_category(self.window.session, cat_name)
        delete_category_by_name(self.window.session, cat_name)
        self.assertTrue(not any(c.name == cat_name for c in get_categories(self.window.session)))

    def test_delete_purchase(self):
        cat_name = "Медицина"
        cat = add_category(self.window.session, cat_name)
        purchase = add_purchase(self.window.session, "Анализы", 7000, self.cur_date, cat)
        delete_purcahses(self.window.session, [purchase.id])
        self.assertTrue(purchase not in get_products(self.window.session))

    def test_change_purchase(self):
        from datetime import datetime

        cat_name = "Образование"
        cat = add_category(self.window.session, cat_name)
        p = add_purchase(self.window.session, "ДПО от Яндекса", 150000, self.cur_date, cat)
        p.name = "ДПО от Альфа-банка"
        p.date = datetime(2025, 10, 15, 0, 0)
        p.cost = 135000
        self.window.session.commit()

        updated = self.window.session.query(p.__class__).filter_by(id=p.id).first()
        self.assertEqual(updated.name, "ДПО от Альфа-банка")
        self.assertEqual(updated.date, datetime(2025, 10, 15, 0, 0))
        self.assertEqual(updated.cost, 135000)
