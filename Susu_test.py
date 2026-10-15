import unittest
from decimal import Decimal
from susu import SusuGroup

class TestSusuBasic(unittest.TestCase):
    
    def test_create_and_add_members(self):
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        susu.add_member("Kofi")
        
        self.assertEqual(susu.members, ["Ama", "Kofi"])
        self.assertEqual(susu.weekly_contribution, Decimal("50.00"))

    def test_duplicate_member_error(self):
        susu = SusuGroup(50)
        susu.add_member("Ama")
        with self.assertRaises(ValueError):
            susu.add_member("Ama")

if __name__ == "__main__":
    unittest.main()