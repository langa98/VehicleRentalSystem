import csv
import io
import os
import secrets
import threading
import time
from datetime import date, datetime
from functools import wraps

import pyodbc
from flask import (Flask, Response, abort, flash, redirect, render_template, request,
                   session, url_for)

import db
from password import hash_password, verify_password

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

STAFF_ROLES = ("Admin", "Staff")


# ---------- helpers ----------
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(16)
    return session["_csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def check_csrf():
    if request.method == "POST":
        if request.form.get("_csrf") != session.get("_csrf"):
            abort(400, "Invalid form token. Go back, refresh and try again.")


def login_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if "user" not in session:
                return redirect(url_for("login"))
            if roles and session["user"]["Role"] not in roles:
                abort(403)
            return fn(*a, **kw)
        return wrapper
    return deco


@app.context_processor
def inject_user():
    return {"user": session.get("user"), "is_staff": session.get("user", {}).get("Role") in STAFF_ROLES}



def safe_next(target):
    """Only allow redirects to a path on this site."""
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return None


def car_art(category=""):
    """Drawn car for a category (sedan under Sedan, SUV under SUV, ...)."""
    c = (category or "").lower()
    kind = "suv" if ("suv" in c or "bakkie" in c or "4x4" in c) else "luxury" if ("lux" in c or "premium" in c) \
        else "economy" if ("econ" in c or "compact" in c or "hatch" in c) else "sedan"
    return url_for("static", filename=f"cars/{kind}.svg")


app.jinja_env.globals["car_art"] = car_art


def group_by_category(rows):
    """[{name, rate_min, rate_max, cars: [...]}] in the order the rows arrive."""
    groups, index = [], {}
    for r in rows:
        g = index.get(r["CategoryName"])
        if not g:
            g = index[r["CategoryName"]] = {"name": r["CategoryName"], "cars": []}
            groups.append(g)
        g["cars"].append(r)
    for g in groups:
        rates = [c["DailyRate"] for c in g["cars"]]
        g["rate_min"], g["rate_max"] = min(rates), max(rates)
    return groups

@app.template_filter("money")
def money(v):
    return f"R {float(v or 0):,.2f}"


@app.errorhandler(pyodbc.Error)
def db_error(e):
    app.logger.exception("Database error")
    return render_template("error.html", message="The database could not complete that request. "
                           "Check it is running and the connection settings in db.py."), 500


@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", message="You don't have access to that page."), 403


def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


# ---------- auth ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        row = db.query_one(
            "SELECT UserID, Username, PasswordHash, [Role], CustomerID "
            "FROM Rental.[User] WHERE Username = ?", (request.form["username"].strip(),))
        if row and verify_password(request.form["password"], row["PasswordHash"]):
            session.clear()
            session["user"] = {k: row[k] for k in ("UserID", "Username", "Role", "CustomerID")}
            return redirect(safe_next(request.args.get("next")) or url_for("home"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        f = {k: request.form.get(k, "").strip() for k in
             ("first", "last", "id_number", "phone", "email", "license", "username", "password")}
        err = None
        if not all([f["first"], f["last"], f["email"], f["username"], f["password"]]):
            err = "Please fill in all required fields."
        elif not (f["id_number"].isdigit() and len(f["id_number"]) == 13):
            err = "ID number must be exactly 13 digits."
        elif len(f["password"]) < 8:
            err = "Password must be at least 8 characters."
        elif db.query_one("SELECT 1 AS x FROM Rental.[User] WHERE Username = ?", (f["username"],)):
            err = "That username is taken."
        if not err:
            try:
                with db.get_connection() as conn:  # one transaction for both inserts
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO Rental.Customer (FirstName, LastName, IDNumber, PhoneNumber, Email, DriversLicenseNo) "
                        "OUTPUT INSERTED.CustomerID VALUES (?,?,?,?,?,?)",
                        (f["first"], f["last"], f["id_number"], f["phone"] or None, f["email"], f["license"] or None))
                    cid = cur.fetchone()[0]
                    cur.execute("INSERT INTO Rental.[User] (Username, PasswordHash, [Role], CustomerID) VALUES (?,?,?,?)",
                                (f["username"], hash_password(f["password"]), "Customer", cid))
                flash("Account created. You can log in now.", "ok")
                return redirect(url_for("login", next=safe_next(request.args.get("next"))))
            except pyodbc.IntegrityError:
                err = "That ID number, email or licence number is already registered."
        flash(err, "error")
    return render_template("register.html")


# ---------- shared ----------
@app.route("/")
def home():
    if "user" not in session:  # visitors: look at the cars, log in for everything else
        refresh_if_stale()
        rows = db.query("SELECT VehicleID, Make, Model, [Year], CategoryName, DailyRate "
                        "FROM Rental.vw_VehicleAvailability WHERE [Status] = 'Available' "
                        "ORDER BY DailyRate, CategoryName, Make, Model")
        return render_template("public_home.html", groups=group_by_category(rows))
    if session["user"]["Role"] in STAFF_ROLES:
        refresh_if_stale()
        stats = db.query_one("""
            SELECT (SELECT COUNT(*) FROM Rental.Vehicle WHERE [Status]='Available') AS available,
                   (SELECT COUNT(*) FROM Rental.Vehicle WHERE [Status]='Rented') AS rented,
                   (SELECT COUNT(*) FROM Rental.Booking WHERE BookingStatus='Pending') AS pending""")
        overdue = db.query("""
            SELECT b.BookingID, c.FirstName, c.LastName, c.PhoneNumber, v.Make, v.Model, v.RegistrationNo, b.EndDate,
                   DATEDIFF(DAY, b.EndDate, CAST(GETDATE() AS DATE)) AS DaysLate,
                   vc.DailyRate * DATEDIFF(DAY, b.EndDate, CAST(GETDATE() AS DATE)) AS FeeSoFar
            FROM Rental.Booking b JOIN Rental.Customer c ON c.CustomerID = b.CustomerID
            JOIN Rental.Vehicle v ON v.VehicleID = b.VehicleID
            JOIN Rental.VehicleCategory vc ON vc.CategoryID = v.CategoryID
            WHERE """ + OVERDUE_SQL + """ ORDER BY b.EndDate, b.BookingID""")
        revenue = None
        if session["user"]["Role"] == "Admin":  # only the Admin sees what the company has earned
            revenue = db.query_one("SELECT COALESCE(SUM(Amount), 0) AS total FROM Rental.Payment")["total"]
        return render_template("staff_home.html", stats=stats, overdue=overdue, revenue=revenue)
    return redirect(url_for("vehicles"))


@app.route("/vehicles")
@login_required()
def vehicles():
    refresh_if_stale()
    show_all = is_staff_session() and request.args.get("all") == "1"
    start, end = parse_date(request.args.get("start")), parse_date(request.args.get("end"))
    searched = bool(start and end)
    if (request.args.get("start") or request.args.get("end")) and not (
            searched and start >= date.today() and end >= start):
        flash("Choose valid dates (start today or later, end on/after start).", "error")
        searched = False
    sql = "SELECT * FROM Rental.vw_VehicleAvailability v WHERE 1=1"
    params = []
    if searched:  # free for the whole period: not in maintenance and no Pending/Confirmed booking overlapping it
        if not show_all:
            sql += " AND v.[Status] <> 'Maintenance'"
        sql += """ AND NOT EXISTS (SELECT 1 FROM Rental.Booking b WHERE b.VehicleID = v.VehicleID
                   AND ((b.BookingStatus IN ('Pending','Confirmed') AND b.StartDate <= ? AND b.EndDate >= ?)
                        OR (""" + OVERDUE_SQL + """)))"""
        params = [end, start]
    elif not show_all:  # default list: cars that are available now
        sql += " AND v.[Status] = 'Available'"
    rows = db.query(sql + " ORDER BY v.DailyRate, v.CategoryName, v.Make, v.Model", params)
    return render_template("vehicles.html", groups=group_by_category(rows), show_all=show_all, searched=searched,
                           start=start.isoformat() if searched else "", end=end.isoformat() if searched else "",
                           days=((end - start).days + 1) if searched else 0,
                           highlight=request.args.get("highlight", type=int, default=0),
                           today=date.today().isoformat())


def is_staff_session():
    return session.get("user", {}).get("Role") in STAFF_ROLES


# ---------- customer ----------
@app.route("/book/<int:vehicle_id>", methods=["POST"])
@login_required("Customer")
def book(vehicle_id):
    start, end = parse_date(request.form.get("start")), parse_date(request.form.get("end"))
    if not start or not end or end < start or start < date.today():
        flash("Choose valid dates (start today or later, end on/after start).", "error")
        return redirect(url_for("vehicles"))
    cid = session["user"]["CustomerID"]
    if cid is None:
        abort(403)
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT [Status] FROM Rental.Vehicle WHERE VehicleID = ?", (vehicle_id,))
        v = cur.fetchone()
        if not v or v[0] == "Maintenance":
            flash("That vehicle is not available.", "error")
            return redirect(url_for("vehicles"))
        cur.execute("""SELECT 1 FROM Rental.Booking b WHERE b.VehicleID = ?
                       AND ((b.BookingStatus IN ('Pending','Confirmed') AND b.StartDate <= ? AND b.EndDate >= ?)
                            OR (""" + OVERDUE_SQL + """))""", (vehicle_id, end, start))
        if cur.fetchone():
            flash("That vehicle is already booked for those dates.", "error")
            return redirect(url_for("vehicles"))
        cur.execute("INSERT INTO Rental.Booking (CustomerID, VehicleID, StartDate, EndDate, BookingStatus) "
                    "VALUES (?,?,?,?, 'Pending')", (cid, vehicle_id, start, end))
    flash("Booking request sent. Staff will approve it, then you pay the full fee at the branch.", "ok")
    return redirect(url_for("my_bookings"))


@app.route("/my/bookings")
@login_required("Customer")
def my_bookings():
    rows = db.query("""
        SELECT b.BookingID, b.StartDate, b.EndDate, b.BookingStatus, v.Make, v.Model, v.RegistrationNo,
               vc.DailyRate * (DATEDIFF(DAY, b.StartDate, b.EndDate) + 1) + b.LateFee AS EstimatedTotal,
               b.LateFee, b.ReturnedDate, """ + DAYS_LATE_SQL + """ AS DaysLate,
               vc.DailyRate * (""" + DAYS_LATE_SQL + """) AS FeeSoFar,
               COALESCE((SELECT SUM(Amount) FROM Rental.Payment p WHERE p.BookingID = b.BookingID), 0) AS Paid
        FROM Rental.Booking b
        JOIN Rental.Vehicle v ON v.VehicleID = b.VehicleID
        JOIN Rental.VehicleCategory vc ON vc.CategoryID = v.CategoryID
        WHERE b.CustomerID = ? ORDER BY b.StartDate DESC""", (session["user"]["CustomerID"],))
    return render_template("my_bookings.html", bookings=rows)


@app.route("/my/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required("Customer")
def cancel_booking(booking_id):
    n = db.execute("UPDATE b SET BookingStatus='Cancelled' FROM Rental.Booking b "
                   "WHERE b.BookingID=? AND b.CustomerID=? AND b.BookingStatus IN ('Pending','Confirmed') "
                   "AND NOT EXISTS (SELECT 1 FROM Rental.Payment p WHERE p.BookingID = b.BookingID)",
                   (booking_id, session["user"]["CustomerID"]))
    flash("Booking cancelled." if n else "That booking can't be cancelled here. If you have paid, speak to the branch.",
          "ok" if n else "error")
    return redirect(url_for("my_bookings"))


@app.route("/my/payments")
@login_required("Customer")
def my_payments():
    rows = db.query("SELECT * FROM Rental.vw_PaymentDetails WHERE CustomerID = ? ORDER BY PaymentDate DESC",
                    (session["user"]["CustomerID"],))
    return render_template("my_payments.html", payments=rows)


# ---------- late returns ----------
# Overdue = approved, never marked returned, and the end date has passed. The late fee is one extra day's rate
# for every day late, worked out and saved when staff mark the car returned.
OVERDUE_SQL = ("b.BookingStatus = 'Confirmed' AND b.ReturnedDate IS NULL "
               "AND b.EndDate < CAST(GETDATE() AS DATE)")
DAYS_LATE_SQL = "CASE WHEN " + OVERDUE_SQL + " THEN DATEDIFF(DAY, b.EndDate, CAST(GETDATE() AS DATE)) ELSE 0 END"


def ensure_schema():
    """The late-return feature needs two extra Booking columns. Added once, safely, when the site starts."""
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COL_LENGTH('Rental.Booking', 'ReturnedDate')")
        if cur.fetchone()[0] is not None:
            return
        cur.execute("ALTER TABLE Rental.Booking ADD ReturnedDate DATE NULL")
        cur.execute("ALTER TABLE Rental.Booking ADD LateFee DECIMAL(10,2) NOT NULL "
                    "CONSTRAINT DF_Booking_LateFee DEFAULT 0")
        # bookings that were already paid and over before this feature existed count as returned on time
        cur.execute("""UPDATE b SET BookingStatus = 'Completed', ReturnedDate = b.EndDate
                       FROM Rental.Booking b JOIN Rental.Vehicle v ON v.VehicleID = b.VehicleID
                       JOIN Rental.VehicleCategory vc ON vc.CategoryID = v.CategoryID
                       WHERE b.BookingStatus = 'Confirmed' AND b.EndDate < CAST(GETDATE() AS DATE)
                       AND COALESCE((SELECT SUM(Amount) FROM Rental.Payment p WHERE p.BookingID = b.BookingID), 0)
                           >= vc.DailyRate * (DATEDIFF(DAY, b.StartDate, b.EndDate) + 1)""")
        cur.execute("UPDATE Rental.Booking SET ReturnedDate = EndDate WHERE BookingStatus = 'Completed' AND ReturnedDate IS NULL")


# ---------- automation ----------
def sync_vehicles(cur):
    """A vehicle is Rented from the start of a Confirmed, fully paid booking until staff mark it returned (even past the end date); otherwise Available. Maintenance is left alone."""
    cur.execute("""
        UPDATE v SET [Status] = CASE WHEN EXISTS (
                SELECT 1 FROM Rental.Booking b WHERE b.VehicleID = v.VehicleID AND b.BookingStatus = 'Confirmed'
                AND b.StartDate <= CAST(GETDATE() AS DATE)
                AND COALESCE((SELECT SUM(Amount) FROM Rental.Payment p WHERE p.BookingID = b.BookingID), 0)
                    >= (SELECT DailyRate FROM Rental.VehicleCategory WHERE CategoryID = v.CategoryID)
                       * (DATEDIFF(DAY, b.StartDate, b.EndDate) + 1)) THEN 'Rented' ELSE 'Available' END
        FROM Rental.Vehicle v WHERE v.[Status] <> 'Maintenance'""")
    return cur.rowcount


def run_automation():
    """The daily housekeeping. Returns (cancelled_requests, cancelled_unpaid, overdue_now).
    1. Pending requests whose start date has passed are cancelled.
    2. Approved bookings with no payment at all whose start date has passed are cancelled (dates released).
    3. Vehicle statuses are refreshed. A booking is only Completed when staff mark the car returned,
       so a car that is late stays Rented and shows up as overdue."""
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE Rental.Booking SET BookingStatus='Cancelled' "
                    "WHERE BookingStatus='Pending' AND StartDate < CAST(GETDATE() AS DATE)")
        expired = cur.rowcount
        cur.execute("""UPDATE b SET BookingStatus='Cancelled' FROM Rental.Booking b
                       WHERE b.BookingStatus='Confirmed' AND b.StartDate < CAST(GETDATE() AS DATE)
                       AND NOT EXISTS (SELECT 1 FROM Rental.Payment p WHERE p.BookingID = b.BookingID)""")
        unpaid = cur.rowcount
        sync_vehicles(cur)
        cur.execute("SELECT COUNT(*) FROM Rental.Booking b WHERE " + OVERDUE_SQL)
        overdue = cur.fetchone()[0]
    return expired, unpaid, overdue


AUTOMATION_MINUTES = 5
_last_run = 0.0
_run_lock = threading.Lock()


def safe_run():
    """Run the automation; a database hiccup is logged, never shown to a visitor."""
    global _last_run
    with _run_lock:
        try:
            result = run_automation()
        except Exception:
            app.logger.exception("Automation run failed")
            result = None
        _last_run = time.time()
        return result


def refresh_if_stale(max_age=60):
    """Called when pages open, so what people see is current (at most one run a minute)."""
    if time.time() - _last_run >= max_age:
        safe_run()


def automation_loop():
    while True:
        safe_run()
        time.sleep(AUTOMATION_MINUTES * 60)


@app.route("/staff/automation", methods=["POST"])
@login_required(*STAFF_ROLES)
def automation():
    expired, unpaid, overdue = run_automation()
    flash(f"Automation done: {expired} unapproved past request(s) cancelled, {unpaid} unpaid approved booking(s) "
          f"cancelled, vehicle statuses refreshed. {overdue} car(s) overdue.", "ok")
    return redirect(url_for("home"))


# ---------- staff / admin ----------
@app.route("/staff/bookings")
@login_required(*STAFF_ROLES)
def staff_bookings():
    status = request.args.get("status", "")
    sql = """SELECT b.BookingID, b.StartDate, b.EndDate, b.BookingStatus, c.FirstName, c.LastName,
                    v.Make, v.Model, v.RegistrationNo,
                    vc.DailyRate * (DATEDIFF(DAY, b.StartDate, b.EndDate) + 1) + b.LateFee AS Total,
                    b.LateFee, b.ReturnedDate,
                    CASE WHEN b.StartDate <= CAST(GETDATE() AS DATE) THEN 1 ELSE 0 END AS Started,
                    """ + DAYS_LATE_SQL + """ AS DaysLate,
                    vc.DailyRate * (""" + DAYS_LATE_SQL + """) AS FeeSoFar,
                    COALESCE((SELECT SUM(Amount) FROM Rental.Payment p WHERE p.BookingID=b.BookingID),0) AS Paid
             FROM Rental.Booking b
             JOIN Rental.Customer c ON c.CustomerID=b.CustomerID
             JOIN Rental.Vehicle v ON v.VehicleID=b.VehicleID
             JOIN Rental.VehicleCategory vc ON vc.CategoryID=v.CategoryID"""
    params = ()
    if status in ("Pending", "Confirmed", "Completed", "Cancelled"):
        sql += " WHERE b.BookingStatus = ?"
        params = (status,)
    rows = db.query(sql + " ORDER BY b.StartDate DESC", params)
    return render_template("staff_bookings.html", bookings=rows, status=status)


def booking_balance(cur, booking_id):
    """Total fee, amount paid and balance for one booking (None if it does not exist)."""
    cur.execute("""SELECT b.BookingStatus,
                          vc.DailyRate * (DATEDIFF(DAY, b.StartDate, b.EndDate) + 1) + b.LateFee AS Total,
                          COALESCE((SELECT SUM(Amount) FROM Rental.Payment p WHERE p.BookingID = b.BookingID), 0) AS Paid
                   FROM Rental.Booking b
                   JOIN Rental.Vehicle v ON v.VehicleID = b.VehicleID
                   JOIN Rental.VehicleCategory vc ON vc.CategoryID = v.CategoryID
                   WHERE b.BookingID = ?""", (booking_id,))
    r = cur.fetchone()
    if not r:
        return None
    return {"status": r[0], "total": r[1], "paid": r[2], "balance": r[1] - r[2]}


@app.route("/staff/bookings/<int:booking_id>/status", methods=["POST"])
@login_required(*STAFF_ROLES)
def set_booking_status(booking_id):
    new = request.form.get("status")
    if new not in ("Confirmed", "Cancelled"):  # Completed only happens through "Mark returned"
        abort(400)
    with db.get_connection() as conn:
        cur = conn.cursor()
        b = booking_balance(cur, booking_id)
        if not b:
            abort(404)
        if new == "Cancelled":
            cur.execute("SELECT 1 FROM Rental.Booking b WHERE b.BookingID = ? AND " + OVERDUE_SQL, (booking_id,))
            if cur.fetchone():
                flash(f"Booking #{booking_id} is overdue: the car is still out. Use Mark returned when it comes back.", "error")
                return redirect(request.referrer or url_for("staff_bookings"))
        cur.execute("UPDATE Rental.Booking SET BookingStatus=? WHERE BookingID=?", (new, booking_id))
        sync_vehicles(cur)  # automation: vehicle status follows the bookings
    if new == "Confirmed":
        flash(f"Booking #{booking_id} approved. The customer now pays {money(b['balance'])} at the branch.", "ok")
    else:
        flash(f"Booking #{booking_id} marked {new}.", "ok")
    return redirect(request.referrer or url_for("staff_bookings"))


@app.route("/staff/bookings/<int:booking_id>/return", methods=["POST"])
@login_required(*STAFF_ROLES)
def mark_returned(booking_id):
    """The car is back. Completes the booking and, if it is late, saves the late fee (one day's rate per day late)."""
    with db.get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT b.BookingStatus, b.StartDate, b.EndDate, vc.DailyRate,
                              COALESCE((SELECT SUM(Amount) FROM Rental.Payment p WHERE p.BookingID = b.BookingID), 0),
                              vc.DailyRate * (DATEDIFF(DAY, b.StartDate, b.EndDate) + 1)
                       FROM Rental.Booking b JOIN Rental.Vehicle v ON v.VehicleID = b.VehicleID
                       JOIN Rental.VehicleCategory vc ON vc.CategoryID = v.CategoryID
                       WHERE b.BookingID = ?""", (booking_id,))
        r = cur.fetchone()
        if not r:
            abort(404)
        status, start, end, rate, paid, base = r
        today = date.today()
        if status != "Confirmed" or start > today:
            flash(f"Booking #{booking_id} can't be marked returned: the car hasn't been collected, or it is already finished.", "error")
        elif paid < base:
            flash(f"Booking #{booking_id} can't be marked returned: the rental fee is still unpaid.", "error")
        else:
            late_days = max(0, (today - end).days)
            fee = rate * late_days
            cur.execute("UPDATE Rental.Booking SET BookingStatus='Completed', ReturnedDate=?, LateFee=? WHERE BookingID=?",
                        (today, fee, booking_id))
            sync_vehicles(cur)
            if late_days:
                flash(f"Booking #{booking_id} returned {late_days} day(s) late. Late fee {money(fee)}: "
                      f"collect it from the customer.", "ok")
            else:
                flash(f"Booking #{booking_id} returned on time. Booking completed.", "ok")
    return redirect(request.referrer or url_for("staff_bookings"))


@app.route("/staff/bookings/<int:booking_id>/payment", methods=["POST"])
@login_required(*STAFF_ROLES)
def add_payment(booking_id):
    """Records the exact remaining fee. The amount is never taken from the form."""
    method = request.form.get("method")
    if method not in ("Cash", "Card", "EFT"):
        flash("Choose how the customer paid: Cash, Card or EFT.", "error")
        return redirect(url_for("staff_bookings"))
    with db.get_connection() as conn:
        cur = conn.cursor()
        b = booking_balance(cur, booking_id)
        if not b:
            abort(404)
        if b["status"] not in ("Confirmed", "Completed"):
            flash("A payment can only be recorded after the booking is approved.", "error")
        elif b["balance"] <= 0:
            flash("That booking is already paid in full.", "error")
        else:
            cur.execute("INSERT INTO Rental.Payment (Amount, PaymentDate, PaymentMethod, BookingID) VALUES (?,?,?,?)",
                        (b["balance"], date.today(), method, booking_id))
            sync_vehicles(cur)
            flash(f"Full payment of {money(b['balance'])} recorded.", "ok")
    return redirect(url_for("staff_bookings"))


@app.route("/staff/vehicles", methods=["GET", "POST"])
@login_required(*STAFF_ROLES)
def staff_vehicles():
    if request.method == "POST":
        try:
            db.execute("INSERT INTO Rental.Vehicle (RegistrationNo, Make, Model, [Year], [Status], CategoryID) "
                       "VALUES (?,?,?,?,?,?)",
                       (request.form["reg"].strip().upper(), request.form["make"].strip(), request.form["model"].strip(),
                        int(request.form["year"]), request.form["status"], int(request.form["category"])))
            flash("Vehicle added.", "ok")
        except (pyodbc.IntegrityError, ValueError, KeyError):
            flash("Could not add vehicle (duplicate registration or invalid data).", "error")
        return redirect(url_for("staff_vehicles"))
    return render_template("staff_vehicles.html",
                           vehicles=db.query("SELECT * FROM Rental.vw_VehicleAvailability ORDER BY Make, Model"),
                           categories=db.query("SELECT * FROM Rental.VehicleCategory ORDER BY CategoryName"))


@app.route("/staff/vehicles/<int:vehicle_id>/status", methods=["POST"])
@login_required(*STAFF_ROLES)
def set_vehicle_status(vehicle_id):
    s = request.form.get("status")
    if s not in ("Available", "Rented", "Maintenance"):
        abort(400)
    db.execute("UPDATE Rental.Vehicle SET [Status]=? WHERE VehicleID=?", (s, vehicle_id))
    flash("Vehicle status updated.", "ok")
    return redirect(url_for("staff_vehicles"))


@app.route("/staff/customers")
@login_required(*STAFF_ROLES)
def staff_customers():
    return render_template("staff_customers.html", customers=db.query(
        "SELECT c.CustomerID, c.FirstName, c.LastName, c.PhoneNumber, c.Email, c.DriversLicenseNo, "
        "CASE WHEN EXISTS (" + RENTING_NOW_SQL + ") THEN 1 ELSE 0 END AS RentingNow "
        "FROM Rental.Customer c ORDER BY c.LastName, c.FirstName"))

# A customer is "renting now" from the start of an approved (Confirmed) booking until staff mark the car returned.
RENTING_NOW_SQL = ("SELECT 1 FROM Rental.Booking b WHERE b.CustomerID = c.CustomerID AND b.BookingStatus = 'Confirmed' "
                   "AND b.StartDate <= CAST(GETDATE() AS DATE)")
ACTIVE_RENTALS_SQL = ("SELECT b.BookingID, b.StartDate, b.EndDate, v.Make, v.Model FROM Rental.Booking b "
                      "JOIN Rental.Vehicle v ON v.VehicleID = b.VehicleID WHERE b.CustomerID = ? "
                      "AND b.BookingStatus = 'Confirmed' AND b.StartDate <= CAST(GETDATE() AS DATE)")


class RentingNow(Exception):
    pass


def _customer_or_404(customer_id):
    c = db.query_one("SELECT CustomerID, FirstName, LastName, Email FROM Rental.Customer WHERE CustomerID = ?",
                     (customer_id,))
    if not c:
        abort(404)
    return c


@app.route("/admin/customers/<int:customer_id>/delete", methods=["GET", "POST"])
@login_required("Admin")
def delete_customer(customer_id):
    """Removes a customer together with everything that points at them, in one all-or-nothing step."""
    c = _customer_or_404(customer_id)
    counts = db.query_one(
        """SELECT (SELECT COUNT(*) FROM Rental.Booking WHERE CustomerID = ?) AS bookings,
                  (SELECT COUNT(*) FROM Rental.Payment p JOIN Rental.Booking b ON b.BookingID = p.BookingID
                   WHERE b.CustomerID = ?) AS payments,
                  (SELECT COALESCE(SUM(p.Amount), 0) FROM Rental.Payment p JOIN Rental.Booking b
                   ON b.BookingID = p.BookingID WHERE b.CustomerID = ?) AS paid,
                  (SELECT COUNT(*) FROM Rental.[User] WHERE CustomerID = ?) AS logins""",
        (customer_id,) * 4)
    full_name = f"{c['FirstName']} {c['LastName']}"
    active = db.query(ACTIVE_RENTALS_SQL, (customer_id,))
    if active:  # never delete someone who has a car out right now
        if request.method == "POST":
            flash(f"{full_name} is renting a car right now, so they can't be deleted.", "error")
        return render_template("customer_delete.html", c=c, full_name=full_name, counts=counts, active=active)
    if request.method == "POST":
        if request.form.get("confirm", "").strip().lower() != full_name.lower():
            flash("The name you typed doesn't match, so nothing was deleted.", "error")
            return redirect(url_for("delete_customer", customer_id=customer_id))
        try:
            with db.get_connection() as conn:  # any failure rolls everything back
                cur = conn.cursor()
                cur.execute(ACTIVE_RENTALS_SQL, (customer_id,))  # checked again inside the transaction
                if cur.fetchone():
                    raise RentingNow()
                cur.execute("DELETE p FROM Rental.Payment p JOIN Rental.Booking b ON b.BookingID = p.BookingID "
                            "WHERE b.CustomerID = ?", (customer_id,))
                cur.execute("DELETE FROM Rental.Booking WHERE CustomerID = ?", (customer_id,))
                cur.execute("DELETE FROM Rental.[User] WHERE CustomerID = ?", (customer_id,))
                cur.execute("DELETE FROM Rental.Customer WHERE CustomerID = ?", (customer_id,))
                sync_vehicles(cur)  # cars they were holding become available again
        except RentingNow:
            flash(f"{full_name} is renting a car right now, so they can't be deleted.", "error")
            return redirect(url_for("delete_customer", customer_id=customer_id))
        except pyodbc.Error as e:
            from admin_tables import db_msg
            flash(f"Nothing was deleted. {db_msg(e)}", "error")
            return redirect(url_for("delete_customer", customer_id=customer_id))
        flash(f"{full_name} was deleted, with {counts['bookings']} booking(s), {counts['payments']} payment(s) "
              f"and {counts['logins']} login(s).", "ok")
        return redirect(url_for("staff_customers"))
    return render_template("customer_delete.html", c=c, full_name=full_name, counts=counts)




# (key, title, why it matters, SQL, admin_only). Money in the financial reports is for the Admin only.
REPORTS = [
    ("fleet-status", "Fleet status by category",
     "How many cars of each type are free, out on rent or in the workshop right now.",
     "SELECT vc.CategoryName, COUNT(*) AS TotalCars, "
     "SUM(CASE WHEN v.[Status] = 'Available' THEN 1 ELSE 0 END) AS Available, "
     "SUM(CASE WHEN v.[Status] = 'Rented' THEN 1 ELSE 0 END) AS Rented, "
     "SUM(CASE WHEN v.[Status] = 'Maintenance' THEN 1 ELSE 0 END) AS Maintenance "
     "FROM Rental.Vehicle v JOIN Rental.VehicleCategory vc ON vc.CategoryID = v.CategoryID "
     "GROUP BY vc.CategoryName ORDER BY vc.CategoryName", False),
    ("upcoming-bookings", "Bookings in the next 7 days",
     "Who is collecting or returning a car this week, so the right cars are ready.",
     "SELECT b.BookingID, c.FirstName + ' ' + c.LastName AS Customer, v.Make + ' ' + v.Model AS Vehicle, "
     "v.RegistrationNo, b.StartDate, b.EndDate, b.BookingStatus "
     "FROM Rental.Booking b JOIN Rental.Customer c ON c.CustomerID = b.CustomerID "
     "JOIN Rental.Vehicle v ON v.VehicleID = b.VehicleID "
     "WHERE b.BookingStatus IN ('Pending', 'Confirmed') AND b.EndDate >= CAST(GETDATE() AS DATE) "
     "AND b.StartDate <= DATEADD(DAY, 7, CAST(GETDATE() AS DATE)) ORDER BY b.StartDate, b.BookingID", False),
    ("outstanding-balances", "Bookings with money still owing",
     "Approved or finished bookings that have not been paid in full, biggest balance first, so nothing is missed.",
     "SELECT * FROM (SELECT b.BookingID, c.FirstName + ' ' + c.LastName AS Customer, v.Make + ' ' + v.Model AS Vehicle, "
     "b.StartDate, b.EndDate, b.BookingStatus, "
     "vc.DailyRate * (DATEDIFF(DAY, b.StartDate, b.EndDate) + 1) + b.LateFee AS Total, COALESCE(pay.Paid, 0) AS Paid, "
     "vc.DailyRate * (DATEDIFF(DAY, b.StartDate, b.EndDate) + 1) + b.LateFee - COALESCE(pay.Paid, 0) AS Balance "
     "FROM Rental.Booking b JOIN Rental.Customer c ON c.CustomerID = b.CustomerID "
     "JOIN Rental.Vehicle v ON v.VehicleID = b.VehicleID "
     "JOIN Rental.VehicleCategory vc ON vc.CategoryID = v.CategoryID "
     "OUTER APPLY (SELECT SUM(p.Amount) AS Paid FROM Rental.Payment p WHERE p.BookingID = b.BookingID) pay "
     "WHERE b.BookingStatus IN ('Confirmed', 'Completed')) x WHERE x.Balance > 0 ORDER BY x.Balance DESC", False),
    ("overdue-returns", "Overdue cars",
     "Cars that should already be back. Phone these customers first: the car can't be rented out until it returns.",
     "SELECT b.BookingID, c.FirstName + ' ' + c.LastName AS Customer, c.PhoneNumber AS Phone, "
     "v.Make + ' ' + v.Model AS Vehicle, v.RegistrationNo, b.EndDate AS DueBack, "
     "DATEDIFF(DAY, b.EndDate, CAST(GETDATE() AS DATE)) AS DaysLate, "
     "vc.DailyRate * DATEDIFF(DAY, b.EndDate, CAST(GETDATE() AS DATE)) AS FeeSoFar "
     "FROM Rental.Booking b JOIN Rental.Customer c ON c.CustomerID = b.CustomerID "
     "JOIN Rental.Vehicle v ON v.VehicleID = b.VehicleID "
     "JOIN Rental.VehicleCategory vc ON vc.CategoryID = v.CategoryID "
     "WHERE " + OVERDUE_SQL + " ORDER BY DaysLate DESC, b.BookingID", False),
    ("booking-status", "Bookings by status",
     "Shows how many requests turn into rentals, and how many are cancelled.",
     "SELECT BookingStatus, COUNT(*) AS Bookings, "
     "CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER () AS DECIMAL(5, 1)) AS SharePercent "
     "FROM Rental.Booking GROUP BY BookingStatus ORDER BY Bookings DESC", False),
    ("late-returns", "Late returns by customer",
     "Customers who have brought cars back late, and the late fees charged, to decide who needs a warning.",
     "SELECT c.FirstName + ' ' + c.LastName AS Customer, COUNT(*) AS LateReturns, "
     "SUM(DATEDIFF(DAY, b.EndDate, b.ReturnedDate)) AS TotalDaysLate, SUM(b.LateFee) AS LateFees "
     "FROM Rental.Booking b JOIN Rental.Customer c ON c.CustomerID = b.CustomerID "
     "WHERE b.ReturnedDate > b.EndDate GROUP BY c.CustomerID, c.FirstName, c.LastName "
     "ORDER BY LateFees DESC", True),
    ("revenue-by-month", "Revenue by month",
     "How much money came in each month, and the running total, to see whether the business is growing.",
     "SELECT CONVERT(CHAR(7), PaymentDate, 120) AS Month, COUNT(*) AS Payments, SUM(Amount) AS Revenue, "
     "SUM(SUM(Amount)) OVER (ORDER BY CONVERT(CHAR(7), PaymentDate, 120)) AS RunningTotal "
     "FROM Rental.Payment GROUP BY CONVERT(CHAR(7), PaymentDate, 120) ORDER BY Month", True),
    ("revenue-by-category", "Revenue by car category",
     "Which kinds of car earn the most, to decide what to buy more of.",
     "SELECT vc.CategoryName, COUNT(DISTINCT b.BookingID) AS Bookings, SUM(p.Amount) AS Revenue, "
     "CAST(100.0 * SUM(p.Amount) / NULLIF(SUM(SUM(p.Amount)) OVER (), 0) AS DECIMAL(5, 1)) AS SharePercent "
     "FROM Rental.Payment p JOIN Rental.Booking b ON b.BookingID = p.BookingID "
     "JOIN Rental.Vehicle v ON v.VehicleID = b.VehicleID "
     "JOIN Rental.VehicleCategory vc ON vc.CategoryID = v.CategoryID "
     "GROUP BY vc.CategoryName ORDER BY Revenue DESC", True),
    ("vehicle-performance", "Vehicle performance",
     "Revenue earned by every car. Cars at the bottom earn little and may not be worth keeping.",
     "SELECT v.RegistrationNo, v.Make + ' ' + v.Model AS Vehicle, vc.CategoryName, "
     "COUNT(DISTINCT b.BookingID) AS Bookings, COALESCE(SUM(p.Amount), 0) AS Revenue "
     "FROM Rental.Vehicle v JOIN Rental.VehicleCategory vc ON vc.CategoryID = v.CategoryID "
     "LEFT JOIN Rental.Booking b ON b.VehicleID = v.VehicleID "
     "LEFT JOIN Rental.Payment p ON p.BookingID = b.BookingID "
     "GROUP BY v.RegistrationNo, v.Make, v.Model, vc.CategoryName ORDER BY Revenue DESC, Bookings DESC", True),
    ("top-customers", "Top customers",
     "The customers who spend the most, so the best ones can be looked after.",
     "SELECT TOP 10 c.FirstName + ' ' + c.LastName AS Customer, COUNT(DISTINCT b.BookingID) AS Bookings, "
     "SUM(p.Amount) AS TotalSpent "
     "FROM Rental.Customer c JOIN Rental.Booking b ON b.CustomerID = c.CustomerID "
     "JOIN Rental.Payment p ON p.BookingID = b.BookingID "
     "GROUP BY c.CustomerID, c.FirstName, c.LastName ORDER BY TotalSpent DESC", True),
]
MONEY_COLS = {"Revenue", "RunningTotal", "TotalSpent", "Total", "Paid", "Balance", "FeeSoFar", "LateFees"}


def _visible_reports():
    is_admin = session["user"]["Role"] == "Admin"
    return [r for r in REPORTS if is_admin or not r[4]]


def _report_data(key):
    for k, title, why, sql, admin_only in _visible_reports():
        if k == key:
            rows = db.query(sql)
            cols = list(rows[0].keys()) if rows else []
            return title, cols, rows
    abort(404)  # unknown key, or a financial report requested by someone who isn't the Admin

# A car is "in use" from the start of an approved (Confirmed) booking until staff mark it returned.
ACTIVE_CAR_RENTALS_SQL = ("SELECT b.BookingID, b.StartDate, b.EndDate, c.FirstName, c.LastName FROM Rental.Booking b "
                          "JOIN Rental.Customer c ON c.CustomerID = b.CustomerID WHERE b.VehicleID = ? "
                          "AND b.BookingStatus = 'Confirmed' AND b.StartDate <= CAST(GETDATE() AS DATE)")


class CarInUse(Exception):
    pass


@app.route("/admin/vehicles/<int:vehicle_id>/delete", methods=["GET", "POST"])
@login_required("Admin")
def delete_vehicle(vehicle_id):
    """Removes a car that is not rented, together with its booking history, in one all-or-nothing step."""
    v = db.query_one("SELECT VehicleID, RegistrationNo, Make, Model, [Status] FROM Rental.Vehicle WHERE VehicleID = ?",
                     (vehicle_id,))
    if not v:
        abort(404)
    name = f"{v['Make']} {v['Model']} ({v['RegistrationNo']})"
    active = db.query(ACTIVE_CAR_RENTALS_SQL, (vehicle_id,))
    in_use = bool(active) or v["Status"] == "Rented"
    counts = db.query_one(
        """SELECT (SELECT COUNT(*) FROM Rental.Booking WHERE VehicleID = ?) AS bookings,
                  (SELECT COUNT(*) FROM Rental.Booking WHERE VehicleID = ? AND BookingStatus IN ('Pending','Confirmed')
                   AND StartDate > CAST(GETDATE() AS DATE)) AS upcoming,
                  (SELECT COUNT(*) FROM Rental.Payment p JOIN Rental.Booking b ON b.BookingID = p.BookingID
                   WHERE b.VehicleID = ?) AS payments,
                  (SELECT COALESCE(SUM(p.Amount), 0) FROM Rental.Payment p JOIN Rental.Booking b
                   ON b.BookingID = p.BookingID WHERE b.VehicleID = ?) AS paid""", (vehicle_id,) * 4)
    if in_use:  # never delete a car that is out on rent
        if request.method == "POST":
            flash(f"{name} is rented right now, so it can't be deleted.", "error")
        return render_template("vehicle_delete.html", v=v, name=name, counts=counts, active=active, in_use=True)
    if request.method == "POST":
        if request.form.get("confirm", "").strip().upper() != v["RegistrationNo"].upper():
            flash("The registration number you typed doesn't match, so nothing was deleted.", "error")
            return redirect(url_for("delete_vehicle", vehicle_id=vehicle_id))
        try:
            with db.get_connection() as conn:  # any failure rolls everything back
                cur = conn.cursor()
                cur.execute(ACTIVE_CAR_RENTALS_SQL, (vehicle_id,))  # checked again inside the transaction
                busy = cur.fetchone()
                cur.execute("SELECT 1 FROM Rental.Vehicle WHERE VehicleID = ? AND [Status] = 'Rented'", (vehicle_id,))
                if busy or cur.fetchone():
                    raise CarInUse()
                cur.execute("DELETE p FROM Rental.Payment p JOIN Rental.Booking b ON b.BookingID = p.BookingID "
                            "WHERE b.VehicleID = ?", (vehicle_id,))
                cur.execute("DELETE FROM Rental.Booking WHERE VehicleID = ?", (vehicle_id,))
                cur.execute("DELETE FROM Rental.Vehicle WHERE VehicleID = ?", (vehicle_id,))
        except CarInUse:
            flash(f"{name} is rented right now, so it can't be deleted.", "error")
            return redirect(url_for("delete_vehicle", vehicle_id=vehicle_id))
        except pyodbc.Error as e:
            from admin_tables import db_msg
            flash(f"Nothing was deleted. {db_msg(e)}", "error")
            return redirect(url_for("delete_vehicle", vehicle_id=vehicle_id))
        flash(f"{name} was deleted, with {counts['bookings']} booking(s) and {counts['payments']} payment(s).", "ok")
        return redirect(url_for("staff_vehicles"))
    return render_template("vehicle_delete.html", v=v, name=name, counts=counts, active=[], in_use=False)



@app.route("/staff/reports")
@login_required(*STAFF_ROLES)
def staff_reports():
    data = []
    for k, title, why, sql, admin_only in _visible_reports():
        rows = db.query(sql)
        data.append({"key": k, "title": title, "why": why, "financial": admin_only,
                     "cols": list(rows[0].keys()) if rows else [], "rows": rows})
    return render_template("staff_reports.html", reports=data, money_cols=MONEY_COLS)


@app.route("/staff/reports/<key>.csv")
@login_required(*STAFF_ROLES)
def report_csv(key):
    title, cols, rows = _report_data(key)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow([r[c] for c in cols])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={key}.csv"})


import admin_tables  # noqa: E402  (needs login_required defined above)
admin_tables.register(app, login_required)


if __name__ == "__main__":
    ensure_schema()
    debug = os.environ.get("FLASK_DEBUG") == "1"
    if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":  # one timer, even with the reloader
        threading.Thread(target=automation_loop, daemon=True, name="automation").start()
    app.run(debug=debug, host="127.0.0.1", port=5000)
