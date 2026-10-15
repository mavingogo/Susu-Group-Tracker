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
    3 members: Mavin, Henry, Jackson. Weekly contribution: 50.00 KES.
    Week 1:
      - Mavin and Henry pay 50.00
      - Jackson pays 30.00 (partial payment)
      - Attempt closing Week 1 -> fails, reports Jackson owes 20.00
      - Jackson pays 20.00
      - Close Week 1 -> succeeds, Mavin receives 150.00
      - Week 2 begins, Henry is next in line.
    """
    print("\n" + "=" * 60)
    print(" >>> RUNNING DEMO SIMULATION (SPECIFICATION WALKTHROUGH) <<<")
    print("=" * 60)

    #1.Initializing the Group
    print("\n[Step 1] Creating a Susu group with KES 50.00 weekly contribution...")
    susu = SusuGroup("50.00")
    print(f" -> Created! Weekly contribution required: KES {susu.weekly_contribution:.2f}")

    #2.Adding the Members
    print("\n[Step 2] Adding members: Mavin, Henry, Jackson (in rotation order)...")
    susu.add_member("Mavin")
    susu.add_member("Henry")
    susu.add_member("Jackson")
    print(f" -> Members added: {', '.join(susu.members)}")
    print(f" -> Weekly Pot Size: KES {Decimal(susu.get_report()['pot_size']):.2f}")

    #3.Recording the Week 1 Contributions
    print("\n[Step 3] Recording Week 1 Contributions:")
    res_mavin = susu.record_payment("Mavin", "50.00")
    print(f" -> Mavin paid KES 50.00 (Balance remaining: KES {res_mavin['remaining_due']:.2f})")

    res_henry = susu.record_payment("Henry", "50.00")
    print(f" -> Henry paid KES 50.00 (Balance remaining: KES {res_henry['remaining_due']:.2f})")

    res_jackson = susu.record_payment("Jackson", "30.00")
    print(f" -> Jackson paid KES 30.00 (Partial payment. Balance remaining: KES {res_jackson['remaining_due']:.2f})")

    # 4.Attempting to close Week 1 with defaulter
    print("\n[Step 4] Attempting to close Week 1 before all payments are complete:")
    close_attempt1 = susu.close_week()
    print(f" -> Success: {close_attempt1['success']}")
    print(f" -> Notice: {close_attempt1['message']}")
    if "defaulters" in close_attempt1:
        for member, owed in close_attempt1["defaulters"].items():
            print(f"    * Defaulter '{member}' still owes: KES {owed:.2f}")

    # 5.Overpayment rejection demonstration
    print("\n[Step 5] Validation Test - Attempting to overpay (Jackson tries to pay 35.00 when owing 20.00):")
    try:
        susu.record_payment("Jackson", "35.00")
    except ValueError as e:
        print(f" -> Correctly Rejected: {e}")

    # 6. Jackson completes his balance
    print("\n[Step 6] Jackson pays his exact remaining balance of KES 20.00:")
    res_jackson2 = susu.record_payment("Jackson", "20.00")
    print(f" -> Jackson paid KES 20.00 (Total this week: KES {res_jackson2['total_paid_this_week']:.2f}, Balance: KES {res_jackson2['remaining_due']:.2f})")

    # 7.Closing Week 1 Successfully
    print("\n[Step 7] Re-attempting to close Week 1:")
    close_attempt2 = susu.close_week()
    print(f" -> Success: {close_attempt2['success']}")
    print(f" -> Payout: {close_attempt2['message']}")
    print(f" -> Recipient: {close_attempt2['recipient']}")
    print(f" -> Amount: KES {Decimal(close_attempt2['amount']):.2f}")
    print(f" -> Current Week advanced to: Week {susu.current_week}")

    # 8.Display Status Report
    print("\n[Step 8] Generating Status Report for Week 2:")
    print(susu.format_report())

    print("\n>>> DEMO SIMULATION FINISHED SUCCESSFULLY <<<\n")

def interactive_menu():
    print_banner()
    print("Welcome! Let's set up your Susu group.")
    
    # Setup Group
    while True:
        amount_input = input("Enter weekly contribution amount in KES [Default: 50.00]: ").strip()
        if not amount_input:
            amount_input = "50.00"
        try:
            susu = SusuGroup(amount_input)
            print(f"Group created with weekly contribution: KES {susu.weekly_contribution:.2f}\n")
            break
        except ValueError as err:
            print(f"Error: {err}. Please enter a valid positive number.\n")

    #Action Loop
    while True:
        print("\n--- SUSU MANAGEMENT MENU ---")
        print(" [1] View Current Group Status & Report")
        print(" [2] Add a New Member")
        print(" [3] Record Member Contribution")
        print(" [4] Close Current Week")
        print(" [5] Run Demo Simulation (Mavin, Henry, Jackson)")
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
                print(f"Payment recorded! {member} paid KES {res['amount_paid']:.2f}. "
                      f"Total paid for Week {susu.current_week}: KES {res['total_paid_this_week']:.2f} "
                      f"(Remaining balance: KES {res['remaining_due']:.2f})")
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
                        print(f"   * {m}: owes KES {amt:.2f}")
            except RuntimeError as err:
                print(f"Error: {err}")

        elif choice == "5":
            run_demo()

        elif choice == "6":
            confirm = input("Are you sure you want to discard the current group? (y/N): ").strip().lower()
            if confirm == 'y':
                amount_input = input("Enter weekly contribution amount in KES [Default: 50.00]: ").strip() or "50.00"
                try:
                    susu = SusuGroup(amount_input)
                    print(f"New group created with weekly contribution: KES {susu.weekly_contribution:.2f}\n")
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
