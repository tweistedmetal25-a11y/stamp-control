import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from carimbo_control.desktop import APP_STYLESHEET, LoginWindow, MainWindow
from carimbo_control.repositories import MemoryRepository
from carimbo_control.services import StampControlService


class DesktopInterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")
        cls.app.setStyleSheet(APP_STYLESHEET)

    def setUp(self):
        self.service = StampControlService(MemoryRepository())

    def test_login_window_authenticates_and_opens_dashboard(self):
        login = LoginWindow(self.service)
        authenticated = []
        login.authenticated.connect(lambda: authenticated.append(True))

        login.chapa.setText("123456")
        login.password.setText("1234")
        login._authenticate()

        self.assertEqual(authenticated, [True])
        self.assertEqual(self.service.current_user["chapa"], "123456")
        login.close()

    def test_dashboard_contains_all_application_pages(self):
        self.service.authenticate("123456", "1234")
        window = MainWindow(self.service)

        self.assertEqual(window.pages.count(), 5)
        self.assertIn("Central de notificações", window.nav_buttons)
        window.show_page("Nova ocorrência", preset_type="Carimbo perdido")
        self.assertEqual(window.pages.currentIndex(), 1)
        self.assertEqual(window.occurrence_type.currentText(), "Carimbo perdido")
        window.close()


if __name__ == "__main__":
    unittest.main()
