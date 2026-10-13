import unittest

from carimbo_control.repositories import MemoryRepository
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
                "Negado",
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

    def test_create_occurrence(self):
        self.service.authenticate("123456", "1234")
        item = self.service.create_occurrence(
            "Carimbo danificado",
            "Texto de teste",
            "Alta",
        )
        self.assertEqual(item["status"], "Em andamento")
        self.assertEqual(self.service.occurrences()[0]["protocol"], item["protocol"])


if __name__ == "__main__":
    unittest.main()