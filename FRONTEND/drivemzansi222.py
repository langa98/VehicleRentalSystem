from tkinter import *

root = Tk()
root.title("Drive Mzansi Car Rental System")
root.geometry("700x700")

admin_username = "Admin"
admin_password = "Admin1"

staff_accounts = {}
customer_accounts = {}
customers = []

attempts = 0

cars = {
    "Toyota Corolla": {
        "Price Per Day": 500,
        "Credit Score": 600,
        "Available": True
    },
    "Volkswagen Polo": {
        "Price Per Day": 450,
        "Credit Score": 550,
        "Available": True
    },
    "BMW 3 Series": {
        "Price Per Day": 900,
        "Credit Score": 700,
        "Available": True
    },
    "Mercedes C-Class": {
        "Price Per Day": 1000,
        "Credit Score": 750,
        "Available": True
    },
    "Ford Ranger": {
        "Price Per Day": 800,
        "Credit Score": 650,
        "Available": True
    }
}


def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


def login_page():

    global attempts
    global nameEntry
    global passwordEntry
    global message

    clear_screen()

    attempts = 0

    Label(
        root,
        text="Drive Mzansi Car Rental System",
        font="arial 24 bold"
    ).pack(pady=20)

    Label(
        root,
        text="Admin / Staff Login",
        font="arial 16 bold"
    ).pack(pady=10)

    Label(
        root,
        text="Username"
    ).pack(pady=5)

    nameEntry = Entry(
        root,
        width=35
    )
    nameEntry.pack(pady=5)

    Label(
        root,
        text="Password"
    ).pack(pady=5)

    passwordEntry = Entry(
        root,
        width=35,
        show="*"
    )
    passwordEntry.pack(pady=5)

    Checkbutton(
        root,
        text="Remember me"
    ).pack(pady=5)

    Button(
        root,
        text="SIGN IN",
        width=25,
        command=login
    ).pack(pady=10)

    Button(
        root,
        text="Customer Login",
        width=25,
        command=customer_login_page
    ).pack(pady=5)

    message = Label(
        root,
        text="",
        font="arial 11 bold"
    )
    message.pack(pady=10)


def login():

    global attempts

    username = nameEntry.get()
    password = passwordEntry.get()

    if username == "" or password == "":
        message.config(
            text="Username and password cannot be blank.",
            fg="red"
        )
        return

    if len(password) < 6:
        message.config(
            text="Password must be at least 6 characters.",
            fg="red"
        )
        return

    if username == admin_username and password == admin_password:
        admin_page()
        return

    if username in staff_accounts and staff_accounts[username] == password:
        staff_page(username)
        return

    attempts += 1

    if attempts >= 3:
        message.config(
            text="Too many failed attempts.",
            fg="red"
        )
        return

    message.config(
        text="Invalid username or password.",
        fg="red"
    )


def customer_login_page():

    clear_screen()

    Label(
        root,
        text="Customer Login",
        font="arial 24 bold"
    ).pack(pady=25)

    Label(
        root,
        text="Username"
    ).pack(pady=5)

    username_entry = Entry(
        root,
        width=35
    )
    username_entry.pack(pady=5)

    Label(
        root,
        text="Password"
    ).pack(pady=5)

    password_entry = Entry(
        root,
        width=35,
        show="*"
    )
    password_entry.pack(pady=5)

    message = Label(
        root,
        text="",
        font="arial 11 bold"
    )
    message.pack(pady=10)

    def customer_login():

        username = username_entry.get()
        password = password_entry.get()

        if username == "" or password == "":
            message.config(
                text="Please enter username and password.",
                fg="red"
            )
            return

        if username in customer_accounts and customer_accounts[username] == password:
            customer_dashboard(username)
        else:
            message.config(
                text="Invalid customer username or password.",
                fg="red"
            )

    Button(
        root,
        text="SIGN IN",
        width=25,
        command=customer_login
    ).pack(pady=5)

    Button(
        root,
        text="Create Customer Account",
        width=25,
        command=create_customer_account
    ).pack(pady=5)

    Button(
        root,
        text="Back",
        width=25,
        command=login_page
    ).pack(pady=15)


