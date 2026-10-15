# NOTES.md - Susu Group Manager

## 1. Assumptions

**Mid-Cycle Member Lock:** Once the first payment is recorded or an attempt is made to close Week 1, new members cannot join. 

*Rationale:* A rotating savings group relies on a fixed number of participants so that everyone contributes the exact same amount and receives an equal lump-sum pot over a fixed cycle length. Adding members midway would unbalance the rotation and accounting.
 
**Strict Weekly Accounting:** Contributions are strictly tied to the currently active week. 

*Rationale:* Accepting advance payments for future weeks or late payments for old closed weeks without strict boundaries creates complex debt-tracking issues and breaks the weekly closure audit trail. 

**Sequential Rotation Order:** Payout recipients are automatically selected in the exact sequential order that members were added to the group. If a cycle finishes, it loops seamlessly back to the beginning.

---

## 2. Decisions Made
**Exact Decimal Arithmetic:** I used Python's built-in `decimal.Decimal` module instead of standard floats. 

*Rationale:* Standard floating-point math introduces binary rounding errors (e.g., $0.1 + 0.2 \neq 0.3$), which is unacceptable for financial software handling real currency. `Decimal` ensures exact, penny-accurate calculations.

**Clean Modular Separation:** The core business logic (`SusuGroup` class) is completely isolated inside `susu.py`, separate from the user interface (`cli.py`) and the test suite (`susu_test.py`).

*Rationale:* This separation of concerns makes the code clean, easy to test, and reusable whether accessed via a command-line menu, script, or web API.
 
**Dictionary-Based State Tracking:** I structured payment tracking using nested dictionaries (`{week_number: {member_name: amount_paid}}`). 

*Rationale:* This makes it computationally fast and straightforward to check individual balances, identify defaulters, and compile weekly reports.

---

## 3. What I Would Improve With More Time
 
**Persistent Storage:** Integrate a lightweight database (like SQLite) or a JSON file-saving mechanism so that group states, member lists, and historical payout records persist across program restarts.

**REST API Wrapper:** Wrap the core `SusuGroup` logic inside a modern web framework like FastAPI or Flask to turn it into a backend service capable of serving multiple groups.

**Automated Notifications:** Add simulated or real email/SMS notification hooks that automatically alert members about outstanding balances when a week is ready to close.