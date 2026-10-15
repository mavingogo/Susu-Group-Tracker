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

    def test_invalid_weekly_contribution(self):
        with self.assertRaises(ValueError):
            SusuGroup("0.00")
        with self.assertRaises(ValueError):
            SusuGroup("-10.00")
        with self.assertRaises(ValueError):
            SusuGroup("invalid_amount")

    def test_duplicate_member_error(self):
        susu = SusuGroup(50)
        susu.add_member("Ama")
        with self.assertRaises(ValueError):
            susu.add_member("Ama")

    def test_invalid_member_name(self):
        susu = SusuGroup(50)
        with self.assertRaises(ValueError):
            susu.add_member("")
        with self.assertRaises(ValueError):
            susu.add_member("   ")

    def test_record_partial_payment(self):
        susu = SusuGroup("50.00")
        susu.add_member("Esi")
        susu.record_payment("Esi", "30.00")
        self.assertEqual(susu.payments[1]["Esi"], Decimal("30.00"))

    def test_record_payment_unknown_member(self):
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        with self.assertRaises(ValueError):
            susu.record_payment("UnknownPerson", "50.00")

    def test_record_payment_zero_or_negative(self):
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        with self.assertRaises(ValueError):
            susu.record_payment("Ama", "0.00")
        with self.assertRaises(ValueError):
            susu.record_payment("Ama", "-15.00")

    def test_overpayment_rejected(self):
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        susu.record_payment("Ama", "30.00")
        with self.assertRaises(ValueError):
            susu.record_payment("Ama", "30.00")  # 30 + 30 = 60 > 50

    def test_record_payment_for_specific_week(self):
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        # Paying for current week explicitly succeeds
        res = susu.record_payment("Ama", "50.00", week=1)
        self.assertEqual(res["week"], 1)

        # Paying for a future week before it is reached is rejected
        with self.assertRaises(ValueError):
            susu.record_payment("Ama", "50.00", week=2)

    def test_week_cannot_close_with_defaulters(self):
        """Test that a week cannot close if a member has a partial payment."""
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        susu.add_member("Kofi")
        susu.add_member("Esi")

        susu.record_payment("Ama", "50")
        susu.record_payment("Kofi", "50")
        susu.record_payment("Esi", "30")  # Partial payment

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
        self.assertEqual(report["scheduled_recipient"], "Kofi")

    def test_cannot_add_members_after_first_payout(self):
        """Test assumption: membership is locked once payouts begin."""
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        susu.record_payment("Ama", "50.00")
        susu.close_week()
        self.assertEqual(susu.current_week, 2)

        with self.assertRaises(ValueError):
            susu.add_member("LateComer")

    def test_full_cycle_rotation_order(self):
        """Test full rotation across 3 weeks ensuring join order is preserved."""
        susu = SusuGroup("50.00")
        members = ["Ama", "Kofi", "Esi"]
        for m in members:
            susu.add_member(m)

        # Week 1: Ama receives 150.00
        for m in members:
            susu.record_payment(m, "50.00")
        r1 = susu.close_week()
        self.assertEqual(r1["recipient"], "Ama")
        self.assertEqual(r1["amount"], "150.00")

        # Week 2: Kofi receives 150.00
        for m in members:
            susu.record_payment(m, "50.00")
        r2 = susu.close_week()
        self.assertEqual(r2["recipient"], "Kofi")
        self.assertEqual(r2["amount"], "150.00")

        # Week 3: Esi receives 150.00
        for m in members:
            susu.record_payment(m, "50.00")
        r3 = susu.close_week()
        self.assertEqual(r3["recipient"], "Esi")
        self.assertEqual(r3["amount"], "150.00")
        self.assertTrue(r3["cycle_complete"])

    def test_prompt_exact_example_walkthrough(self):
        """
        Exact scenario from prompt:
        3 members (Ama, Kofi, Esi), weekly amount 50.00.
        Week 1: Ama and Kofi pay 50. Esi pays 30.
        Closing week 1 pays nothing and reports 'Esi owes 20.00'.
        Esi pays 20, week 1 closes, and Ama receives 150.00.
        Week 2 begins, and Kofi is next.
        """
        susu = SusuGroup("50.00")
        susu.add_member("Ama")
        susu.add_member("Kofi")
        susu.add_member("Esi")

        # Week 1 payments
        susu.record_payment("Ama", "50.00")
        susu.record_payment("Kofi", "50.00")
        susu.record_payment("Esi", "30.00")

        # Closing week 1 pays nothing and reports Esi owes 20.00
        res1 = susu.close_week()
        self.assertFalse(res1["success"])
        self.assertIn("Esi", res1["defaulters"])
        self.assertEqual(res1["defaulters"]["Esi"], Decimal("20.00"))
        self.assertEqual(susu.current_week, 1)

        # Esi pays 20.00
        susu.record_payment("Esi", "20.00")

        # Week 1 closes, and Ama receives 150.00
        res2 = susu.close_week()
        self.assertTrue(res2["success"])
        self.assertEqual(res2["recipient"], "Ama")
        self.assertEqual(res2["amount"], "150.00")

        # Week 2 begins, and Kofi is next
        self.assertEqual(susu.current_week, 2)
        rep = susu.get_report()
        self.assertEqual(rep["scheduled_recipient"], "Kofi")


if __name__ == "__main__":
    unittest.main()