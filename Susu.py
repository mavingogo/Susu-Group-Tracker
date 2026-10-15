from decimal import Decimal, InvalidOperation


class SusuGroup:
    """
    Manages a single Rotating Savings and Credit Association (Susu/ROSCA) group.
    
    Rules & Mechanics:
    - Fixed weekly contribution per member in GHS handled with exact Decimals.
    - Members receive the entire pot in the exact order they joined.
    - A week can only close if every member has contributed in full.
    - Partial payments for the active week are allowed and accumulated.
    - Defaulters are reported with their exact outstanding balances.
    """

    def __init__(self, weekly_contribution):
        """
        Initialize a new Susu group.
        
        :param weekly_contribution: The fixed contribution required from each member per week.
        """
        try:
            self.weekly_contribution = Decimal(str(weekly_contribution))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(f"Invalid weekly contribution amount: '{weekly_contribution}'.")

        if self.weekly_contribution <= Decimal('0.00'):
            raise ValueError("Weekly contribution must be greater than zero.")

        self.members = []
        self.current_week = 1
        # payments format: {week_number: {member_name: Decimal('amount_paid')}}
        self.payments = {self.current_week: {}}
        self.payout_history = []
        self.started = False

    def add_member(self, name):
        """
        Add a unique member to the group before payouts begin.
        
        :param name: Unique name or identifier for the member.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Member name or ID must be a non-empty string.")

        name = name.strip()

        if name in self.members:
            raise ValueError(f"Member '{name}' is already in the group.")

        # Assumption: Once Week 1 has closed and payouts have begun, membership is locked
        # to ensure fair, equal cycle lengths and uniform pot sizes for all participants.
        if self.payout_history or self.current_week > 1:
            raise ValueError("Cannot add members after Week 1 has closed and payouts have begun.")

        self.members.append(name)
        if self.current_week in self.payments:
            self.payments[self.current_week][name] = Decimal('0.00')

    def record_payment(self, member, amount, week=None):
        """
        Record a contribution for a member for a given week.
        
        :param member: The member making the payment.
        :param amount: Monetary amount contributed.
        :param week: The week for which payment is made (defaults to current active week).
        """
        if member not in self.members:
            raise ValueError(f"Unknown member '{member}'. Member must be registered in the group first.")

        try:
            amt = Decimal(str(amount))
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError(f"Invalid monetary payment amount: '{amount}'.")

        if amt <= Decimal('0.00'):
            raise ValueError("Payment amount must be greater than zero.")

        if week is None:
            target_week = self.current_week
        else:
            try:
                target_week = int(week)
            except (ValueError, TypeError):
                raise ValueError(f"Invalid week number '{week}'. Week must be an integer.")

        # Validation: Enforce strict week consistency
        if target_week < self.current_week:
            raise ValueError(f"Week {target_week} is already closed. Current active week is {self.current_week}.")
        elif target_week > self.current_week:
            raise ValueError(f"Cannot pay in advance for future week {target_week}. Current active week is {self.current_week}.")

        if target_week not in self.payments:
            self.payments[target_week] = {m: Decimal('0.00') for m in self.members}

        current_paid = self.payments[target_week].get(member, Decimal('0.00'))
        remaining = self.weekly_contribution - current_paid

        if amt > remaining:
            raise ValueError(
                f"Payment of GHS {amt:.2f} exceeds what {member} owes for Week {target_week}. "
                f"Already paid: GHS {current_paid:.2f}, remaining owed: GHS {remaining:.2f}."
            )

        self.payments[target_week][member] = current_paid + amt

        return {
            "success": True,
            "member": member,
            "week": target_week,
            "amount_paid": amt,
            "total_paid_this_week": self.payments[target_week][member],
            "remaining_due": self.weekly_contribution - self.payments[target_week][member]
        }

    def close_week(self):
        """
        Attempts to close the current active week.
        - If all members have paid in full: pays out the entire pot to the next member in join order
          and advances to the next week.
        - If not: halts payout, remains on current week, and returns who owes and how much.
        """
        if not self.members:
            raise RuntimeError("Cannot close week with no members.")

        self.started = True
        week_payments = self.payments.get(self.current_week, {})

        # Identify any members who have not contributed their full weekly share
        owes = {}
        for member in self.members:
            paid = week_payments.get(member, Decimal('0.00'))
            if paid < self.weekly_contribution:
                owes[member] = self.weekly_contribution - paid

        if owes:
            defaulters_msg = ", ".join(f"{m} owes GHS {amt:.2f}" for m, amt in owes.items())
            return {
                "success": False,
                "message": f"Week {self.current_week} cannot close. Defaulters: {defaulters_msg}.",
                "defaulters": owes
            }

        # Calculate pot and recipient in order of joining
        pot_amount = self.weekly_contribution * len(self.members)
        recipient_index = (self.current_week - 1) % len(self.members)
        recipient = self.members[recipient_index]

        payout_record = {
            "week": self.current_week,
            "recipient": recipient,
            "amount": str(pot_amount),
            "pot_amount": pot_amount
        }
        self.payout_history.append(payout_record)

        closed_week = self.current_week
        # Advance week and initialize payments for the next week
        self.current_week += 1
        self.payments[self.current_week] = {m: Decimal('0.00') for m in self.members}

        is_cycle_complete = (len(self.payout_history) % len(self.members) == 0)

        return {
            "success": True,
            "message": f"Week {closed_week} closed successfully. {recipient} received GHS {pot_amount:.2f}.",
            "week_closed": closed_week,
            "recipient": recipient,
            "amount": str(pot_amount),
            "pot_amount": pot_amount,
            "next_week": self.current_week,
            "cycle_complete": is_cycle_complete
        }

    def get_report(self):
        """
        Generate a complete status dictionary of the group.
        Includes current week, who paid in full, who owes what, and payout history.
        """
        week_payments = self.payments.get(self.current_week, {})
        paid_in_full = []
        owes = {}

        for member in self.members:
            paid = week_payments.get(member, Decimal('0.00'))
            if paid >= self.weekly_contribution:
                paid_in_full.append(member)
            else:
                owes[member] = str(self.weekly_contribution - paid)

        scheduled_recipient = None
        if self.members:
            recipient_index = (self.current_week - 1) % len(self.members)
            scheduled_recipient = self.members[recipient_index]

        return {
            "current_week": self.current_week,
            "weekly_contribution": str(self.weekly_contribution),
            "total_members": len(self.members),
            "members": list(self.members),
            "pot_size": str(self.weekly_contribution * len(self.members)) if self.members else "0.00",
            "scheduled_recipient": scheduled_recipient,
            "paid_in_full": paid_in_full,
            "owes": owes,
            "payout_history": self.payout_history
        }

    def format_report(self):
        """
        Generate a human-readable, formatted text report suitable for CLI/terminal viewing.
        """
        report = self.get_report()
        pot = Decimal(report["pot_size"])
        contrib = Decimal(report["weekly_contribution"])
        
        lines = [
            "=" * 56,
            "               SUSU GROUP STATUS REPORT",
            "=" * 56,
            f" Current Active Week : Week {report['current_week']}",
            f" Weekly Contribution : GHS {contrib:.2f}",
            f" Total Members       : {report['total_members']} ({', '.join(report['members']) if report['members'] else 'None'})",
            f" Weekly Pot Total    : GHS {pot:.2f}",
            f" Next In Line To Win : {report['scheduled_recipient'] or 'N/A'}",
            "-" * 56,
            f" [Week {report['current_week']} Contribution Status]",
        ]

        if report["paid_in_full"]:
            lines.append(f"  * Paid in Full ({len(report['paid_in_full'])}): {', '.join(report['paid_in_full'])}")
        else:
            lines.append("  * Paid in Full: None")

        if report["owes"]:
            lines.append(f"  * Outstanding Defaulters ({len(report['owes'])}):")
            week_payments = self.payments.get(self.current_week, {})
            for member, owed_str in report["owes"].items():
                paid = week_payments.get(member, Decimal('0.00'))
                lines.append(f"      - {member:<10}: owes GHS {Decimal(owed_str):.2f} (paid GHS {paid:.2f} / {contrib:.2f})")
        else:
            lines.append("  * Outstanding Defaulters: None (All members paid in full!)")

        lines.append("-" * 56)
        lines.append(f" [Payout History ({len(report['payout_history'])} completed)]")
        if report["payout_history"]:
            for entry in report["payout_history"]:
                lines.append(f"  * Week {entry['week']}: {entry['recipient']} received GHS {Decimal(entry['amount']):.2f}")
        else:
            lines.append("  * No payouts completed yet.")
        lines.append("=" * 56)

        return "\n".join(lines)