def create_customer_account():

    clear_screen()

    Label(
        root,
        text="Create Customer Account",
        font="arial 24 bold"
    ).pack(pady=20)

    Label(
        root,
        text="Username"
    ).pack(pady=5)

    username_entry = Entry(
        root,
        width=35
    )
    username_entry.pack(pady=5)

    Label(
        root,
        text="Password"
    ).pack(pady=5)

    password_entry = Entry(
        root,
        width=35,
        show="*"
    )
    password_entry.pack(pady=5)

    Label(
        root,
        text="Confirm Password"
    ).pack(pady=5)

    confirm_entry = Entry(
        root,
        width=35,
        show="*"
    )
    confirm_entry.pack(pady=5)

    message = Label(
        root,
        text="",
        font="arial 11 bold"
    )
    message.pack(pady=10)

    def save_account():

        username = username_entry.get()
        password = password_entry.get()
        confirm = confirm_entry.get()

        if username == "" or password == "" or confirm == "":
            message.config(
                text="Please complete all fields.",
                fg="red"
            )
            return

        if len(password) < 6:
            message.config(
                text="Password must be at least 6 characters.",
                fg="red"
            )
            return

        if password != confirm:
            message.config(
                text="Passwords do not match.",
                fg="red"
            )
            return

        if username in customer_accounts:
            message.config(
                text="Username already exists.",
                fg="red"
            )
            return

        customer_accounts[username] = password

        message.config(
            text="CUSTOMER ACCOUNT CREATED SUCCESSFULLY!",
            fg="green"
        )

        username_entry.delete(0, END)
        password_entry.delete(0, END)
        confirm_entry.delete(0, END)

    Button(
        root,
        text="CREATE ACCOUNT",
        width=25,
        command=save_account
    ).pack(pady=10)

    Button(
        root,
        text="Back",
        width=25,
        command=customer_login_page
    ).pack(pady=10)


def admin_page():

    clear_screen()

    Label(
        root,
        text="Admin Dashboard",
        font="arial 24 bold"
    ).pack(pady=20)

    Label(
        root,
        text="Welcome Admin",
        font="arial 15 bold"
    ).pack(pady=10)

    Button(
        root,
        text="User Account Administration",
        width=30,
        command=user_account_administration
    ).pack(pady=5)

    Button(
        root,
        text="Review Rental Applications",
        width=30,
        command=lambda: review_rentals("Admin")
    ).pack(pady=5)

    Button(
        root,
        text="Check Vehicle Availability",
        width=30,
        command=lambda: vehicle_availability("Admin")
    ).pack(pady=5)

    Button(
        root,
        text="Manage Database Tables",
        width=30,
        command=manage_tables
    ).pack(pady=5)

    Button(
        root,
        text="Manage Database Columns",
        width=30,
        command=manage_columns
    ).pack(pady=5)

    Button(
        root,
        text="View Reports",
        width=30,
        command=view_reports
    ).pack(pady=5)

    Button(
        root,
        text="Logout",
        width=30,
        command=login_page
    ).pack(pady=20)


