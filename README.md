# 🚗 Drive Mzansi – Vehicle Rental Management System

> **A full-stack vehicle rental management system built with Flask, Python, HTML/CSS, Jinja2 and Microsoft SQL Server.**

Drive Mzansi is a vehicle rental management system designed to manage the complete rental workflow — from customer registration and vehicle availability to booking management, payments, returns, overdue rentals, reporting and database administration.

The project combines a **Flask web application**, **Python backend**, and **Microsoft SQL Server database**, with role-based functionality for **Customers, Staff and Administrators**.

---

## 🛠️ Technology Stack

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python\&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask\&logoColor=white)
![SQL Server](https://img.shields.io/badge/Microsoft-SQL%20Server-red?logo=microsoftsqlserver\&logoColor=white)
![HTML](https://img.shields.io/badge/HTML5-E34F26?logo=html5\&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-1572B6?logo=css3\&logoColor=white)

### Core Technologies

| Component         | Technology                         |
| ----------------- | ---------------------------------- |
| Frontend          | HTML, CSS and Jinja2 templates     |
| Backend           | Python + Flask                     |
| Database          | Microsoft SQL Server               |
| Database Access   | Python database connectivity + SQL |
| Authentication    | Role-based authentication          |
| Password Security | Password hashing                   |
| Styling           | CSS                                |
| Graphics          | SVG and JPG assets                 |
| Reporting         | SQL queries + Flask dashboards     |
| Version Control   | Git + GitHub                       |

---

# 📌 Project Overview

Drive Mzansi was developed as a **Vehicle Rental Management System** capable of handling the major operations involved in a rental business.

The system manages:

* Customer accounts
* Staff accounts
* Administrator accounts
* Vehicle categories
* Vehicles
* Vehicle availability
* Booking requests
* Booking approval
* Payments
* Vehicle returns
* Overdue rentals
* Late fees
* Operational reports
* Financial reports
* Customer management
* Database structure management

The application communicates directly with the **VehicleRental SQL Server database**, allowing information entered through the website to be stored and retrieved from the relational database.

---

# 👥 User Roles

The system implements different functionality depending on the user's role.

## 👤 Visitors

Visitors can:

* View the home page
* Browse vehicles available today
* View vehicles grouped by category
* Register for an account
* Log in to the system

Visitors cannot make bookings until they authenticate.

---

## 🧑‍💼 Customers

Customers can:

* Browse available vehicles
* Search vehicle availability by date
* View rental totals
* Submit booking requests
* View their bookings
* View payment information
* Monitor booking status
* Receive warnings for overdue vehicles

The customer workflow is designed around:

**Search → Select Vehicle → Request Booking → Payment → Rental → Return**

---

## 👷 Staff

Staff members have access to operational rental-management functionality.

### Staff Dashboard

Staff can:

* Monitor bookings
* Approve booking requests
* Record full payments
* Cancel bookings
* Mark vehicles as returned
* Monitor overdue vehicles
* Manage vehicles
* Manage customers

### Operational Reports

Staff have access to:

1. Fleet Status
2. Bookings in the Next 7 Days
3. Overdue Cars
4. Bookings With Money Owing
5. Bookings by Status

Staff deliberately do **not** have access to financial reports.

---

## 👑 Administrators

Administrators have all staff capabilities plus additional management functionality.

### Financial Reports

Administrators can access:

1. Revenue by Month
2. Revenue by Vehicle Category
3. Vehicle Performance
4. Top Customers
5. Late Returns by Customer

### Additional Administration

Administrators can also:

* Delete customers who are not currently renting
* Delete vehicles that are not currently rented
* Preserve rental history when appropriate
* Create database tables
* Remove database tables
* Add columns
* Drop columns
* Add rows
* Edit rows
* Delete rows

This provides administrators with direct database-structure management through the application.

---

# ⚙️ Automated System Processes

The application includes automated rental-management logic that runs:

* Every **5 minutes while the website is running**
* When relevant pages are opened
* When the administrator selects **Run Automation Now**

### Automated processes include:

### 1. Expired Pending Requests

Pending booking requests whose start date has already passed are automatically cancelled.

### 2. Unpaid Approved Bookings

Approved bookings with no payment whose start date has passed are automatically cancelled.

This releases the vehicle dates for other customers.

### 3. Vehicle Status Management

A vehicle becomes:

```text
Available → Rented
```

when it has a fully paid approved booking beginning.

The vehicle remains:

```text
Rented
```

until staff explicitly select **Mark Returned**.

This prevents an overdue vehicle from accidentally becoming available for another customer.

Vehicles already marked **Maintenance** are not overwritten by the automation.

---

# ⏰ Late Return Management

Late returns are handled separately from normal completed rentals.

A booking is **not considered completed simply because the end date has passed**.

Staff must explicitly select:

> **Mark Returned**

If the end date passes before the vehicle is returned, the booking is displayed as **Overdue**.

Overdue information appears in:

* Staff dashboard
* Bookings page
* Overdue report
* Customer account
* Vehicle availability logic

### Late Fees

The system calculates:

> **Late Fee = Number of Days Late × Vehicle Daily Rate**

The late fee is saved to the booking and becomes part of the customer's outstanding balance.

---

# 🗄️ Database

The application uses **Microsoft SQL Server** with the database:

```text
VehicleRental
```

The project uses the:

```text
Rental
```

schema.

Major entities include:

* Customer
* User
* Vehicle
* VehicleCategory
* Booking
* Payment

The database contains:

* Primary keys
* Foreign keys
* Unique constraints
* Check constraints
* Identity columns
* Referential integrity
* Indexes
* Views
* Authentication data
* Sample/demo data

The complete database setup is provided in:

```text
VehicleRental_Setup.sql
```

---

# 🧩 Database Design

The database design was supported by:

* Entity Relationship Diagram
* ERD attribute documentation
* Normalization analysis
* Data dictionary
* SQL table definitions
* Constraints
* Relationships
* Indexes
* Database views

The supporting documentation can be found in:

```text
Documentation/
```

---

# 📊 Database Views & Reporting

The system makes use of database views and SQL queries to support application functionality and reporting.

Examples include:

* Customer booking details
* Payment information
* Vehicle availability
* Fleet status
* Upcoming bookings
* Overdue vehicles
* Outstanding balances
* Revenue analysis
* Customer performance
* Vehicle performance

---

# 🔐 Authentication & Security

The application implements role-based authentication for:

```text
Customer
Staff
Admin
```

Passwords are stored using password hashing rather than plain-text storage.

Database credentials can be configured through environment variables rather than being hard-coded.

---

# 📂 Project Structure

```text
VehicleRentalSystem/
│
├── Documentation/
│   ├── Car_Rental_ERD.pdf
│   ├── DB Normalization.docx
│   ├── DriveMzansi_DataDictionary.docx
│   ├── DriveMzansi_Pitch_Rentals (final).pptx
│   └── vehicle_rental_er_attributes.pdf
│
├── static/
│   ├── cars/
│   │   ├── economy.svg
│   │   ├── luxury.svg
│   │   ├── sedan.svg
│   │   └── suv.svg
│   ├── customer-bg.jpg
│   ├── favicon.svg
│   ├── login-bg.jpg
│   └── style.css
│
├── templates/
│
├── admin_tables.py
├── app.py
├── db.py
├── password.py
├── requirements.txt
├── VehicleRental_Setup.sql
├── README.md
└── .gitignore
```

---

# 🚀 Installation & Setup

## 1. Clone the repository

```bash
git clone https://github.com/langa98/VehicleRentalSystem.git
cd VehicleRentalSystem
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure SQL Server

Create/configure the `VehicleRental` database in SQL Server.

Run:

```text
VehicleRental_Setup.sql
```

The script creates the required database structures, tables, constraints, sample data, views and supporting database objects.

---

# 🔌 Database Connection

Database connection settings are configured in:

```text
db.py
```

The default configuration uses Windows Authentication with a local SQL Server instance.

Environment variables can be used to override the connection:

```text
VR_SERVER
VR_DATABASE
VR_USER
VR_PASSWORD
```

A `SECRET_KEY` should also be configured for secure session management.

---

# ▶️ Running the Website

With the virtual environment activated:

```bash
python app.py
```

The website will normally be available at:

```text
http://127.0.0.1:5000
```

Open the address in a web browser.

---

# 📚 Project Documentation

The repository includes supporting documentation covering the database design and project development.

### ERD

```text
Documentation/Car_Rental_ERD.pdf
```

### Normalization

```text
Documentation/DB Normalization.docx
```

### Data Dictionary

```text
Documentation/DriveMzansi_DataDictionary.docx
```

### ERD Attributes

```text
Documentation/vehicle_rental_er_attributes.pdf
```

### Project Presentation

```text
Documentation/DriveMzansi_Pitch_Rentals (final).pptx
```

---

# 🧪 Testing & Validation

The system was developed with validation of:

* Database constraints
* User authentication
* Role permissions
* Vehicle availability
* Booking dates
* Payment requirements
* Booking status transitions
* Vehicle status transitions
* Overdue rentals
* Late fees
* Database operations
* Reporting queries

The database setup is designed to support repeatable development and testing rather than requiring the database to be manually rebuilt for every test.

---

# 📈 Project Scope

This project goes beyond a basic vehicle-booking interface.

The implementation covers multiple layers of a software system:

```text
┌─────────────────────────────┐
│       Web Interface         │
│      Flask + HTML/CSS       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Application Logic     │
│          Python/Flask       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       Database Layer        │
│       Microsoft SQL Server  │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Tables • Constraints       │
│  Views • Indexes • Queries  │
│  Relationships • Reports    │
└─────────────────────────────┘
```

The project demonstrates work across:

* Web development
* Backend development
* Database design
* SQL
* Authentication
* Role-based access control
* CRUD operations
* Reporting
* Business logic
* Automation
* Data validation
* Database administration
* Software documentation

---

# 🤝 Contributing

Pull requests are welcome.

Possible future improvements include:

* UI/UX improvements
* Additional reporting
* Performance optimizations
* Additional automated processes
* Notification systems
* API development
* Additional modules

---

# 📜 License

This project is provided for **educational and personal use**.

No warranty is expressed or implied.
