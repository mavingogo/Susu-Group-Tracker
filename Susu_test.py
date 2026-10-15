import unittest
from decimal import Decimal
from susu import SusuGroup

class TestSusuGroup(unittest.TestCase):
    
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

    def test_record_partial_payment(self):
        susu = SusuGroup("50.00")
        susu.add_member("Esi")
        susu.record_payment("Esi", "30.00")
        self.assertEqual(susu.payments[1]["Esi"], Decimal("30.00"))

    def test_week_cannot_close_with_defaulters(self):
        """Test that a week cannot close if a member has a partial payment."""
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        susu.add_member("Kofi")
        susu.add_member("Esi")
        
        susu.record_payment("Ama", "50")
        susu.record_payment("Kofi", "50")
        susu.record_payment("Esi", "30") # Partial payment
        
        result = susu.close_week()
        self.assertFalse(result["success"])
        self.assertIn("Esi", result["defaulters"])
        self.assertEqual(result["defaulters"]["Esi"], Decimal("20.00"))

    def test_successful_week_closure_and_payout(self):
        """Test full week closure, payout, and advancing to the next week."""
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        susu.add_member("Kofi")
        susu.add_member("Esi")
        
        susu.record_payment("Ama", "50")
        susu.record_payment("Kofi", "50")
        susu.record_payment("Esi", "50")
        
        result = susu.close_week()
        self.assertTrue(result["success"])
        self.assertEqual(result["recipient"], "Ama")
        self.assertEqual(result["amount"], "150.00")
        
        # Check that week advanced to 2
        report = susu.get_report()
        self.assertEqual(report["current_week"], 2)

    def test_overpayment_rejected(self):
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        susu.record_payment("Ama", "30.00")
        with self.assertRaises(ValueError):
            susu.record_payment("Ama", "30.00")

if __name__ == "__main__":
    unittest.main()