def user_account_administration():

    clear_screen()

    Label(
        root,
        text="User Account Administration",
        font="arial 22 bold"
    ).pack(pady=20)

    Label(
        root,
        text="Create Staff Account",
        font="arial 16 bold"
    ).pack(pady=10)

    Label(
        root,
        text="Staff Username"
    ).pack(pady=5)

    username_entry = Entry(
        root,
        width=35
    )
    username_entry.pack(pady=5)

    Label(
        root,
        text="Staff Password"
    ).pack(pady=5)

    password_entry = Entry(
        root,
        width=35,
        show="*"
    )
    password_entry.pack(pady=5)

    message = Label(
        root,
        text="",
        font="arial 11 bold"
    )
    message.pack(pady=10)

    staff_list = Listbox(
        root,
        width=45,
        height=8
    )
    staff_list.pack(pady=10)

    def show_staff():

        staff_list.delete(0, END)

        for staff in staff_accounts:
            staff_list.insert(
                END,
                "Staff Username: " + staff
            )

    def create_staff():

        username = username_entry.get()
        password = password_entry.get()

        if username == "" or password == "":
            message.config(
                text="Please complete all fields.",
                fg="red"
            )
            return

        if len(password) < 6:
            message.config(
                text="Password must be at least 6 characters.",
                fg="red"
            )
            return

        if username in staff_accounts:
            message.config(
                text="Staff account already exists.",
                fg="red"
            )
            return

        staff_accounts[username] = password

        message.config(
            text="STAFF ACCOUNT CREATED SUCCESSFULLY!",
            fg="green"
        )

        username_entry.delete(0, END)
        password_entry.delete(0, END)

        show_staff()

    Button(
        root,
        text="CREATE STAFF ACCOUNT",
        width=30,
        command=create_staff
    ).pack(pady=5)

    show_staff()

    Button(
        root,
        text="Back",
        width=30,
        command=admin_page
    ).pack(pady=10)


def staff_page(staff_name):

    clear_screen()

    Label(
        root,
        text="Staff Dashboard",
        font="arial 24 bold"
    ).pack(pady=20)

    Label(
        root,
        text="Welcome " + staff_name,
        font="arial 15 bold"
    ).pack(pady=10)

    Button(
        root,
        text="Register Customer",
        width=30,
        command=lambda: register_customer(staff_name)
    ).pack(pady=5)

    Button(
        root,
        text="Review Rental Applications",
        width=30,
        command=lambda: review_rentals(staff_name)
    ).pack(pady=5)

    Button(
        root,
        text="Check Vehicle Availability",
        width=30,
        command=lambda: vehicle_availability(staff_name)
    ).pack(pady=5)

    Button(
        root,
        text="Logout",
        width=30,
        command=login_page
    ).pack(pady=20)


