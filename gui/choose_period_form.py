from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi
from gui.range_calendar import CalenderWithRange

class ChoosePeriodForm(QDialog):
    """Форма для выбора периода для фильтрации покупок"""
    def __init__(self):
        super().__init__()
        loadUi("gui/ui/choose_period_form.ui", self)
        self.setLayout(self.gridLayout)
        self.calendar = CalenderWithRange()
        self.gridLayout.addWidget(self.calendar, 0, 0, 1, 1)
