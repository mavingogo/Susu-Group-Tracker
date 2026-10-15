# Susu Rotating Savings Group Tracker

A simple Python application that manages a rotating savings group (Susu) with exact financial accounting, partial payment support, and strict weekly closure rules.

---

## How It Works

1. **Fixed Contributions:** Members agree on a fixed weekly amount in KES.
2. **Partial Payments:** Members can pay in installments during the week.
3. **Weekly Closure:** A week can only close when **every** member has paid in full. If anyone owes money, payout is blocked and the program reports who owes and how much.
4. **Orderly Payouts:** The total pot is paid out to members in the exact order they joined.

---

## Assumptions & Rules

- **Member Lock:** Once the cycle begins (payments or week closure started), no new members can be added.
- **Exact Accounting:** Uses Python's `decimal` module to prevent rounding errors.
- **Strict Week Tracking:** Payments apply only to the active week.

---

## Project Files

- `susu.py`: Core logic and validation class (`SusuGroup`).
- `cli.py` (or `main.py`): Interactive menu and demo script.
- `susu_test.py`: Automated unit tests.

---

## How to Run

### 1. Run the Interactive Program
```bash
python cli.py
```
This opens a menu where you can:
- Add members
- Record contributions
- Close weeks (and receive payouts automatically)
- See real-time status reports

### 2. Run Automated Tests
```bash
python -m unittest -v susu_test.py
```