def register_customer(staff_name):

    clear_screen()

    Label(
        root,
        text="Register Customer",
        font="arial 24 bold"
    ).pack(pady=15)

    form = Frame(root)
    form.pack()

    Label(
        form,
        text="Customer Username"
    ).grid(row=0, column=0, pady=4)

    username_entry = Entry(
        form,
        width=35
    )
    username_entry.grid(row=1, column=0, pady=4)

    Label(
        form,
        text="Customer Name"
    ).grid(row=2, column=0, pady=4)

    name_entry = Entry(
        form,
        width=35
    )
    name_entry.grid(row=3, column=0, pady=4)

    Label(
        form,
        text="Surname"
    ).grid(row=4, column=0, pady=4)

    surname_entry = Entry(
        form,
        width=35
    )
    surname_entry.grid(row=5, column=0, pady=4)

    Label(
        form,
        text="ID Number"
    ).grid(row=6, column=0, pady=4)

    id_entry = Entry(
        form,
        width=35
    )
    id_entry.grid(row=7, column=0, pady=4)

    Label(
        form,
        text="Email Address"
    ).grid(row=8, column=0, pady=4)

    email_entry = Entry(
        form,
        width=35
    )
    email_entry.grid(row=9, column=0, pady=4)

    Label(
        form,
        text="Phone Number"
    ).grid(row=10, column=0, pady=4)

    phone_entry = Entry(
        form,
        width=35
    )
    phone_entry.grid(row=11, column=0, pady=4)

    Label(
        form,
        text="Car Being Rented"
    ).grid(row=12, column=0, pady=4)

    car_variable = StringVar()
    car_variable.set("Select Car")

    OptionMenu(
        form,
        car_variable,
        *cars.keys()
    ).grid(row=13, column=0, pady=4)

    Label(
        form,
        text="Number Of Days"
    ).grid(row=14, column=0, pady=4)

    days_entry = Entry(
        form,
        width=35
    )
    days_entry.grid(row=15, column=0, pady=4)

    Label(
        form,
        text="Available Funds"
    ).grid(row=16, column=0, pady=4)

    funds_entry = Entry(
        form,
        width=35
    )
    funds_entry.grid(row=17, column=0, pady=4)

    Label(
        form,
        text="Credit Score"
    ).grid(row=18, column=0, pady=4)

    credit_entry = Entry(
        form,
        width=35
    )
    credit_entry.grid(row=19, column=0, pady=4)

    Label(
        form,
        text="Payment Method"
    ).grid(row=20, column=0, pady=4)

    payment_variable = StringVar()
    payment_variable.set("Select Payment Method")

    OptionMenu(
        form,
        payment_variable,
        "Cash",
        "Debit Card",
        "Credit Card",
        "Bank Transfer"
    ).grid(row=21, column=0, pady=4)

    message = Label(
        root,
        text="",
        font="arial 11 bold"
    )
    message.pack(pady=5)

    def save_customer(return_dashboard=False):

        username = username_entry.get().strip()
        name = name_entry.get().strip()
        surname = surname_entry.get().strip()
        id_number = id_entry.get().strip()
        email = email_entry.get().strip()
        phone = phone_entry.get().strip()
        car = car_variable.get()
        days = days_entry.get().strip()
        funds = funds_entry.get().strip()
        credit = credit_entry.get().strip()
        payment_method = payment_variable.get()

        if username == "":
            message.config(
                text="Please enter customer username.",
                fg="red"
            )
            return

        if username not in customer_accounts:
            message.config(
                text="Customer account does not exist. Create the account first.",
                fg="red"
            )
            return

        for existing_customer in customers:
            if existing_customer["Username"] == username:
                message.config(
                    text="This customer has already been registered.",
                    fg="red"
                )
                return

        if name == "" or surname == "" or id_number == "" or email == "" or phone == "":
            message.config(
                text="Please complete all customer information.",
                fg="red"
            )
            return

        if car == "Select Car":
            message.config(
                text="Please select a car.",
                fg="red"
            )
            return

        if days == "" or funds == "" or credit == "":
            message.config(
                text="Please complete all rental information.",
                fg="red"
            )
            return

        if payment_method == "Select Payment Method":
            message.config(
                text="Please select a payment method.",
                fg="red"
            )
            return

        try:
            days_value = int(days)
            funds_value = float(funds)
            credit_value = int(credit)
        except ValueError:
            message.config(
                text="Please enter valid numbers for days, funds and credit score.",
                fg="red"
            )
            return

        if days_value <= 0:
            message.config(
                text="Number of days must be greater than 0.",
                fg="red"
            )
            return

        if funds_value < 0:
            message.config(
                text="Available funds cannot be negative.",
                fg="red"
            )
            return

        if credit_value < 0:
            message.config(
                text="Credit score cannot be negative.",
                fg="red"
            )
            return

        rental_cost = cars[car]["Price Per Day"] * days_value

        customer = {
            "Username": username,
            "Name": name,
            "Surname": surname,
            "ID Number": id_number,
            "Email": email,
            "Phone": phone,
            "Car": car,
            "Payment Method": payment_method,
            "Number of Days": days_value,
            "Available Funds": funds_value,
            "Credit Score": credit_value,
            "Rental Cost": rental_cost,
            "Amount Paid": 0,
            "Outstanding": 0,
            "Status": "Pending",
            "Reason": "Waiting for approval",
            "Registered By": staff_name
        }

        customers.append(customer)

        if return_dashboard:

            message.config(
                text="CUSTOMER INFORMATION SAVED SUCCESSFULLY!",
                fg="green"
            )

            root.after(
                700,
                lambda: staff_page(staff_name)
            )

        else:

            message.config(
                text="CUSTOMER INFORMATION SAVED SUCCESSFULLY!",
                fg="green"
            )

            username_entry.delete(0, END)
            name_entry.delete(0, END)
            surname_entry.delete(0, END)
            id_entry.delete(0, END)
            email_entry.delete(0, END)
            phone_entry.delete(0, END)
            days_entry.delete(0, END)
            funds_entry.delete(0, END)
            credit_entry.delete(0, END)

            car_variable.set("Select Car")
            payment_variable.set("Select Payment Method")

    Button(
        root,
        text="SAVE INFORMATION",
        width=30,
        height=2,
        command=lambda: save_customer(False)
    ).pack(pady=5)

    Button(
        root,
        text="SAVE & RETURN TO DASHBOARD",
        width=30,
        height=2,
        command=lambda: save_customer(True)
    ).pack(pady=5)

    Button(
        root,
        text="BACK TO DASHBOARD",
        width=30,
        height=2,
        command=lambda: staff_page(staff_name)
    ).pack(pady=5)


