from PyQt5.QtWidgets import QApplication, QCalendarWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QTextCharFormat


class CalenderWithRange(QCalendarWidget):
    """Виджет календаря, поддерживающий множественный выбор даты"""
    def __init__(self):
        super().__init__()
        self.from_date = None
        self.to_date = None

        self.highlighter_format = QTextCharFormat()
        self.highlighter_format.setBackground(self.palette().brush(QPalette.Highlight))
        self.highlighter_format.setForeground(self.palette().color(QPalette.HighlightedText))

        self.clicked.connect(self.select_range)

        super().dateTextFormat()

    def highlight_range(self, format):
        """Выделяет на виджете даты из промежутка"""
        if self.from_date is None or self.to_date is None:
            return
        d1 = min(self.from_date, self.to_date)
        d2 = max(self.from_date, self.to_date)
        while d1 <= d2:
            self.setDateTextFormat(d1, format)
            d1 = d1.addDays(1)

    def select_range(self, date_value):
        """Запоминает начальную и конечную дату"""
        self.highlight_range(QTextCharFormat())

        if QApplication.instance().keyboardModifiers() & Qt.ShiftModifier and self.from_date:
            self.to_date = date_value
            self.highlight_range(self.highlighter_format)
        else:
            self.from_date = date_value	
            self.to_date = None