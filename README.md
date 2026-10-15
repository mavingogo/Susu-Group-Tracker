# Rotating Savings Group (Susu) Tracker

A Python application that manages a single Rotating Savings and Credit Association (Susu / ROSCA).

---

## How It Works

A **Susu** operates on a cyclical, collective savings model:
1. A fixed group of members agree to contribute a fixed monetary amount in Ghana Cedis (**GHS**) each week.
2. Each week, every member must contribute their share. Partial payments are accepted and accumulated.
3. Once all members have contributed in full, the entire accumulated weekly pot is paid out to one member.
4. Payouts rotate strictly in the order members joined the group (first to join receives the pot in Week 1, second in Week 2, etc.).
5. If any member has not paid their full share when closing the week, the pot is **not** paid out, the week does **not** advance, and a report lists who still owes and the exact amount due.

---

## Assumptions & Sensible Rules

Per project specifications, rules chosen for unspecified edge cases are explicitly defined below:

1. **Member Addition Lock (Mid-Cycle Addition)**:
   - In a Susu group, the total pot value (`pot = weekly_contribution * number_of_members`) and cycle length are predetermined so that every member pays the same total and receives the exact same lump-sum pot.
   - *Rule*: Members can be added during group setup in Week 1 before payouts begin. Once Week 1 has closed and the first payout has been disbursed, membership is locked for the remainder of that rotation cycle. Attempting to add members mid-cycle raises a `ValueError`.
2. **Strict Week Tracking**:
   - *Rule*: Contributions must be recorded for the currently active week (`target_week == current_week`). Advance payments for future weeks and late contributions for past already-closed weeks are rejected to ensure balance transparency and prevent out-of-order accounting states.
3. **Exact Currency & Precision**:
   - *Rule*: All monetary values are handled using Python's `decimal.Decimal` module. No floating-point arithmetic is used, preventing binary rounding anomalies (e.g. `0.1 + 0.2 != 0.3`).
4. **Member Identification**:
   - *Rule*: Member names or IDs must be non-empty strings. Leading and trailing whitespace is trimmed. Duplicates are strictly rejected.
5. **Cycle Completion**:
   - *Rule*: A full cycle is reached when `number_of_completed_payouts == number_of_members`. When this occurs, the group status flags `cycle_complete = True`.

---

## Rules & Validation

| Scenario | Behavior |
| :--- | :--- |
| **Invalid Weekly Amount** | Negative, zero, or non-numeric contributions are rejected (`ValueError`). |
| **Duplicate Member** | Adding a member who already exists is rejected (`ValueError`). |
| **Empty Member Name** | Empty or whitespace-only names/IDs are rejected (`ValueError`). |
| **Unknown Member Payment** | Payments from unregistered individuals are rejected (`ValueError`). |
| **Zero / Negative Payment** | Payments $\le 0.00$ are rejected (`ValueError`). |
| **Overpayment** | Contributing more than a member owes for the active week is rejected (`ValueError`). |
| **Defaulters at Week Close** | If any member owes balance, payout is blocked, week does not advance, and defaulters are listed (`success = False`). |
| **Close Week Without Members** | Attempting to close an empty group raises `RuntimeError`. |

---

## Project Structure

- [susu.py](file:///c:/Susu%20Project/susu.py): Core `SusuGroup` domain class with financial logic, validation, and reporting.
- [cli.py](file:///c:/Susu%20Project/cli.py): Interactive command-line menu and demonstration simulation runner.
- [main.py](file:///c:/Susu%20Project/main.py): Standard entry point that runs the CLI application.
- [live.py](file:///c:/Susu%20Project/live.py): Standalone live demo script illustrating the core API.
- [susu_test.py](file:///c:/Susu%20Project/susu_test.py): Unit test suite covering all specifications, error conditions, and edge cases.

---

## How to Run

### 1. Run the Interactive CLI Menu
```bash
python cli.py
# or
python main.py
```
This opens an interactive menu allowing you to:
- View real-time group status reports
- Add members
- Record contributions (with partial payment support)
- Close the current week and trigger payouts
- Run the built-in walkthrough simulation

### 2. Run the Automated Demo Simulation
To run the exact example walkthrough directly without interactive prompts:
```bash
python cli.py --demo
# or
python live.py
```

### 3. Run Unit Tests
```bash
python -m unittest -v susu_test.py
```

---

## Example Walkthrough

```python
from susu import SusuGroup

# 1. Create a group with GHS 50.00 weekly contribution
susu = SusuGroup("50.00")

# 2. Add members in order of join
susu.add_member("Ama")
susu.add_member("Kofi")
susu.add_member("Esi")

# 3. Week 1: Ama and Kofi pay 50.00 each, Esi pays 30.00 (partial)
susu.record_payment("Ama", "50.00")
susu.record_payment("Kofi", "50.00")
susu.record_payment("Esi", "30.00")

# 4. Closing Week 1 fails because Esi still owes 20.00
result = susu.close_week()
# result["success"] -> False
# result["defaulters"] -> {"Esi": Decimal("20.00")}

# 5. Esi completes her remaining balance
susu.record_payment("Esi", "20.00")

# 6. Week 1 closes successfully; Ama receives 150.00 pot
result = susu.close_week()
# result["success"] -> True
# result["recipient"] -> "Ama"
# result["amount"] -> "150.00"

# 7. Week 2 begins, Kofi is next scheduled recipient
report = susu.get_report()
# report["current_week"] -> 2
# report["scheduled_recipient"] -> "Kofi"
```
