from susu import SusuGroup
print("--- Starting Susu Group Demo ---")

#1.Creating a group with 50.00 KES weekly contribution
susu = SusuGroup("50.00")
print(f"Created Susu Group with weekly contribution: KES {susu.weekly_contribution}")

#2.Adding members
susu.add_member("Mavin")
susu.add_member("Gogo")
susu.add_member("Kwame")
print(f"Members added: {susu.members}")

#3.Week 1: Mavin and Gogo pay 50, Kwame pays 30 (partial payment)
print("\n--- Recording Week 1 Payments ---")
susu.record_payment("Mavin", "50.00")
susu.record_payment("Gogo", "50.00")
susu.record_payment("Kwame", "30.00")

#4.Attempting to close week 1 (should fail and report Kwame's deficit)
print("\n--- Attempting to Close Week 1 ---")
result1 = susu.close_week()
print("Closure Result:", result1)

#5.Kwame pays the remaining 20.00 balance
print("\n--- Kwame Completes Balance ---")
susu.record_payment("Kwame", "20.00")
print("Kwame paid remaining KES 20.00.")

#6.Close week 1 again (should succeed and pay Mavin)
print("\n--- Closing Week 1 Again ---")
result2 = susu.close_week()
print("Closure Result:", result2)

#7.Show final report for Week 2
print("\n--- Final Group Report ---")
report = susu.get_report()
print(report)