def review_rentals(user):

    clear_screen()

    Label(
        root,
        text="Review Rental Applications",
        font="arial 22 bold"
    ).pack(pady=15)

    if len(customers) == 0:

        Label(
            root,
            text="No rental applications available.",
            font="arial 13 bold"
        ).pack(pady=20)

    else:

        for index, customer in enumerate(customers):

            frame = Frame(
                root,
                relief=RIDGE,
                borderwidth=2
            )

            frame.pack(
                fill=X,
                padx=15,
                pady=5
            )

            Label(
                frame,
                text="Customer: " + customer["Username"],
                font="arial 11 bold"
            ).pack()

            Label(
                frame,
                text="Name: " +
                customer["Name"] +
                " " +
                customer["Surname"]
            ).pack()

            Label(
                frame,
                text="Car: " +
                customer["Car"]
            ).pack()

            Label(
                frame,
                text="Days: " +
                str(customer["Number of Days"])
            ).pack()

            Label(
                frame,
                text="Rental Cost: R" +
                str(customer["Rental Cost"])
            ).pack()

            Label(
                frame,
                text="Available Funds: R" +
                str(customer["Available Funds"])
            ).pack()

            Label(
                frame,
                text="Credit Score: " +
                str(customer["Credit Score"])
            ).pack()

            Label(
                frame,
                text="Payment Method: " +
                customer["Payment Method"]
            ).pack()

            Label(
                frame,
                text="Status: " +
                customer["Status"]
            ).pack()

            Label(
                frame,
                text="Reason: " +
                customer["Reason"]
            ).pack()

            if customer["Status"] == "Pending":

                Button(
                    frame,
                    text="APPROVE",
                    command=lambda i=index:
                    approve_rental(i, user)
                ).pack(
                    side=LEFT,
                    padx=10,
                    pady=5
                )

                Button(
                    frame,
                    text="DECLINE",
                    command=lambda i=index:
                    decline_rental(i, user)
                ).pack(
                    side=RIGHT,
                    padx=10,
                    pady=5
                )

    if user == "Admin":

        Button(
            root,
            text="Back",
            width=30,
            command=admin_page
        ).pack(pady=15)

    else:

        Button(
            root,
            text="Back",
            width=30,
            command=lambda:
            staff_page(user)
        ).pack(pady=15)


def approve_rental(index, staff_name):

    customer = customers[index]
    car = customer["Car"]

    if cars[car]["Available"] == False:

        customer["Status"] = "Declined"
        customer["Reason"] = "Car Not Available"

        review_rentals(staff_name)
        return

    if customer["Available Funds"] < customer["Rental Cost"]:

        customer["Status"] = "Declined"
        customer["Reason"] = "Insufficient Funds"

        review_rentals(staff_name)
        return

    if customer["Credit Score"] < cars[car]["Credit Score"]:

        customer["Status"] = "Declined"
        customer["Reason"] = "Credit Score Too Low"

        review_rentals(staff_name)
        return

    customer["Status"] = "Approved"
    customer["Reason"] = "Rental Approved"
    customer["Outstanding"] = customer["Rental Cost"]

    cars[car]["Available"] = False

    review_rentals(staff_name)


def decline_rental(index, staff_name):

    customer = customers[index]

    customer["Status"] = "Declined"
    customer["Reason"] = "Application Declined By Staff"

    review_rentals(staff_name)


