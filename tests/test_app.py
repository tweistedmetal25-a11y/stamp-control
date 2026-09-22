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

    def test_create_occurrence(self):
        self.service.authenticate("123456", "1234")
        item = self.service.create_occurrence(
            "Carimbo danificado",
            "Texto de teste",
            "Alta",
        )
        self.assertEqual(item["status"], "Em análise")
        self.assertEqual(self.service.occurrences()[0]["protocol"], item["protocol"])


if __name__ == "__main__":
    unittest.main()