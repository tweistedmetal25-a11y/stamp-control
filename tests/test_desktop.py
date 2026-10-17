import os
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton
from PySide6.QtGui import QImageReader

from carimbo_control.desktop import (
    APP_STYLESHEET,
    DesktopApplication,
    LoginWindow,
    MainWindow,
)
from carimbo_control.repositories import AccessRepository, MemoryRepository
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

    def test_demo_login_shows_operator_and_admin_accounts(self):
        login = LoginWindow(self.service)

        self.assertIsNotNone(login.demo_access_label)
        demo_text = login.demo_access_label.text()
        self.assertIn("Operador", demo_text)
        self.assertIn("Chapa 654321", demo_text)
        self.assertIn("Administrador", demo_text)
        self.assertIn("Chapa 123456", demo_text)
        login.close()

    def test_access_mode_does_not_show_demo_credentials(self):
        access_service = StampControlService(
            AccessRepository("database.accdb", "Access Driver")
        )
        login = LoginWindow(access_service)

        self.assertIsNone(login.demo_access_label)
        login.close()

    def test_program_logos_are_readable_by_qt(self):
        assets_dir = Path(__file__).resolve().parents[1] / "carimbo_control" / "assets"
        for filename in ("logo_stamp.png", "logo_kroschu.png"):
            with self.subTest(filename=filename):
                reader = QImageReader(str(assets_dir / filename))
                self.assertTrue(reader.canRead(), reader.errorString())
                self.assertFalse(reader.read().isNull(), reader.errorString())

    def test_login_and_main_windows_open_fullscreen(self):
        application = DesktopApplication(self.service)
        with patch.object(application.qt_app, "exec", return_value=0):
            self.assertEqual(application.start(), 0)
        self.assertTrue(application.login_window.isFullScreen())

        self.service.authenticate("654321", "1234")
        application.open_main()
        self.app.processEvents()
        self.assertTrue(application.main_window.isFullScreen())
        application.main_window.close()

    def test_login_primary_button_keeps_its_visible_color(self):
        login = LoginWindow(self.service)
        login.show()
        self.app.processEvents()
        button = login.findChild(QPushButton, "primaryButton")
        color = button.grab().toImage().pixelColor(8, button.height() // 2)

        self.assertEqual(color.name(), "#4b27b3")
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

    def test_operator_opens_new_request_page_and_cannot_select_new_employee(self):
        self.service.authenticate("654321", "1234")
        window = MainWindow(self.service)

        self.assertEqual(window.pages.currentIndex(), 1)
        self.assertEqual(window.nav_buttons["Nova ocorrência"].isChecked(), True)
        occurrence_types = [
            window.occurrence_type.itemText(index)
            for index in range(window.occurrence_type.count())
        ]
        self.assertNotIn("Funcionário novo", occurrence_types)
        window.close()

    def test_operator_sees_only_owned_requests_without_admin_controls(self):
        self.service.authenticate("654321", "1234")
        window = MainWindow(self.service)
        window.show_page("Minhas solicitações")

        self.assertEqual(window.requests_table.rowCount(), 1)
        self.assertEqual(window.requests_table.item(0, 2).text(), "654321")
        self.assertIsNone(window.request_admin_panel)
        self.assertIsNotNone(window.priority_info)
        self.assertFalse(window.priority_info.isHidden())
        self.assertNotIn("Central de notificações", window.nav_buttons)
        window.close()

    def test_admin_can_edit_priority_and_status_from_requests_page(self):
        self.service.authenticate("123456", "1234")
        window = MainWindow(self.service)
        window.show_page("Solicitações da equipe")
        self.assertEqual(window.requests_table.rowCount(), 4)
        self.assertIsNotNone(window.request_admin_panel)
        self.assertIsNone(window.priority_info)
        self.assertEqual(
            [window.request_status.itemText(index) for index in range(window.request_status.count())],
            ["Em andamento", "Concluído"],
        )
        occurrence_types = [
            window.occurrence_type.itemText(index)
            for index in range(window.occurrence_type.count())
        ]
        self.assertIn("Funcionário novo", occurrence_types)

        row = next(
            index
            for index in range(window.requests_table.rowCount())
            if window.requests_table.item(index, 2).text() == "654321"
        )
        window.requests_table.selectRow(row)
        self.app.processEvents()
        self.assertTrue(window.save_request_button.isEnabled())
        self.assertEqual(
            window.request_description.toPlainText(),
            "Solicitação de substituição por desgaste.",
        )
        protocol = window.request_protocol
        window.request_priority.setCurrentText("Alta")
        window.request_status.setCurrentText("Concluído")

        with patch("carimbo_control.desktop.QMessageBox.information"):
            window._save_request_changes()

        updated = next(
            item
            for item in self.service.occurrences()
            if item["protocol"] == protocol
        )
        self.assertEqual(updated["priority"], "Alta")
        self.assertEqual(updated["status"], "Concluído")
        window.close()


if __name__ == "__main__":
    unittest.main()