def vehicle_availability(user):

    clear_screen()

    Label(
        root,
        text="Vehicle Availability",
        font="arial 24 bold"
    ).pack(pady=20)

    for car in cars:

        if cars[car]["Available"]:
            status = "AVAILABLE"
        else:
            status = "NOT AVAILABLE"

        Label(
            root,
            text=car +
            " - R" +
            str(cars[car]["Price Per Day"]) +
            " per day - " +
            status,
            font="arial 12"
        ).pack(pady=5)

    if user == "Admin":

        Button(
            root,
            text="Back",
            width=30,
            command=admin_page
        ).pack(pady=20)

    elif user in staff_accounts:

        Button(
            root,
            text="Back",
            width=30,
            command=lambda:
            staff_page(user)
        ).pack(pady=20)

    else:

        Button(
            root,
            text="Back",
            width=30,
            command=lambda:
            customer_dashboard(user)
        ).pack(pady=20)


def view_available_cars_customer(username):

    clear_screen()

    Label(
        root,
        text="Available Cars",
        font="arial 24 bold"
    ).pack(pady=20)

    available = False

    for car in cars:

        if cars[car]["Available"]:

            available = True

            Label(
                root,
                text=car +
                " - R" +
                str(cars[car]["Price Per Day"]) +
                " per day",
                font="arial 13"
            ).pack(pady=5)

    if not available:

        Label(
            root,
            text="No cars are currently available.",
            font="arial 13 bold"
        ).pack(pady=10)

    Button(
        root,
        text="Back",
        width=30,
        command=lambda:
        customer_dashboard(username)
    ).pack(pady=20)


def view_my_rental(username):

    clear_screen()

    Label(
        root,
        text="My Rental",
        font="arial 24 bold"
    ).pack(pady=20)

    found = False

    for customer in customers:

        if customer["Username"] == username:

            found = True

            Label(
                root,
                text="Customer: " +
                customer["Name"] +
                " " +
                customer["Surname"]
            ).pack(pady=5)

            Label(
                root,
                text="Car: " +
                customer["Car"]
            ).pack(pady=5)

            Label(
                root,
                text="Number Of Days: " +
                str(customer["Number of Days"])
            ).pack(pady=5)

            Label(
                root,
                text="Rental Cost: R" +
                str(customer["Rental Cost"])
            ).pack(pady=5)

            Label(
                root,
                text="Status: " +
                customer["Status"]
            ).pack(pady=5)

            Label(
                root,
                text="Reason: " +
                customer["Reason"]
            ).pack(pady=5)

    if not found:

        Label(
            root,
            text="No rental information found.",
            font="arial 13 bold"
        ).pack(pady=10)

    Button(
        root,
        text="Back",
        width=30,
        command=lambda:
        customer_dashboard(username)
    ).pack(pady=20)


def view_my_payment(username):

    clear_screen()

    Label(
        root,
        text="My Payment",
        font="arial 24 bold"
    ).pack(pady=20)

    found = False

    for customer in customers:

        if customer["Username"] == username:

            found = True

            rental_cost = customer["Rental Cost"]
            amount_paid = customer["Amount Paid"]

            if customer["Status"] == "Approved":
                outstanding = rental_cost - amount_paid

                if outstanding < 0:
                    outstanding = 0
            else:
                outstanding = 0

            if amount_paid == 0:
                payment_status = "OUTSTANDING"
            elif amount_paid < rental_cost:
                payment_status = "PARTIALLY PAID"
            else:
                payment_status = "PAID"

            Label(
                root,
                text="Car: " +
                customer["Car"]
            ).pack(pady=5)

            Label(
                root,
                text="Rental Cost: R" +
                str(rental_cost)
            ).pack(pady=5)

            Label(
                root,
                text="Amount Paid: R" +
                str(amount_paid)
            ).pack(pady=5)

            Label(
                root,
                text="Outstanding: R" +
                str(outstanding)
            ).pack(pady=5)

            Label(
                root,
                text="Payment Method: " +
                customer["Payment Method"]
            ).pack(pady=5)

            Label(
                root,
                text="Payment Status: " +
                payment_status
            ).pack(pady=5)

            Label(
                root,
                text="Rental Status: " +
                customer["Status"]
            ).pack(pady=5)

    if not found:

        Label(
            root,
            text="No payment information found.",
            font="arial 13 bold"
        ).pack(pady=10)

    Button(
        root,
        text="Back",
        width=30,
        command=lambda:
        customer_dashboard(username)
    ).pack(pady=20)


