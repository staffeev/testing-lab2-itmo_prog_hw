import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from test_setup import TestSetupMixin
from db.db_control_functions import add_category, add_purchase, get_categories, get_products, \
    delete_category_by_name, delete_purcahses
from datetime import datetime


class TestCRUD(TestSetupMixin):
    """Тестирование CRUD-функций для БД"""

    def test_add_category(self):
        """Добавление новой категории"""
        cat = add_category(self.window.session, "Транспорт")
        self.assertIn(cat, get_categories(self.window.session))

    def test_add_category_empty_name(self):
        """Добавление категории с пустым именем"""
        with self.assertRaises(Exception):
            add_category(self.window.session, "")

    def test_add_category_long_name(self):
        """Добавление категории с слишкм длинным именем"""
        with self.assertRaises(Exception):
            add_category(self.window.session, "A" * 1001)
    
    def test_add_category_nonunique_name(self):
        """Дублирование категории"""
        cat_name = "Категория"
        add_category(self.window.session, cat_name)
        with self.assertRaises(Exception):
            add_category(self.window.session, cat_name)

    def test_add_purchase(self):
        """Добавление покупки"""
        cat_name = "Техника"
        cat = add_category(self.window.session, cat_name)
        purchase = add_purchase(self.window.session, "Ноутбук", 30000, datetime(2025, 10, 15), cat)
        self.assertIn(purchase, get_products(self.window.session))
        self.assertTrue(any(c.name == cat_name for c in get_categories(self.window.session)))

    def test_add_purchase_empty_name(self):
        """Добавление покупки с пустым именем"""
        cat = add_category(self.window.session, "Категория")
        with self.assertRaises(Exception):
            add_purchase(self.window.session, "", 30000, datetime(2025, 10, 15), cat)

    def test_add_purchase_long_name(self):
        """Добавление покупки с слишком длинным именем"""
        cat = add_category(self.window.session, "Категория")
        with self.assertRaises(Exception):
            add_purchase(self.window.session, "A" * 1001, 30000, datetime(2025, 10, 15), cat)
    
    def test_add_purchase_large_cost(self):
        """Добавление покупки с слишком большой суммой"""
        cat = add_category(self.window.session, "Категория")
        with self.assertRaises(Exception):
            add_purchase(self.window.session, "", 10 ** 9 + 7, datetime(2025, 10, 15), cat)

    def test_delete_category(self):
        """Удаление категории"""
        cat_name = "Продукты"
        add_category(self.window.session, cat_name)
        delete_category_by_name(self.window.session, cat_name)
        self.assertTrue(not any(c.name == cat_name for c in get_categories(self.window.session)))

    def test_delete_purchase(self):
        """Удаление покупки"""
        cat_name = "Медицина"
        cat = add_category(self.window.session, cat_name)
        purchase = add_purchase(self.window.session, "Анализы", 7000, datetime(2025, 10, 15), cat)
        delete_purcahses(self.window.session, [purchase.id])
        self.assertTrue(purchase not in get_products(self.window.session))

    def test_change_purchase(self):
        """Изменение покупки"""
        from datetime import datetime

        cat_name = "Образование"
        cat = add_category(self.window.session, cat_name)
        p = add_purchase(self.window.session, "ДПО от Яндекса", 150000, datetime(2025, 10, 15), cat)
        p.name = "ДПО от Альфа-банка"
        p.date = datetime(2025, 10, 15, 0, 0)
        p.cost = 135000
        self.window.session.commit()

        updated = self.window.session.query(p.__class__).filter_by(id=p.id).first()
        self.assertEqual(updated.name, "ДПО от Альфа-банка")
        self.assertEqual(updated.date, datetime(2025, 10, 15, 0, 0))
        self.assertEqual(updated.cost, 135000)

    def test_change_purchase_empty_name(self):
        """Изменение покупки на пустое имя"""
        cat = add_category(self.window.session, "Категория")
        p = add_purchase(self.window.session, "Товар", 10000, datetime(2025, 10, 15), cat)
        p.name = ""
        with self.assertRaises(Exception):
            self.window.session.commit()