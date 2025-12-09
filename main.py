# main.py
from bank import *
import sys

def user_menu():
    while True:
        print("""
1. Create Account
2. Check Balance
3. Deposit
4. Withdraw
5. Mini Statement
6. Register UPI
7. UPI Transfer
8. Transfer Money (A/C)
9. Apply Loan
10. View Loans
11. Repay Loan
12. Lock Card
13. Unlock Card
14. Change PIN
15. Update Profile
16. Search Accounts
17. Exit
""")
        ch = input("Choose: ").strip()
        if ch == "1":
            create_acc()
        elif ch == "2":
            check_balance()
        elif ch == "3":
            deposit()
        elif ch == "4":
            withdraw()
        elif ch == "5":
            mini_statement()
        elif ch == "6":
            register_upi()
        elif ch == "7":
            transfer_upi()
        elif ch == "8":
            transfer_money()
        elif ch == "9":
            apply_loan()
        elif ch == "10":
            view_loans()
        elif ch == "11":
            repay_loan()
        elif ch == "12":
            lock_card()
        elif ch == "13":
            unlock_card()
        elif ch == "14":
            change_pin()
        elif ch == "15":
            update_profile()
        elif ch == "16":
            search_acc()
        elif ch == "17":
            break
        else:
            print("Invalid option. Please choose a valid number from the menu.")

def admin_menu():
    while True:
        print("""
1. View all accounts
2. Apply monthly interest
3. View all loans
4. Exit admin
""")
        ch = input("Admin choose: ").strip()
        if ch == "1":
            view_all_acc()
        elif ch == "2":
            try:
                rate = float(input("Enter monthly interest rate percent (default 0.5): ").strip() or "0.5")
            except:
                rate = 0.5
            add_interest(default_rate_per=rate)
        elif ch == "3":
            view_loans()
        elif ch == "4":
            break
        else:
            print("Invalid option. Please choose a valid number from the admin menu.")

def main():
    print("=== Welcome to NexaBank (MySQL) ===")
    while True:
        print("""
1. User Menu
2. Admin Login
3. Exit
""")
        ch = input("Choose: ").strip()
        if ch == "1":
            user_menu()
        elif ch == "2":
            if admin_login():
                print("Admin authenticated\n")
                admin_menu()
            else:
                print("Invalid admin credentials")
        elif ch == "3":
            print("Goodbye")
            sys.exit(0)
        else:
            print("Invalid option. Please enter 1, 2 or 3.")

if __name__ == "__main__":
    main()