def customer_dashboard(username):

    clear_screen()

    Label(
        root,
        text="Customer Profile",
        font="arial 24 bold"
    ).pack(pady=20)

    Label(
        root,
        text="Welcome " + username,
        font="arial 15 bold"
    ).pack(pady=10)

    Button(
        root,
        text="View Available Cars",
        width=30,
        command=lambda:
        view_available_cars_customer(username)
    ).pack(pady=5)

    Button(
        root,
        text="View My Rental",
        width=30,
        command=lambda:
        view_my_rental(username)
    ).pack(pady=5)

    Button(
        root,
        text="View My Payment",
        width=30,
        command=lambda:
        view_my_payment(username)
    ).pack(pady=5)

    Button(
        root,
        text="Logout",
        width=30,
        command=customer_login_page
    ).pack(pady=20)


def manage_tables():

    clear_screen()

    Label(
        root,
        text="Manage Database Tables",
        font="arial 24 bold"
    ).pack(pady=20)

    Label(
        root,
        text="Customer Registration",
        font="arial 13"
    ).pack(pady=5)

    Label(
        root,
        text="Staff Accounts",
        font="arial 13"
    ).pack(pady=5)

    Label(
        root,
        text="Vehicle Information",
        font="arial 13"
    ).pack(pady=5)

    Label(
        root,
        text="Rental Applications",
        font="arial 13"
    ).pack(pady=5)

    Button(
        root,
        text="Back",
        width=30,
        command=admin_page
    ).pack(pady=20)


def manage_columns():

    clear_screen()

    Label(
        root,
        text="Manage Database Columns",
        font="arial 24 bold"
    ).pack(pady=20)

    columns = [
        "Customer Username",
        "Customer Name",
        "Surname",
        "ID Number",
        "Email Address",
        "Phone Number",
        "Car",
        "Number Of Days",
        "Available Funds",
        "Credit Score",
        "Payment Method",
        "Rental Cost",
        "Amount Paid",
        "Outstanding",
        "Status"
    ]

    for column in columns:

        Label(
            root,
            text=column
        ).pack(pady=3)

    Button(
        root,
        text="Back",
        width=30,
        command=admin_page
    ).pack(pady=20)


def view_reports():

    clear_screen()

    Label(
        root,
        text="Reports",
        font="arial 24 bold"
    ).pack(pady=20)

    total_customers = len(customers)
    approved = 0
    declined = 0
    pending = 0

    for customer in customers:

        if customer["Status"] == "Approved":
            approved += 1

        elif customer["Status"] == "Declined":
            declined += 1

        elif customer["Status"] == "Pending":
            pending += 1

    Label(
        root,
        text="Total Rental Applications: " +
        str(total_customers)
    ).pack(pady=5)

    Label(
        root,
        text="Approved Rentals: " +
        str(approved)
    ).pack(pady=5)

    Label(
        root,
        text="Declined Rentals: " +
        str(declined)
    ).pack(pady=5)

    Label(
        root,
        text="Pending Rentals: " +
        str(pending)
    ).pack(pady=5)

    Label(
        root,
        text="Staff Accounts: " +
        str(len(staff_accounts))
    ).pack(pady=5)

    Label(
        root,
        text="Customer Accounts: " +
        str(len(customer_accounts))
    ).pack(pady=5)

    Button(
        root,
        text="Back",
        width=30,
        command=admin_page
    ).pack(pady=20)


login_page()

root.mainloop()