import unittest
from unittest import mock
from PyQt5.QtWidgets import QApplication, QMessageBox
from models import db_session
from gui.main_window import MoneyControlApp
from datetime import datetime
from PyQt5.QtCore import QDateTime

app = QApplication([])


class TestSetupMixin(unittest.TestCase):
    TEST_DB = ":memory:"

    @classmethod
    def setUpClass(cls):
        cls._patch_question = mock.patch.object(QMessageBox, "question", return_value=QMessageBox.Yes)
        cls._patch_critical = mock.patch.object(QMessageBox, "critical", return_value=None)
        cls._patch_question.start()
        cls._patch_critical.start()

        cls._patch_qt = mock.patch("PyQt5.QtCore.QDateTime.currentDateTime", 
                                   return_value=QDateTime(datetime(2025, 10, 20, 0, 0, 0)))
        cls._patch_qt.start()

    @classmethod
    def tearDownClass(cls):
        cls._patch_question.stop()
        cls._patch_critical.stop()

    def setUp(self):
        db_session.global_init(self.TEST_DB)
        self.engine = db_session.create_session().bind
        db_session.SqlAlchemyBase.metadata.create_all(self.engine)
        self.window = MoneyControlApp(self.TEST_DB)

    def tearDown(self):
        self.window.session.close()
        self.window.close()
        db_session.SqlAlchemyBase.metadata.drop_all(bind=self.window.session.bind)
