import unittest
from decimal import Decimal
from susu import SusuGroup


class TestSusuGroup(unittest.TestCase):

    def test_create_and_add_members(self):
        susu = SusuGroup("50.00")
        susu.add_member("Mavin")
        susu.add_member("Gogo")
        susu.add_member("Kwame")
        self.assertEqual(susu.members, ["Mavin", "Gogo", "Kwame"])
        self.assertEqual(susu.weekly_contribution, Decimal("50.00"))

    def test_invalid_weekly_contribution(self):
        with self.assertRaises(ValueError):
            SusuGroup("0.00")
        with self.assertRaises(ValueError):
            SusuGroup("-10.00")
        with self.assertRaises(ValueError):
            SusuGroup("invalid_amount")

    def test_duplicate_member_error(self):
        susu = SusuGroup(50)
        susu.add_member("Mavin")
        with self.assertRaises(ValueError):
            susu.add_member("Mavin")

    def test_invalid_member_name(self):
        susu = SusuGroup(50)
        with self.assertRaises(ValueError):
            susu.add_member("")
        with self.assertRaises(ValueError):
            susu.add_member("   ")

    def test_record_partial_payment(self):
        susu = SusuGroup("50.00")
        susu.add_member("Kwame")
        susu.record_payment("Kwame", "30.00")
        self.assertEqual(susu.payments[1]["Kwame"], Decimal("30.00"))

    def test_record_payment_unknown_member(self):
        susu = SusuGroup("50.00")
        susu.add_member("Mavin")
        with self.assertRaises(ValueError):
            susu.record_payment("John", "50.00")

    def test_record_payment_zero_or_negative(self):
        susu = SusuGroup("50.00")
        susu.add_member("Mavin")
        with self.assertRaises(ValueError):
            susu.record_payment("Mavin", "0.00")
        with self.assertRaises(ValueError):
            susu.record_payment("Mavin", "-15.00")

    def test_overpayment_rejected(self):
        susu = SusuGroup("50.00")
        susu.add_member("Mavin")
        susu.record_payment("Mavin", "30.00")
        with self.assertRaises(ValueError):
            susu.record_payment("Mavin", "30.00")

    def test_record_payment_for_specific_week(self):
        susu = SusuGroup("50.00")
        susu.add_member("Mavin")
        # Paying for current week explicitly succeeds
        res = susu.record_payment("Mavin", "50.00", week=1)
        self.assertEqual(res["week"], 1)

        # Paying for a future week before it is reached is rejected
        with self.assertRaises(ValueError):
            susu.record_payment("Mavin", "50.00", week=2)

    def test_week_cannot_close_with_defaulters(self):
        """Test that a week cannot close if a member has a partial payment."""
        susu = SusuGroup("50.00")
        susu.add_member("Mavin")
        susu.add_member("Gogo")
        susu.add_member("Kwame")

        susu.record_payment("Mavin", "50")
        susu.record_payment("Gogo", "50")
        susu.record_payment("Kwame", "30") 

        result = susu.close_week()
        self.assertFalse(result["success"])
        self.assertIn("Kwame", result["defaulters"])
        self.assertEqual(result["defaulters"]["Kwame"], Decimal("20.00"))

    def test_successful_week_closure_and_payout(self):
        """Test full week closure, payout, and advancing to the next week."""
        susu = SusuGroup("50.00")
        susu.add_member("Mavin")
        susu.add_member("Gogo")
        susu.add_member("Kwame")

        susu.record_payment("Mavin", "50")
        susu.record_payment("Gogo", "50")
        susu.record_payment("Kwame", "50")

        result = susu.close_week()
        self.assertTrue(result["success"])
        self.assertEqual(result["recipient"], "Mavin")
        self.assertEqual(result["amount"], "150.00")

        # Check that week advanced to 2
        report = susu.get_report()
        self.assertEqual(report["current_week"], 2)
        self.assertEqual(report["scheduled_recipient"], "Gogo")

    def test_cannot_add_members_after_first_payout(self):
        """Test assumption: membership is locked once payouts begin."""
        susu = SusuGroup("50.00")
        susu.add_member("Mavin")
        susu.record_payment("Mavin", "50.00")
        susu.close_week()
        self.assertEqual(susu.current_week, 2)

        with self.assertRaises(ValueError):
            susu.add_member("LateComer")

    def test_full_cycle_rotation_order(self):
        """Test full rotation across 3 weeks ensuring join order is preserved."""
        susu = SusuGroup("50.00")
        members = ["Mavin", "Gogo", "Kwame"]
        for m in members:
            susu.add_member(m)

        # Week 1: Mavin receives 150.00
        for m in members:
            susu.record_payment(m, "50.00")
        r1 = susu.close_week()
        self.assertEqual(r1["recipient"], "Mavin")
        self.assertEqual(r1["amount"], "150.00")

        # Week 2: Gogo receives 150.00
        for m in members:
            susu.record_payment(m, "50.00")
        r2 = susu.close_week()
        self.assertEqual(r2["recipient"], "Gogo")
        self.assertEqual(r2["amount"], "150.00")

        # Week 3: Kwame receives 150.00
        for m in members:
            susu.record_payment(m, "50.00")
        r3 = susu.close_week()
        self.assertEqual(r3["recipient"], "Kwame")
        self.assertEqual(r3["amount"], "150.00")
        self.assertTrue(r3["cycle_complete"])

    def test_prompt_exact_example_walkthrough(self):
        """
        Exact scenario from prompt:
        3 members (Mavin, Gogo, Kwame), weekly amount 50.00.
        Week 1: Mavin and Gogo pay 50. Kwame pays 30.
        Closing week 1 pays nothing and reports 'Kwame owes 20.00'.
        Kwame pays 20, week 1 closes, and Mavin receives 150.00.
        Week 2 begins, and Gogo is next.
        """
        susu = SusuGroup("50.00")
        susu.add_member("Mavin")
        susu.add_member("Gogo")
        susu.add_member("Kwame")

        # Week 1 payments
        susu.record_payment("Mavin", "50.00")
        susu.record_payment("Gogo", "50.00")
        susu.record_payment("Kwame", "30.00")

        # Closing week 1 pays nothing and reports Esi owes 20.00
        res1 = susu.close_week()
        self.assertFalse(res1["success"])
        self.assertIn("Kwame", res1["defaulters"])
        self.assertEqual(res1["defaulters"]["Kwame"], Decimal("20.00"))
        self.assertEqual(susu.current_week, 1)

        # Kwame pays 20.00
        susu.record_payment("Kwame", "20.00")

        # Week 1 closes, and Mavin receives 150.00
        res2 = susu.close_week()
        self.assertTrue(res2["success"])
        self.assertEqual(res2["recipient"], "Mavin")
        self.assertEqual(res2["amount"], "150.00")

        # Week 2 begins, and Gogo is next
        self.assertEqual(susu.current_week, 2)
        rep = susu.get_report()
        self.assertEqual(rep["scheduled_recipient"], "Gogo")


if __name__ == "__main__":
    unittest.main()