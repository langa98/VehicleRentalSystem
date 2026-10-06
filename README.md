# Drive Mzansi – website

Flask website on the same `VehicleRental` SQL Server database as the Tkinter app.

## Run
1. Run `SQL/00_FullSetup.sql` once in SQL Server.
2. In this folder (with the virtual environment active): `pip install -r requirements.txt`, then `python app.py`.
3. Open http://127.0.0.1:5000

Connection settings are in `db.py` (Windows authentication to `localhost` by default; override with `VR_SERVER`,
`VR_DATABASE`, `VR_USER`, `VR_PASSWORD`). Set `SECRET_KEY` to keep logins valid across restarts.

## What visitors, customers and staff see
- **Visitors:** the home page lists the cars that are available today, grouped by category, view only. Request booking sends them to log in or register.
- **Customers:** the same list plus a date search (shows cars free on those dates, with the total), booking requests, My bookings and My payments.
- **Staff (workers):** dashboard (no money figures), bookings (approve, record full payment, mark returned, cancel), an overdue-cars list, vehicles, customers, and 5 operational reports: fleet status, bookings in the next 7 days, overdue cars, bookings with money still owing, bookings by status.
- **Admin:** everything staff can do, plus 5 financial reports (revenue by month, revenue by car category, vehicle performance, top customers, late returns by customer), deleting customers and cars that are not rented (with their history), and Tables: create/remove tables, add/drop columns, add/edit/delete rows.

## Automation (runs by itself every 5 minutes while the site is running, and when pages open)
1. Pending requests whose start date has passed are cancelled.
2. Approved bookings with no payment at all whose start date has passed are cancelled, which releases the dates.
3. Car status becomes Rented from the start of a fully paid approved booking until staff click **Mark returned** (so a late car stays Rented), otherwise Available (Maintenance is left alone).

## Late returns
A booking is only Completed when staff click Mark returned. After the end date it shows as **Overdue** (dashboard list, bookings page, overdue report, and a warning for the customer), and nobody else can book that car. The late fee is one extra day's rate for each day late, saved when the car is returned and paid like any other balance. The site adds two Booking columns (`ReturnedDate`, `LateFee`) by itself the first time it starts.
"Run automation now" on the dashboard does the same on demand.
