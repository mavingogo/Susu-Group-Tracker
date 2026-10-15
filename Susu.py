from decimal import Decimal, ROUND_DOWN

class SusuGroup:
    def __init__(self, weekly_contribution):
        self.weekly_contribution = Decimal(str(weekly_contribution)).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
        if self.weekly_contribution <= 0:
            raise ValueError("Weekly contribution must be greater than zero.")
        
        self.members = []
        self.current_week = 1
        self.started = False
        self.payments = {1: {}}
        self.payout_history = []

    def add_member(self, name):
        name = name.strip()
        if not name:
            raise ValueError("Member name cannot be empty.")
        if self.started:
            raise RuntimeError("Cannot add members after the cycle has started.")
        if name in self.members:
            raise ValueError(f"Member '{name}' already exists.")
        
        self.members.append(name)
        self.payments[self.current_week][name] = Decimal('0.00')