import sys
import os
sys.path.append(os.getcwd())
from models import db_session
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QAbstractItemView, \
    QHeaderView, QComboBox, QMenu, QMessageBox
from PyQt5 import QtCore
from PyQt5.uic import loadUi
from PyQt5.QtGui import QColor
from gui.checkable_combobox import ComboBoxWithCheckBoxes
from gui.form_add_purchase import AddForm
from gui.choose_period_form import ChoosePeriodForm
from db.db_control_functions import get_categories, get_products, add_category, \
    get_category_by_name, add_purchase, delete_purcahses, change_purchase, delete_category_by_name
import qdarktheme
from datetime import datetime


def except_hook(cls, exception, traceback):
    """Функция для отлова возможных исключений, вознкающих при работе с Qt"""
    sys.__excepthook__(cls, exception, traceback)


class MoneyControlApp(QMainWindow):
    """Класс основного окна программы"""
    def __init__(self, path_to_db: str):
        super().__init__()
        loadUi("gui/ui/main_window.ui", self)
        self.setCentralWidget(self.centralwidget)
        self.setLayout(self.gridLayout)
        self.setStyleSheet("QToolTip { color: #ffffff; background-color: #000000; border: 0px; }")
        db_session.global_init(path_to_db)
        self.session = db_session.create_session()
        self.category_combobox = ComboBoxWithCheckBoxes()
        self.gridLayout_2.addWidget(self.category_combobox, 3, 1, 1, 1)
        # Объявление нужных переменных
        self.all_categories = get_categories(self.session)
        self.all_purchases = get_products(self.session)
        self.shown_purchases = [i for i in self.all_purchases]
        # Настройка сигналов и слотов
        self.purchase_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.btn_add_purchase.clicked.connect(self.exec_add_purchase_form)
        self.btn_add_balance.clicked.connect(lambda: self.exec_add_purchase_form(True))
        self.sorting_combobox.currentTextChanged.connect(self.load_all_purchases)
        self.category_combobox.view().pressed.connect(self.update_shown_purchases)
        # self.category_combobox.currentTextChanged.connect(self.update_shown_purchases)
        self.period_combobox.currentTextChanged.connect(self.update_shown_purchases)
        self.reset_btn.clicked.connect(self.reset_filters)
        self.category_combobox.setInsertPolicy(QComboBox.NoInsert)

        # Вызов предварительных функций
        self.load_all_categories()
        self.load_all_purchases()
        self.calculate_total_cost()
        self.update_balance()
    
    def get_month_refill(self):
        """Получение месячной выплаты"""
        day = datetime.now().day
        if day != 15:
            return
        add_purchase(self.session, "Начисление зарплаты", -30000, datetime.now(), "Зарплата")
    
    def get_balance(self):
        """Возвращает баланс кошелька"""
        cash_receipts = get_products(self.session, -1)
        balance = sum([-i.cost for i in cash_receipts]) - sum([i.cost for i in self.all_purchases])
        return balance
    
    def update_balance(self):
        """Выводит баланс кошелька"""
        self.balance.setText(str(round(self.get_balance(), 2)))
    
    def reload_all_purchases(self):
        """Делает повторный запрос в бд на получение покупок"""
        self.all_purchases = get_products(self.session)
        self.update_shown_purchases()

    def reload_all_categories(self):
        """Делает повторный запрос в бд на получение категорий"""
        self.all_categories= get_categories(self.session)
        self.load_all_categories()
    
    def reset_filters(self):
        """Сброс фильтров"""
        [self.category_combobox.check_item(i, True) for i in range(self.category_combobox.count())]
        self.period_combobox.setCurrentIndex(0)
        self.sorting_combobox.setCurrentIndex(0)
        self.update_shown_purchases()

    def filter_by_period(self):
        """Оставляет в таблице покупки по фильтру"""
        filtered_purchases = self.get_filtered_purchases(self.all_purchases)
        self.update_shown_purchases(filtered_purchases)
    
    def get_filtered_purchases_by_period(self, purchases: list):
        """Возвращает покупки с фильтром времени"""
        period = self.period_combobox.currentText()
        if not period: # период не установлен
            return purchases
        if period != "Выбрать": # период из предустановленных
            current_dt = datetime.now()
            dif_days = {"День": 1, "Неделя": 7, "Месяц": 31, "Год": 365}[period]
            return list(filter(lambda x: (current_dt - x.date).days <= dif_days, purchases))
        # пользователь выбирает период сам
        form = ChoosePeriodForm()
        if not form.exec():
            return purchases
        start_dt = form.calendar.from_date.toPyDate()
        if form.calendar.to_date is None: # если выбран не промежуток, а один день
            return list(filter(lambda x: x.date.date() == start_dt, purchases))
        end_dt = form.calendar.to_date.toPyDate()
        if end_dt < start_dt:
            start_dt, end_dt = end_dt, start_dt
        return list(filter(lambda x: start_dt <= x.date.date() <= end_dt, purchases))
    
    def get_filtered_purchases_by_category(self, purchases: list):
        """Возвращает покупки с фильтром категории"""
        # получим список выделенных категорий
        if self.category_combobox.is_item_checked(0): # выделены все категории
            return purchases
        categories = {self.category_combobox.itemText(i) for i in 
                      range(self.category_combobox.count()) if self.category_combobox.is_item_checked(i)}
        if not categories: # ничего не выделено
            return []
        return list(filter(lambda x: x.category.name in categories, purchases))

    def load_all_categories(self):
        """Загрузка категорий в меню"""
        self.category_combobox.clear()
        self.category_combobox.addItems([""] + sorted(map(str, self.all_categories)))
        [self.category_combobox.check_item(i, True) for i in range(self.category_combobox.count())]
    
    def update_shown_purchases(self):
        """Обновляет список показываемых покупок"""
        self.shown_purchases = self.get_filtered_purchases_by_category(
            self.get_filtered_purchases_by_period(self.all_purchases))
        self.calculate_total_cost()
        self.update_balance()
        self.load_all_purchases()
    
    def calculate_total_cost(self):
        """Подсчет суммы потраченных средств за период"""
        value = sum(i.cost for i in self.shown_purchases)
        self.total_cost.setText(str(round(value, 2)))
    
    def load_all_purchases(self):
        """Загрузка покупок в таблицу"""
        self.shown_purchases = self.get_sorted_purchases()
        self.purchase_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)   
        self.purchase_list.setRowCount(len(self.shown_purchases))
        for i, purchase in enumerate(self.shown_purchases):
            self.purchase_list.setItem(i, 0, QTableWidgetItem(purchase.date.strftime("%d-%m-%Y %H:%M")))
            self.purchase_list.setItem(i, 1, QTableWidgetItem(purchase.name))
            self.purchase_list.setItem(i, 2, QTableWidgetItem(str(purchase.cost)))
            if purchase.category is None:
                continue
            self.purchase_list.setItem(i, 3, QTableWidgetItem(str(purchase.category)))
            self.purchase_list.item(i, 3).setBackground(QColor(purchase.category.color))
    
    def get_sorted_purchases(self):
        """Возвращает покупки, отсортированные по ключу из меню"""
        sorting_method = self.sorting_combobox.currentText()
        if sorting_method == "По убыванию даты":
            return sorted(self.shown_purchases, key=lambda x: x.date, reverse=True)
        elif sorting_method == "По возрастанию даты":
            return sorted(self.shown_purchases, key=lambda x: x.date)
        elif sorting_method == "По убыванию цены":
            return sorted(self.shown_purchases, key=lambda x: x.cost, reverse=True)
        elif sorting_method == "По возрастанию цены":
            return sorted(self.shown_purchases, key=lambda x: x.cost)
    
    def exec_add_purchase_form(self, negative_cost=False):
        """Метод для работы с формой добавления покупки"""
        if not negative_cost:
            form = AddForm(self.all_categories, max_cost=self.get_balance())
        else:
            cats = [i for i in self.all_categories if all(x.cost < 0 for x in i.products)]
            form = AddForm(cats, "add_balance_form.ui")
        if not form.exec():
            return
        self.process_purchase(*form.get_data(), negative_cost=negative_cost)
        
    def process_purchase(self, *args, id_to_update=False, negative_cost=False):
        print(negative_cost)
        """Обработка данных о новой покупке"""
        product_name, cost, category_name, date = args
        cost = -cost if negative_cost else cost
        print(args)
        date = date.toPyDateTime()
        if category_name not in list(map(str, self.all_categories)): # новая категория
            category = add_category(self.session, category_name)
            self.reload_all_categories()
            # self.all_categories.append(category_name)
            # self.load_all_categories()
        else:
            category = get_category_by_name(self.session, category_name)
        
        if id_to_update is False: # новая запись
            add_purchase(self.session, product_name, cost, date, category)
            self.reload_all_purchases()
            # print(self.all_purchases)
            # self.all_purchases.append(purchase)
            self.update_shown_purchases()
        else: # измененная запись
            change_purchase(self.session, id_to_update, product_name, cost, date, category)
            self.reload_all_purchases()
    
    def delete_from_table(self, rows):
        """Удаление записей из таблицы"""
        flag = QMessageBox.question(
                self, "Удаление", "Вы уверены, что хотите удалить выбранные записи?"
            )
        if flag != QMessageBox.Yes:
            return
        delete_purcahses(self.session, [self.shown_purchases[i].id for i in rows])
        self.reload_all_purchases()
    
    def exec_change_table_item(self, row):
        """Изменение записи в таблице"""
        purchase = self.shown_purchases[row]
        form = AddForm(self.all_categories)
        form.set_data(purchase)
        if not form.exec():
            return
        self.process_purchase(*form.get_data(), id_to_update=purchase.id)

    def delete_categories(self, categories_names):
        """Удаление выбранных категорий"""
        flag = QMessageBox.question(
                self, "Удаление", f"Вы уверены, что хотите удалить категории {', '.join(categories_names)}? все продукты с этими категориями будут удалены."
            )
        if flag != QMessageBox.Yes:
            return
        [delete_category_by_name(self.session, cat) for cat in categories_names]
        self.reload_all_categories()
        self.reload_all_purchases()

    def closeEvent(self, _):
        """Ивент закрытия окна"""
        self.session.close()
    
    def contextMenuEvent(self, event):
        """Обработка вызова контекстного меню"""
        selected_rows = self.purchase_list.selectionModel().selectedRows()
        rows = [i.row() for i in selected_rows]
        selected_categories = {i.data(0) for i in self.purchase_list.selectedItems() if i.column() == 3}
        menu = QMenu()
        if rows:
            menu.addAction("Удалить записи", lambda: self.delete_from_table(rows))
        if len(rows) == 1:
            menu.addAction("Изменить запись", lambda: self.exec_change_table_item(rows[0]))
        if selected_categories:
            menu.addAction("Удалить категории", lambda: self.delete_categories(sorted(selected_categories)))
        menu.exec_(self.mapToGlobal(event.pos()))


def run_app(path_to_db: str):
    """Запуск программы"""
    app = QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    qdarktheme.setup_theme("dark")
    programm = MoneyControlApp(path_to_db)
    programm.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
    

if __name__ == "__main__":
    run_app("db/purchases.db")

