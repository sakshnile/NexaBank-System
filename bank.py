from db import connect_db
import random
import time 

#--------- HELPER FUNCTIONS ---------
def add_history(acc_no,msg):
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO history(acc_no,message) VALUES (%s,%s)",(acc_no,msg))
        db.commit()
    finally:
        try:
         cursor.close()
         db.close()
        except:
            pass

def run_query_fetchall(query, params=()):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows

def run_query_fetchone(query, params=()):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(query, params)
    row = cursor.fetchone()
    cursor.close()
    db.close()
    return row

# -------------- Account Helper Functions --------------

def get_acc(acc_no):
    try:
        acc_no_int = int(acc_no)
    except:
        return None
    return run_query_fetchone("SELECT * FROM accounts WHERE acc_no = %s", (acc_no_int,))    

#--------- ACCOUNT CREATING ---------

def create_acc():
    print("\n ========== Create New Bank Account ==========")
    name = input("Enter Name: ").strip().title()
    if not name:
        print("Name Cannot be Empty..")
        return
    try:
        age = int(input("Enter Age: "))
    except:
        print("Invalid Age") 
        return
    if age <= 18:
        print("Age Must be 18 or Older..!")
        return
    gender = input("Enter Gender (Male/Female/Other): ").strip().title()
    address = input("Enter Address: ").strip()
    mobile = input("Enter Mobile Number: ").strip()
    if not(mobile.isdigit() and len(mobile )== 10):
        print("Invalid Mobile Number..!\n")
        return  
    email = input("Enter Email:").strip()
    aadhaar = input("Enter Aadhaar Number(12 digits): ").strip()
    if not (aadhaar.isdigit() and len(aadhaar) == 12):
        print("Invalid Aadhaar Number...!\n")
        return
    pan = input("Enter Pan Number: ").strip().upper()
    if len(pan) != 10:
        print("Invalid PAN Number..!\n")
        return  
    dob = input("Enter Date of Birth (DD-MM-YYYY): ").strip()
    acc_type = input("Account Type (Saving/Current): ").strip().title() or "Saving"
    try:
        balance = float(input("Initial Balance: "))
    except:
        balance = 0.0
    pin = input("Create a 4- Digits PIN: ").strip()
    if not (pin.isdigit() and len(pin) == 4):
        print("PIN Must Be 4 Digits...!\n")
        return
    acc_no = random.randint(100000000000,999999999999)
    db = connect_db()
    cursor = db.cursor()
    sql = """INSERT INTO accounts
    (acc_no, name, age, gender, address, mobile, email, aadhaar, pan, dob, acc_type, balance, pin, last_transaction)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    cursor.execute(sql,(acc_no,name,age,gender,address,mobile,email,aadhaar,pan,dob,acc_type,balance,pin,"Account Created"))
    db.commit()
    cursor.close()
    db.close()
    add_history(acc_no,"Account Created")
    print(f"\nAccount created! Your Account Number: {acc_no}\n")
    print("Thank You For Visiting NexaBank...!\n")

#------------------ Basic Opertions -------------------

def check_balance():
    acc_no = input("Enter Account Number: ").strip()
    acc = get_acc(acc_no)
    if not acc:
        print("Account Not Found..!")
        return
    print("\n ======== Account Summary ========")
    print(f"Account Number : {acc['acc_no']}")
    print(f"AccountHolder Name: {acc['name']}")
    print(f"Current Balance   : ₹{acc['balance']}") 
    print(f"Last Transaction  : {acc['last_transaction']}")

def deposite():
    acc_no = input("Enter Account Number: ").strip()
    acc = get_acc(acc_no)
    if not acc:
        print("Account Not Found")
        return
    if acc.get("card_Locked"):
        print("Account Card is Locked. Unlock First.")
        return
    try:
        amt = float(input("Enter Amount to Deposit: "))
    except:
        print("Invlid Amount")
        return
    if amt <= 0:
        print("Amount Must be Positive")
        return
    new_bal = acc['balance'] + amt
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE accounts SET balance=%s, last_transaction=%s WHERE acc_no=%s", (new_bal, f"Deposited ₹{amt}", int(acc_no)))
    db.commit()
    cursor.close()
    db.close()
    add_history(acc_no,f"Deposite ₹{amt}")
    print(f"Deposited ₹{amt}. New Balance: ₹{new_bal}")

def withdraw():
    acc_no = input("Enter Account Number: ").strip()
    acc = get_acc(acc_no)
    if not acc:
        print("Account Not Found")
        return
    if acc.get("card_Locked"):
        print("Account Card is Locked. Unlock First.")
        return
    try:
        amt = float(input("Enter Amount to Withdraw: "))
    except:
        print("Invlid Amount")
        return
    pin = input("Enter Your 4-Digits PIN: ").strip()
    if pin  != acc['pin']:
        print("Incorrect PIN")
        return
    if amt <= 0:
        print("Amount Must be Positive")
        return
    if amt > acc['balance']:
        print("Insufficient Balance")
        return
    new_bal = acc['balance'] - amt
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE accounts SET balance=%s, last_transaction=%s WHERE acc_no=%s", (new_bal, f"Withdrew ₹{amt}", int(acc_no)))
    db.commit()
    cursor.close()
    db.close()
    add_history(acc_no,f"Withdrew ₹{amt}")
    print("Withdrawal successful...!\n")
    print(f"Withdrew ₹{amt}.  New Balance: ₹{new_bal}\n")

# -------------------- Mini Statement ------------------------

def mini_statement():
    acc_no = input("Enter Account Number: ").strip()
    try:
        rows = run_query_fetchall("SELECT message, created_at FROM history WHERE acc_no=%s ORDER BY id DESC LIMIT 10", (int(acc_no),))
    except:
        print("No transactions found or invalid account number.")
        return
    if not rows:
        print("No transactions found")
        return
    print("\n-------- Mini Statement --------")
    for r in rows:
        created = r.get('created_at') or ''
        print(f"{created}  •  {r['message']}")
    print()    

#--------------------- UPI : Register and transfer -----------------

def register_upi():
    acc_no = input("Enter Account Number: ").strip()
    acc = get_acc(acc_no)
    if not acc:
        print("Account Not Found")
        return
    upi_id = input("Enter UPI ID (like number@bank): ").strip()
    if not upi_id:
        print("Invalid UPI ID")
        return
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO upi(upi_id,acc_no) VALUES (&s,%s)", (upi_id, int(acc_no)))
        db.commit()
    except Exception as e:
        print("Could Not Register UPI: May Already Registered or DB error.")
        db.rollback()
        cursor.close()
        db.close()
        return
    cursor.close()
    db.close()
    add_history(acc_no,"UPI Registered")
    print("UPI Registered Successfully")

def transfer_upi():
    sender = input("Enter Sender Account Number: ").strip()
    sender_acc = get_acc(sender)
    if not sender_acc:
        print("Sender Account Not Found")
        return
    if sender_acc.get("card_Locked"):
        print("Sender Account Card is Locked. Unlock First.")
        return
    upi_target = input("Reciver UPI ID: ").strip()
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM upi WHERE upi_id=%s", (upi_target,))
    target = cursor.fetchone()
    cursor.close()
    db.close()
    if not target:
        print("Target UPI Not Found")
        return
    receiver = target['acc_no']
    receiver_acc = get_acc(receiver)
    if not receiver_acc:
        print("Receiver Account Not Found")
        return
    try:
        amt = float(input("Enter Amount to Transfer: "))
    except:
        print("Invalid Amount")
        return
    pin_input = input("Enter Your 4-Digits PIN: ").strip()
    if pin_input != str(sender_acc['pin']):
        print("Incorrect PIN")
        return
    if amt <= 0:
        print("Amount Must be Positive")
        return
    if sender_acc['balance'] < amt:
        print("Insufficient Balance")
        return
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE accounts SET balance=balance-%s WHERE acc_no=%s", (amt, f"UPI Transfer ₹{amt} to {receiver}",int(sender)))
    cursor.execute("UPDATE accounts SET balance=balance+%s WHERE acc_no=%s", (amt, f"UPI Transfer ₹{amt} from {sender}",int(receiver)))
    db.commit()
    cursor.close()
    db.close()
    add_history(sender, f"Transferred ₹{amt} to {receiver} (UPI: {upi_target})")
    add_history(receiver, f"Received ₹{amt} from {sender} (UPI: {upi_target})")
    print(f"Transferred ₹{amt} to {receiver}. New Balance: ₹{sender_acc['balance'] - amt}")
    print("Transfer Successful")

# -------------------- OTP : Generate and Verify -------------------

def generate_otp():
    otp = str(random.randint(1000,9999))
    print(f"OTP for Account {acc_no} is: {otp}")
    return otp

def verify_otp():
    otp = generate_otp()
    user_otp = int(input("Enter OTP: ")).strip()
    if otp != user_otp:
        print("Incorrect OTP")
        return False
    print("OTP Verified Successfully")
    return True

#--------------------- Tansfer Money (Account to Account) --------------------

def transfer_money():
    sender = input("Enter Sender Account Number: ").strip()
    sender_acc = get_acc(sender)
    if not sender_acc:
        print("Sender Account Not Found")
        return
    if sender_acc.get("card_Locked"):
        print("Sender Account Card is Locked. Unlock First.")
        return
    receiver = input("Enter Receiver Account Number: ").strip()
    receiver_acc = get_acc(receiver)
    if not receiver_acc:
        print("Receiver Account Not Found")
        return
    try:
        amt = float(input("Enter Amount to Transfer: "))
    except:
        print("Invalid Amount")
        return
    pin_input = input("Enter Your 4-Digits PIN: ").strip()
    if pin_input != str(sender_acc['pin']):
        print("Incorrect PIN")
        return
    if amt <= 0:
        print("Amount Must be Positive")
        return
    if sender_acc['balance'] < amt:
        print("Insufficient Balance")
        return
    if amt > 10000:
        print("Large Transfer - OTP Required")
        if not verify_otp_for(sender):
            return
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE accounts SET balance=balance-%s, last_transaction=%s WHERE acc_no=%s", (amt, f"Transferred ₹{amt} to {receiver}", int(sender)))
    cursor.execute("UPDATE accounts SET balance=balance+%s, last_transaction=%s WHERE acc_no=%s", (amt, f"Received ₹{amt} from {sender}", int(receiver)))
    db.commit()
    cursor.close()
    db.close()
    add_history(sender, f"Transferred ₹{amt} to {receiver}")
    add_history(receiver, f"Received ₹{amt} from {sender}")
    print(f"Transferred ₹{amt} to {receiver}. New Balance: ₹{sender_acc['balance'] - amt}")
    print("Transfer Successful")

# --------------------- Admin : add interest Monthly---------------------

def add_interest(default_rate_per=0.5):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT acc_no, balanceFROM accounts WHERE acc_type='saving'AND card_locked=False")
    rows = cursor.fetchall()
    for row in rows:
        acc_no = row['acc_no']
        bal = float(row.get('balance') or 0.0)
        interest = (bal * float(default_rate_per) )/ 100.0
        new_bal = bal + interest
        cursor2 = db.cursor()
        cursor2.execute("UPDATE accounts SET balance=%s, last_transaction=%s WHERE acc_no=%s", (new_bal, f"Interest Added: ₹{round(interest,2)}", acc_no))
        cursor2.close()
        add_history(acc_no, f"Interest Added: ₹{round(interest,2)}")
    db.commit()
    cursor.close()
    db.close()
    print("Monthly interest applied to all Savings accounts.")

# --------------------- Loan System ---------------------

def apply_loan():
    acc_no = input("Enter Account Number: ").strip()
    acc = get_acc(acc_no)
    if not acc:
        print("Account Not Found")
        return
    try:
        principal = float(input("Enter Loan Amount: "))
    except:
        print("Invalid Amount")
        return
    try:
        interest_rate = float(input("Enter Annual Interest Rate(%) for this Loan (e.g., 10): "))
    except:
        interest_rate = 10.0
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO loans(acc_no, principal, interest_rate, outstanding, status) VALUES (%s, %s, %s, %s, %s)", (int(acc_no), principal, interest_rate, principal, 'Active'))
    db.commit()
    cursor.close()
    db.close()
    add_history(acc_no, f"Loan Applied: ₹{principal} @ {interest_rate}%")
    print("Loan application recorded. Loan will be reviewed by admin (simulated).")

def view_loans():
    acc_no = input("Enter Account Number to view loans: ").strip()
    if acc_no:
        rows = run_query_fetchall("SELECT * FROM loans WHERE acc_no=%s", (int(acc_no),))
    else:
        rows = run_query_fetchall("SELECT * FROM loans")
    if not rows:
        print("No loans found")
        return
    if rows:
        for row in rows:
            print(f"Loan ID: {row['loan_id']}")
            print(f"Account Number: {row['acc_no']}")
            print(f"Principal Amount: ₹{row['principal']}")
            print(f"Interest Rate: {row['interest_rate']}%")
            print(f"Outstanding: ₹{row['outstanding']}")
            print(f"Status: {row['status']}")
            print("-" * 30)

def repay_loan():
    try:
        loan_id = int(input("Enter Loan ID to repay: "))
    except:
        print("Invalid Loan ID")
        return
    loan = run_query_fetchone("SELECT * FROM loans WHERE loan_id=%s", (loan_id,))
    if not loan:
        print("Loan Not Found")
        return
    acc = get_acc(loan['acc_no'])
    if not acc:
        print("Account Not Found")
        return
    try:
        amt = float(input("Enter Amount to Repay: "))
    except:
        print("Invalid Amount")
        return
    if amt > acc['balance']:
        print("Insufficient Balance to Repay the Loan")
        return
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE accounts SET balance=balance-%s, last_transaction=%s WHERE acc_no=%s", (amt, f"Loan Repayment: ₹{amt} (LoanID {loan_id})", loan['acc_no']))
    new_out = float(loan.get('outstanding') or 0.0) - amt
    status = 'Closed' if new_out <= 0 else 'Active'
    cursor.execute("UPDATE loans SET outstanding=%s, status=%s WHERE loan_id=%s", (max(new_out,0.0),status, loan_id))
    db.commit()
    cursor.close()
    db.close()
    add_history(loan['acc_no'], f"Loan Repayment: ₹{amt} (LoanID {loan_id})")
    print(f"Loan Repayment Successful. New Outstanding: ₹{max(new_out,0.0)}, New Status: {status}")

# ---------------------- Card Lock / Unlock ----------------------

def lock_card():
    acc_no = input("Enter Account Number to Lock Card: ").strip()
    acc = get_acc(acc_no)
    if not acc:
        print("Account Not Found")
        return
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE accounts SET card_locked=%s, last_transaction=%s WHERE acc_no=%s", (True, "Card Locked", int(acc_no)))
    db.commit()
    cursor.close()
    db.close()
    add_history(acc_no, "Card Locked")
    print("Card Locked Successfully")

def unlock_card():
    acc_no = input("Enter Account Number to Unlock Card: ").strip()
    acc = get_acc(acc_no)
    if not acc:
        print("Account Not Found")
        return
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE accounts SET card_locked=%s, last_transaction=%s WHERE acc_no=%s", (False, "Card Unlocked", int(acc_no)))
    db.commit()
    cursor.close()
    db.close()
    add_history(acc_no, "Card Unlocked")
    print("Card Unlocked Successfully")

# ---------------------- Admin Functions ----------------------

def admin_login():
    username = input("Enter Admin Username: ").strip()
    password = input("Enter Admin Password: ").strip()
    row = run_query_fetchone("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
    return bool(row)

def view_all_acc():
    rows = run_query_fetchall("SELECT * FROM accounts")
    if not rows:
        print("No Accounts Found")
        return
    print("\n--- All Accounts ---")
    for row in rows:
        print(f"Account Number: {row['acc_no']}")
        print(f"Name: {row['name']}")
        print(f"Balance: ₹{row['balance']}")
        print(f"Account Type: {row['acc_type']}")
        print(f"Card Locked: {row['card_locked']}")
        print("-" * 30)

# ---------------------- Utility ---------------------

def search_acc():
    text = input("Search by Name or Mobile: ").strip()
    rows = run_query_fetchall("SELECT  acc_no, name, mobile, balance FROM accounts WHERE name LIKE %s OR mobile LIKE %s", (f"%{text}%", f"%{text}%"))
    print("\n--- Search Results ---")
    if not rows:
        print("No Accounts Found")
        return
    for row in rows:
        print(f"Account Number: {row['acc_no']}")
        print(f"Name: {row['name']}")
        print(f"Mobile: {row['mobile']}")
        print(f"Balance: ₹{row['balance']}")
        print("-" * 30)

# ---------------------- Additional : Change PIN & Update Profile ---------------------

def change_pin():
    acc_no = input("Enter Account Number: ").strip()
    acc = get_acc(acc_no)
    if not acc:
        print("Account Not Found")
        return
    old_pin = input("Enter current 4-digit PIN: ").strip()
    if old_pin != str(acc['pin']):
        print("Incorrect current PIN")
        return
    new_pin = input("Enter new 4-digit PIN: ").strip()
    if not (new_pin.isdigit() and len(new_pin) == 4):
        print("New PIN must be 4 digits")
        return
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE accounts SET pin=%s, last_transaction=%s WHERE acc_no=%s", (int(new_pin), "PIN Changed", int(acc_no)))
    db.commit()
    cursor.close()
    db.close()
    add_history(acc_no, "PIN Changed")
    print("PIN Changed Successfully")

def update_profile():
    acc_no = input("Enter Account Number to update profile: ").strip()
    acc = get_acc(acc_no)
    if not acc:
        print("Account Not Found")
        return
    print("Leave blank to keep existing value.")
    name = input(f"Name [{acc.get('name')}]: ").strip() or acc.get('name')
    address = input(f"Address [{acc.get('address')}]: ").strip() or acc.get('address')
    mobile = input(f"Mobile [{acc.get('mobile')}]: ").strip() or acc.get('mobile')
    email = input(f"Email [{acc.get('email')}]: ").strip() or acc.get('email')
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("UPDATE accounts SET name=%s, address=%s, mobile=%s, email=%s, last_transaction=%s WHERE acc_no=%s",
                   (name, address, mobile, email, "Profile Updated", int(acc_no)))
    db.commit()
    cursor.close()
    db.close()
    add_history(acc_no, "Profile Updated")
    print("Profile Updated Successfully")


    
