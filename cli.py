#!/usr/bin/env python3
"""
CLI Menu and Demo Runner for the Susu Group Savings Tracker.
"""

import sys
from decimal import Decimal, InvalidOperation
from susu import SusuGroup


def print_banner():
    print("""
==========================================================
        ROTATING SAVINGS & CREDIT GROUP (SUSU) CLI
==========================================================
""")


def run_demo():
    """
    Executes the exact example scenario from the project requirements:
    3 members: Ama, Kofi, Esi. Weekly contribution: 50.00 GHS.
    Week 1:
      - Ama and Kofi pay 50.00
      - Esi pays 30.00 (partial payment)
      - Attempt closing Week 1 -> fails, reports Esi owes 20.00
      - Esi pays 20.00
      - Close Week 1 -> succeeds, Ama receives 150.00
      - Week 2 begins, Kofi is next in line.
    """
    print("\n" + "=" * 60)
    print(" >>> RUNNING DEMO SIMULATION (SPECIFICATION WALKTHROUGH) <<<")
    print("=" * 60)

    # 1. Initialize Group
    print("\n[Step 1] Creating a Susu group with GHS 50.00 weekly contribution...")
    susu = SusuGroup("50.00")
    print(f" -> Created! Weekly contribution required: GHS {susu.weekly_contribution:.2f}")

    # 2. Add members
    print("\n[Step 2] Adding members: Ama, Kofi, Esi (in rotation order)...")
    susu.add_member("Ama")
    susu.add_member("Kofi")
    susu.add_member("Esi")
    print(f" -> Members added: {', '.join(susu.members)}")
    print(f" -> Weekly Pot Size: GHS {Decimal(susu.get_report()['pot_size']):.2f}")

    # 3. Week 1 Payments
    print("\n[Step 3] Recording Week 1 Contributions:")
    res_ama = susu.record_payment("Ama", "50.00")
    print(f" -> Ama paid GHS 50.00 (Balance remaining: GHS {res_ama['remaining_due']:.2f})")

    res_kofi = susu.record_payment("Kofi", "50.00")
    print(f" -> Kofi paid GHS 50.00 (Balance remaining: GHS {res_kofi['remaining_due']:.2f})")

    res_esi = susu.record_payment("Esi", "30.00")
    print(f" -> Esi paid GHS 30.00 (Partial payment. Balance remaining: GHS {res_esi['remaining_due']:.2f})")

    # 4. Attempt week closure with defaulter
    print("\n[Step 4] Attempting to close Week 1 before all payments are complete:")
    close_attempt1 = susu.close_week()
    print(f" -> Success: {close_attempt1['success']}")
    print(f" -> Notice: {close_attempt1['message']}")
    if "defaulters" in close_attempt1:
        for member, owed in close_attempt1["defaulters"].items():
            print(f"    * Defaulter '{member}' still owes: GHS {owed:.2f}")

    # 5. Overpayment rejection demonstration
    print("\n[Step 5] Validation Test - Attempting to overpay (Esi tries to pay 35.00 when owing 20.00):")
    try:
        susu.record_payment("Esi", "35.00")
    except ValueError as e:
        print(f" -> Correctly Rejected: {e}")

    # 6. Esi completes her balance
    print("\n[Step 6] Esi pays her exact remaining balance of GHS 20.00:")
    res_esi2 = susu.record_payment("Esi", "20.00")
    print(f" -> Esi paid GHS 20.00 (Total this week: GHS {res_esi2['total_paid_this_week']:.2f}, Balance: GHS {res_esi2['remaining_due']:.2f})")

    # 7. Close week 1 successfully
    print("\n[Step 7] Re-attempting to close Week 1:")
    close_attempt2 = susu.close_week()
    print(f" -> Success: {close_attempt2['success']}")
    print(f" -> Payout: {close_attempt2['message']}")
    print(f" -> Recipient: {close_attempt2['recipient']}")
    print(f" -> Amount: GHS {Decimal(close_attempt2['amount']):.2f}")
    print(f" -> Current Week advanced to: Week {susu.current_week}")

    # 8. Display Status Report
    print("\n[Step 8] Generating Status Report for Week 2:")
    print(susu.format_report())

    print("\n>>> DEMO SIMULATION FINISHED SUCCESSFULLY <<<\n")


def interactive_menu():
    print_banner()
    print("Welcome! Let's set up your Susu group.")
    
    # Setup Group
    while True:
        amount_input = input("Enter weekly contribution amount in GHS [Default: 50.00]: ").strip()
        if not amount_input:
            amount_input = "50.00"
        try:
            susu = SusuGroup(amount_input)
            print(f"Group created with weekly contribution: GHS {susu.weekly_contribution:.2f}\n")
            break
        except ValueError as err:
            print(f"Error: {err}. Please enter a valid positive number.\n")

    # Main Action Loop
    while True:
        print("\n--- SUSU MANAGEMENT MENU ---")
        print(" [1] View Current Group Status & Report")
        print(" [2] Add a New Member")
        print(" [3] Record Member Contribution")
        print(" [4] Close Current Week")
        print(" [5] Run Demo Simulation (Ama, Kofi, Esi)")
        print(" [6] Reset & Create a New Group")
        print(" [0] Exit")

        choice = input("Select an option (0-6): ").strip()

        if choice == "1":
            print("\n" + susu.format_report())

        elif choice == "2":
            name = input("Enter member name or unique ID: ").strip()
            try:
                susu.add_member(name)
                print(f"Success: Member '{name}' added. Current roster: {', '.join(susu.members)}")
            except ValueError as err:
                print(f"Failed to add member: {err}")

        elif choice == "3":
            if not susu.members:
                print("Error: Please add members to the group first before recording payments.")
                continue

            print(f"Active members: {', '.join(susu.members)}")
            member = input("Enter member name: ").strip()
            amount_str = input(f"Enter contribution amount for Week {susu.current_week} in GHS: ").strip()
            try:
                res = susu.record_payment(member, amount_str)
                print(f"Payment recorded! {member} paid GHS {res['amount_paid']:.2f}. "
                      f"Total paid for Week {susu.current_week}: GHS {res['total_paid_this_week']:.2f} "
                      f"(Remaining balance: GHS {res['remaining_due']:.2f})")
            except ValueError as err:
                print(f"Payment rejected: {err}")

        elif choice == "4":
            try:
                result = susu.close_week()
                if result["success"]:
                    print("\n SUCCESS! Week closed.")
                    print(f" {result['message']}")
                    print(f" Next week is now Week {susu.current_week}.")
                else:
                    print("\n CANNOT CLOSE WEEK:")
                    print(f" {result['message']}")
                    print(" Defaulters:")
                    for m, amt in result["defaulters"].items():
                        print(f"   * {m}: owes GHS {amt:.2f}")
            except RuntimeError as err:
                print(f"Error: {err}")

        elif choice == "5":
            run_demo()

        elif choice == "6":
            confirm = input("Are you sure you want to discard the current group? (y/N): ").strip().lower()
            if confirm == 'y':
                amount_input = input("Enter weekly contribution amount in GHS [Default: 50.00]: ").strip() or "50.00"
                try:
                    susu = SusuGroup(amount_input)
                    print(f"New group created with weekly contribution: GHS {susu.weekly_contribution:.2f}\n")
                except ValueError as err:
                    print(f"Error: {err}")

        elif choice == "0":
            print("Exiting Susu Tracker. Goodbye!")
            sys.exit(0)

        else:
            print("Invalid option. Please choose a number from 0 to 6.")


def main():
    if "--demo" in sys.argv:
        run_demo()
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
