def close_week(self):
        """
        Attempts to close the current week.
        If all members paid in full, pays out the pot to the next member and advances the week.
        If not, reports who still owes and how much.
        """
        if not self.members:
            raise RuntimeError("Cannot close week with no members.")

        self.started = True
        week_payments = self.payments[self.current_week]
        
        # Check who owes
        owes = {}
        for member in self.members:
            paid = week_payments.get(member, Decimal('0.00'))
            if paid < self.weekly_contribution:
                owes[member] = self.weekly_contribution - paid

        if owes:
            return {
                "success": False,
                "message": "Week cannot close. Not all members have paid in full.",
                "defaulters": {m: str(amt) for m, amt in owes.items()}
            }

        # Successful closure and payout
        pot_amount = self.weekly_contribution * len(self.members)
        recipient_index = (self.current_week - 1) % len(self.members)
        recipient = self.members[recipient_index]

        payout_record = {
            "week": self.current_week,
            "recipient": recipient,
            "amount": str(pot_amount)
        }
        self.payout_history.append(payout_record)

        # Advance week and initialize payments for the next week
        self.current_week += 1
        self.payments[self.current_week] = {m: Decimal('0.00') for m in self.members}

        return {
            "success": True,
            "message": f"Week {self.current_week - 1} closed successfully. {recipient} received {pot_amount}.",
            "recipient": recipient,
            "amount": str(pot_amount)
        }

    def get_report(self):
        """Generate a complete status report of the group."""
        week_payments = self.payments.get(self.current_week, {})
        paid_in_full = []
        owes = {}

        for member in self.members:
            paid = week_payments.get(member, Decimal('0.00'))
            if paid >= self.weekly_contribution:
                paid_in_full.append(member)
            else:
                owes[member] = str(self.weekly_contribution - paid)

        return {
            "current_week": self.current_week,
            "weekly_contribution": str(self.weekly_contribution),
            "members": self.members,
            "paid_in_full": paid_in_full,
            "owes": owes,
            "payout_history": self.payout_history
        }
        