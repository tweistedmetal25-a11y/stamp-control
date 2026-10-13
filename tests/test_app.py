import unittest
from unittest.mock import MagicMock, patch

from carimbo_control.repositories import AccessRepository, MemoryRepository
from carimbo_control.services import StampControlService


class StampControlTests(unittest.TestCase):
    def setUp(self):
        self.service = StampControlService(MemoryRepository())

    def test_authentication_sets_current_user(self):
        user = self.service.authenticate("123456", "1234")
        self.assertEqual(user["name"], "João da Silva")
        self.assertTrue(self.service.is_supervisor())

    def test_invalid_authentication_does_not_login(self):
        self.assertIsNone(self.service.authenticate("123456", "errada"))
        self.assertIsNone(self.service.current_user)

    def test_operator_only_sees_own_requests(self):
        self.service.authenticate("654321", "1234")
        records = self.service.occurrences()
        self.assertTrue(records)
        self.assertTrue(all(item["chapa"] == "654321" for item in records))

    def test_operator_cannot_bypass_filter_or_update_requests(self):
        self.service.authenticate("654321", "1234")
        records = self.service.occurrences(all_records=True)
        self.assertTrue(records)
        self.assertTrue(all(item["chapa"] == "654321" for item in records))
        with self.assertRaises(PermissionError):
            self.service.update_occurrence(
                records[0]["protocol"],
                "Alta",
                "Em andamento",
            )

    def test_admin_can_see_and_update_any_request(self):
        self.service.authenticate("123456", "1234")
        records = self.service.occurrences()
        self.assertGreater(len(records), 1)
        protocol = next(
            item["protocol"] for item in records if item["chapa"] == "654321"
        )

        self.service.update_occurrence(protocol, "Alta", "Concluído")

        updated = next(
            item
            for item in self.service.occurrences()
            if item["protocol"] == protocol
        )
        self.assertEqual(updated["priority"], "Alta")
        self.assertEqual(updated["status"], "Concluído")

    def test_update_rejects_unknown_priority_and_status(self):
        self.service.authenticate("123456", "1234")
        protocol = self.service.occurrences()[0]["protocol"]
        with self.assertRaises(ValueError):
            self.service.update_occurrence(protocol, "Urgente", "Concluído")
        with self.assertRaises(ValueError):
            self.service.update_occurrence(protocol, "Alta", "Em análise")
        with self.assertRaises(ValueError):
            self.service.update_occurrence(protocol, "Alta", "Negado")

    def test_create_occurrence(self):
        self.service.authenticate("123456", "1234")
        item = self.service.create_occurrence(
            "Carimbo danificado",
            "Texto de teste",
            "Alta",
        )
        self.assertEqual(item["status"], "Em andamento")
        self.assertEqual(self.service.occurrences()[0]["protocol"], item["protocol"])

    def test_operator_cannot_choose_priority_when_creating_request(self):
        self.service.authenticate("654321", "1234")
        item = self.service.create_occurrence(
            "Carimbo danificado",
            "Solicitação de demonstração",
            "Alta",
        )
        self.assertEqual(item["priority"], "Média")
        self.assertEqual(item["status"], "Em andamento")


class AccessRepositoryUpdateTests(unittest.TestCase):
    def setUp(self):
        self.repository = AccessRepository("database.accdb", "Access Driver")
        self.connection = MagicMock()
        self.cursor = self.connection.__enter__.return_value.cursor.return_value
        self.cursor.execute.return_value = self.cursor

    def test_update_writes_priority_and_status_to_access(self):
        self.cursor.fetchone.return_value = ("CAR-2025-0001",)
        with patch.object(self.repository, "_connect", return_value=self.connection):
            updated = self.repository.update_occurrence(
                "CAR-2025-0001",
                "Alta",
                "Concluído",
            )

        self.assertTrue(updated)
        update_call = self.cursor.execute.call_args_list[1]
        self.assertIn("UPDATE Ocorrencias", update_call.args[0])
        self.assertEqual(
            update_call.args[1:],
            ("Alta", "Concluído", "CAR-2025-0001"),
        )
        self.connection.__enter__.return_value.commit.assert_called_once()

    def test_update_returns_false_when_protocol_does_not_exist(self):
        self.cursor.fetchone.return_value = None
        with patch.object(self.repository, "_connect", return_value=self.connection):
            updated = self.repository.update_occurrence(
                "CAR-9999",
                "Baixa",
                "Em andamento",
            )

        self.assertFalse(updated)
        self.assertEqual(self.cursor.execute.call_count, 1)
        self.connection.__enter__.return_value.commit.assert_not_called()


if __name__ == "__main__":
    unittest.main()