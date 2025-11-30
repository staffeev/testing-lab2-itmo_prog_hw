import sys
import os
import datetime
from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import Qt
from test_setup import TestSetupMixin
from unittest import mock
import gui.main_window as main_window
import gui.choose_period_form as choose_period_form


class TestGuiFiltersSorting(TestSetupMixin):
    """Тестирование фильтров и сортировки в GUI"""

    def setUp(self):
        super().setUp()
        # Несколько покупок для дальнейших операций
        
        # self.patcher_dt = mock.patch("datetime.datetime")
        # mock_dt = self.patcher_dt.start()
        # self.addCleanup(self.patcher_dt.stop)
        # mock_dt.now.return_value = datetime(2025, 10, 20)
        # mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

        self.purchases_data = [
            ["Хлеб", 50, "Продукты", QDateTime(datetime.datetime(2025, 10, 20))],
            ["Молоко", 90, "Продукты", QDateTime(datetime.datetime(2025, 10, 15))],
            ["Ноутбук", 30000, "Техника", QDateTime(datetime.datetime(2025, 9, 23))],
            ["Монитор", 15000, "Техника", QDateTime(datetime.datetime(2024, 10, 25))]
        ]

        [self.window.process_purchase(*i) for i in self.purchases_data]
    
    def _mock_now(self):
        patcher = mock.patch("gui.main_window.datetime")
        mock_dt = patcher.start()
        self.addCleanup(patcher.stop)
        mock_dt.now.return_value = datetime.datetime(2025, 10, 20)
        mock_dt.side_effect = lambda *args, **kwargs: datetime.datetime(*args, **kwargs)
        return mock_dt
    
    def get_table_data(self):
        """Возвращает данные из purchase_list в формате [name, cost, category, date]"""
        data = []
        for row in range(self.window.purchase_list.rowCount()):
            name = self.window.purchase_list.item(row, 1).text()
            cost = float(self.window.purchase_list.item(row, 2).text())
            category = self.window.purchase_list.item(row, 3).text()
            date_text = self.window.purchase_list.item(row, 0).text()
            date = QDateTime.fromString(date_text, "dd-MM-yyyy HH:mm")
            data.append([name, cost, category, date])
        return data

    def test_filter_disable_category(self):
        """Фильтр по категории (отключение)"""
        # Отключение категории "Продукты"
        index = self.window.category_combobox.model().index(1, 0)
        self.window.category_combobox.view().pressed.emit(index)
        
        shown_names = [self.window.purchase_list.item(i, 1).text()
                       for i in range(self.window.purchase_list.rowCount())]
        self.assertListEqual(sorted(shown_names), ["Монитор", "Ноутбук"])

    def test_filter_enable_category(self):
        """Фильтр по категории (отключение)"""
        # Отключение всех категорий
        index = self.window.category_combobox.model().index(0, 0)
        self.window.category_combobox.view().pressed.emit(index)
        # Включение категории "Продукты"
        index = self.window.category_combobox.model().index(1, 0)
        self.window.category_combobox.view().pressed.emit(index)
        
        shown_names = [self.window.purchase_list.item(i, 1).text()
                       for i in range(self.window.purchase_list.rowCount())]
        self.assertListEqual(sorted(shown_names), ["Молоко", "Хлеб"])

    def test_sort_by_date_descending(self):
        """Тест сортировки по убыванию даты покупки"""
        self.window.sorting_combobox.setCurrentText("По убыванию даты")
        table_data = self.get_table_data()
        self.assertEqual(table_data, sorted(self.purchases_data, key=lambda x: x[3], reverse=True))

    def test_sort_by_date_ascending(self):
        """Тест сортировки по возрастанию даты покупки"""
        self.window.sorting_combobox.setCurrentText("По возрастанию даты")
        table_data = self.get_table_data()
        self.assertEqual(table_data, sorted(self.purchases_data, key=lambda x: x[3]))
    
    def test_sort_by_cost_descending(self):
        """Тест сортировки по убыванию стоимости покупки"""
        self.window.sorting_combobox.setCurrentText("По убыванию цены")
        table_data = self.get_table_data()
        self.assertEqual(table_data, sorted(self.purchases_data, key=lambda x: x[1], reverse=True))
    
    def test_sort_by_cost_ascending(self):
        """Тест сортировки по возрастанию стоимости покупки"""
        self.window.sorting_combobox.setCurrentText("По возрастанию цены")
        table_data = self.get_table_data()
        self.assertEqual(table_data, sorted(self.purchases_data, key=lambda x: x[1]))
    
    def test_filter_by_day(self):
        """Фильтр за последний день"""
        self._mock_now()
        self.window.period_combobox.setCurrentText("День")
        self.window.update_shown_purchases()

        shown_names = [
            self.window.purchase_list.item(i, 1).text()
            for i in range(self.window.purchase_list.rowCount())
        ]
        self.assertSetEqual(set(shown_names), {"Хлеб"})

    def test_filter_by_week(self):
        """Фильтр за последнюю неделю"""
        self._mock_now()
        self.window.period_combobox.setCurrentText("Неделя")
        self.window.update_shown_purchases()

        shown_names = [
            self.window.purchase_list.item(i, 1).text()
            for i in range(self.window.purchase_list.rowCount())
        ]
        self.assertSetEqual(set(shown_names), {"Хлеб", "Молоко"})

    def test_filter_by_month(self):
        """Фильтр за последний месяц"""
        self._mock_now()
        self.window.period_combobox.setCurrentText("Месяц")
        self.window.update_shown_purchases()

        shown_names = [
            self.window.purchase_list.item(i, 1).text()
            for i in range(self.window.purchase_list.rowCount())
        ]
        self.assertSetEqual(set(shown_names), {"Хлеб", "Молоко", "Ноутбук"})

    def test_filter_by_year(self):
        """Фильтр за последний год"""
        self._mock_now()
        self.window.period_combobox.setCurrentText("Год")
        self.window.update_shown_purchases()

        shown_names = [
            self.window.purchase_list.item(i, 1).text()
            for i in range(self.window.purchase_list.rowCount())
        ]
        self.assertSetEqual(set(shown_names), {"Хлеб", "Молоко", "Ноутбук", "Монитор"})
    

    def test_filter_by_custom_period(self):
        """Тест фильтрации покупок за пользовательский период"""
        # Делаем мок для формы с календарем
        mock_form = mock.MagicMock()
        mock_form.exec.return_value = True
        mock_calendar = mock.MagicMock()
        mock_calendar.from_date.toPyDate.return_value = datetime.date(2025, 10, 15)
        mock_calendar.to_date.toPyDate.return_value = datetime.date(2025, 10, 20)
        mock_form.calendar = mock_calendar

        with mock.patch("gui.main_window.ChoosePeriodForm", return_value=mock_form):
            self.window.period_combobox.setCurrentText("Выбрать")
            self.window.update_shown_purchases()

            shown_names = [
                self.window.purchase_list.item(i, 1).text()
                for i in range(self.window.purchase_list.rowCount())
            ]
            
            self.assertSetEqual(set(shown_names), {"Хлеб", "Молоко"})



