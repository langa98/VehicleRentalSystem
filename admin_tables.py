"""Admin 'Tables' area: create/drop tables, add/drop columns, add/edit/delete rows.

Every table or column name that reaches SQL is either checked against the live
database catalog or matched against a strict pattern, then bracket-quoted.
Values always go in as query parameters.
"""
import re

import pyodbc
from flask import abort, flash, redirect, render_template, request, url_for

import db
from password import hash_password

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,49}$")
# Tables the website itself depends on: can't be dropped (or lose columns) from the site.
CORE = {"Customer", "VehicleCategory", "Vehicle", "Booking", "Payment", "User"}

TYPES = {
    "Whole number": "INT",
    "Big whole number": "BIGINT",
    "Decimal / money": "DECIMAL(12,2)",
    "Short text (50)": "NVARCHAR(50)",
    "Text (100)": "NVARCHAR(100)",
    "Long text (255)": "NVARCHAR(255)",
    "Date": "DATE",
    "Date and time": "DATETIME2",
    "Yes / No": "BIT",
}
INT_T = {"int", "bigint", "smallint", "tinyint"}
DEC_T = {"decimal", "numeric", "money", "smallmoney", "float", "real"}
DT_T = {"datetime", "datetime2", "smalldatetime"}
SKIP_T = {"timestamp", "rowversion"}


def db_msg(e):
    """Readable SQL Server message. SQL Server often sends the real reason first and a generic
    'The statement has been terminated.' second, so keep the reason and drop the generic part."""
    text = str(e.args[1]) if len(e.args) > 1 else str(e)
    parts = [re.split(r"\s*\(\d+\)", p)[0].strip(" ;") for p in text.split("[SQL Server]")[1:]] or [text]
    parts = [p for p in parts if p and "statement has been terminated" not in p.lower()]
    msg = " ".join(parts) or "The database refused that change."
    if "conflicted with the REFERENCE constraint" in msg:
        used = re.search(r'table "(?:\w+\.)?(\w+)"', msg)
        where = f"in {used.group(1)}" if used else "by other tables"
        if msg.startswith("The DELETE"):
            return f"This row can't be deleted because it is still used {where}. Delete or change those rows first."
        return f"That change isn't allowed because the row is used {where}."
    return msg


def list_tables():
    return db.query("""
        SELECT t.name AS name, COALESCE(SUM(p.rows), 0) AS row_count
        FROM sys.tables t JOIN sys.schemas s ON s.schema_id = t.schema_id
        LEFT JOIN sys.partitions p ON p.object_id = t.object_id AND p.index_id IN (0, 1)
        WHERE s.name = 'Rental' GROUP BY t.name ORDER BY t.name""")


def get_columns(table):
    cols = db.query("""
        SELECT c.name, ty.name AS type, c.max_length, c.is_nullable, c.is_identity, c.is_computed,
               CASE WHEN ic.column_id IS NULL THEN 0 ELSE 1 END AS is_pk
        FROM sys.columns c
        JOIN sys.types ty ON ty.user_type_id = c.user_type_id
        LEFT JOIN sys.indexes i ON i.object_id = c.object_id AND i.is_primary_key = 1
        LEFT JOIN sys.index_columns ic ON ic.object_id = i.object_id AND ic.index_id = i.index_id
                                      AND ic.column_id = c.column_id
        WHERE c.object_id = OBJECT_ID(?) ORDER BY c.column_id""", (f"Rental.[{table}]",))
    for c in cols:
        t = c["type"]
        c["kind"] = ("int" if t in INT_T else "dec" if t in DEC_T else "date" if t == "date"
                     else "dt" if t in DT_T else "bit" if t == "bit" else "text")
        c["readonly"] = bool(c["is_identity"] or c["is_computed"] or t in SKIP_T)
    return cols


def get_table(name):
    if name not in {t["name"] for t in list_tables()}:
        abort(404)
    return name


def pk_of(cols):
    pks = [c for c in cols if c["is_pk"]]
    return pks[0] if len(pks) == 1 else None


def convert(col, form):
    raw = form.get("f_" + col["name"], "")
    if col["kind"] == "bit":
        return 1 if raw else 0
    raw = raw.strip()
    if raw == "":
        return None
    return raw.replace("T", " ") if col["kind"] == "dt" else raw


def register(app, login_required):
    admin = login_required("Admin")

    @app.route("/admin/tables")
    @admin
    def admin_tables():
        tables = list_tables()
        link_targets = []
        for t in tables:
            pk = pk_of(get_columns(t["name"]))
            if pk and pk["kind"] == "int":
                link_targets.append(t["name"])
        return render_template("admin_tables.html", tables=tables, core=CORE, types=TYPES, targets=link_targets)

    @app.route("/admin/tables/create", methods=["POST"])
    @admin
    def create_table():
        name = request.form.get("table_name", "").strip()
        if not NAME_RE.match(name):
            flash("Table name: letters, numbers and underscores only, starting with a letter.", "error")
            return redirect(url_for("admin_tables"))
        existing = {t["name"].lower() for t in list_tables()}
        if name.lower() in existing:
            flash(f"A table called {name} already exists.", "error")
            return redirect(url_for("admin_tables"))
        id_col = f"{name}ID"
        parts, seen = [f"[{id_col}] INT IDENTITY(1,1) PRIMARY KEY"], {id_col.lower()}
        names = request.form.getlist("col_name")
        types = request.form.getlist("col_type")
        reqs = request.form.getlist("col_req")
        for cname, ctype, req in zip(names, types, reqs):
            cname = cname.strip()
            if not cname:
                continue
            if not NAME_RE.match(cname) or cname.lower() in seen:
                flash(f"Column name '{cname}' is invalid or repeated.", "error")
                return redirect(url_for("admin_tables"))
            seen.add(cname.lower())
            null = "NOT NULL" if req == "yes" else "NULL"
            if ctype.startswith("fk:"):
                target = ctype[3:]
                if target not in existing and target not in {t["name"] for t in list_tables()}:
                    abort(400)
                tpk = pk_of(get_columns(target))
                if not tpk:
                    abort(400)
                parts.append(f"[{cname}] INT {null} CONSTRAINT [FK_{name}_{cname}] "
                             f"FOREIGN KEY REFERENCES Rental.[{target}]([{tpk['name']}])")
            elif ctype in TYPES:
                parts.append(f"[{cname}] {TYPES[ctype]} {null}")
            else:
                abort(400)
        try:
            db.execute(f"CREATE TABLE Rental.[{name}] ({', '.join(parts)})")
            flash(f"Table {name} created (with an automatic {id_col} key).", "ok")
            return redirect(url_for("admin_table", table=name))
        except pyodbc.Error as e:
            flash(db_msg(e), "error")
            return redirect(url_for("admin_tables"))

    @app.route("/admin/tables/<table>")
    @admin
    def admin_table(table):
        table = get_table(table)
        cols = get_columns(table)
        pk = pk_of(cols)
        order = f" ORDER BY [{pk['name']}]" if pk else ""
        rows = db.query(f"SELECT TOP 500 * FROM Rental.[{table}]{order}")
        return render_template("admin_table.html", table=table, cols=cols, pk=pk, rows=rows,
                               core=table in CORE, types=TYPES)

    @app.route("/admin/tables/<table>/rows/add", methods=["POST"])
    @admin
    def row_add(table):
        table = get_table(table)
        names, vals = [], []
        for c in get_columns(table):
            if c["readonly"]:
                continue
            v = convert(c, request.form)
            if table == "User" and c["name"] == "PasswordHash":
                if not v:
                    flash("Enter a password for the new user.", "error")
                    return redirect(url_for("admin_table", table=table))
                v = hash_password(v)
            names.append(f"[{c['name']}]")
            vals.append(v)
        try:
            db.execute(f"INSERT INTO Rental.[{table}] ({', '.join(names)}) VALUES ({', '.join('?' * len(vals))})",
                       tuple(vals))
            flash("Row added.", "ok")
        except pyodbc.Error as e:
            flash(db_msg(e), "error")
        return redirect(url_for("admin_table", table=table))

    @app.route("/admin/tables/<table>/rows/<pk>/edit", methods=["GET", "POST"])
    @admin
    def row_edit(table, pk):
        table = get_table(table)
        cols = get_columns(table)
        pkc = pk_of(cols)
        if not pkc:
            abort(400)
        row = db.query_one(f"SELECT * FROM Rental.[{table}] WHERE [{pkc['name']}] = ?", (pk,))
        if not row:
            abort(404)
        if request.method == "POST":
            sets, vals = [], []
            for c in cols:
                if c["readonly"] or c["is_pk"]:
                    continue
                v = convert(c, request.form)
                if table == "User" and c["name"] == "PasswordHash":
                    if not v:
                        continue  # blank = keep current password
                    v = hash_password(v)
                sets.append(f"[{c['name']}] = ?")
                vals.append(v)
            try:
                if sets:
                    db.execute(f"UPDATE Rental.[{table}] SET {', '.join(sets)} WHERE [{pkc['name']}] = ?",
                               tuple(vals) + (pk,))
                flash("Row updated.", "ok")
                return redirect(url_for("admin_table", table=table))
            except pyodbc.Error as e:
                flash(db_msg(e), "error")
        return render_template("admin_row_edit.html", table=table, cols=cols, row=row, pk=pk)

    @app.route("/admin/tables/<table>/rows/<pk>/delete", methods=["POST"])
    @admin
    def row_delete(table, pk):
        table = get_table(table)
        if table == "Customer" and pk.isdigit():  # a customer owns bookings, payments and a login: use the full delete
            return redirect(url_for("delete_customer", customer_id=int(pk)))
        if table == "Vehicle" and pk.isdigit():  # a car has booking history: use the safe delete
            return redirect(url_for("delete_vehicle", vehicle_id=int(pk)))
        pkc = pk_of(get_columns(table))
        if not pkc:
            abort(400)
        try:
            n = db.execute(f"DELETE FROM Rental.[{table}] WHERE [{pkc['name']}] = ?", (pk,))
            flash("Row deleted." if n else "Row not found.", "ok" if n else "error")
        except pyodbc.Error as e:
            flash(db_msg(e), "error")
        return redirect(url_for("admin_table", table=table))

    @app.route("/admin/tables/<table>/columns/add", methods=["POST"])
    @admin
    def column_add(table):
        table = get_table(table)
        cname, ctype = request.form.get("col_name", "").strip(), request.form.get("col_type")
        existing = {c["name"].lower() for c in get_columns(table)}
        if not NAME_RE.match(cname) or cname.lower() in existing or ctype not in TYPES:
            flash("Invalid or repeated column name.", "error")
        else:
            try:  # optional (NULL) so it works on tables that already hold rows
                db.execute(f"ALTER TABLE Rental.[{table}] ADD [{cname}] {TYPES[ctype]} NULL")
                flash(f"Column {cname} added.", "ok")
            except pyodbc.Error as e:
                flash(db_msg(e), "error")
        return redirect(url_for("admin_table", table=table))

    @app.route("/admin/tables/<table>/columns/<col>/drop", methods=["POST"])
    @admin
    def column_drop(table, col):
        table = get_table(table)
        cols = {c["name"]: c for c in get_columns(table)}
        if table in CORE:
            flash("Columns of the system tables are protected. Change them in SQL Server.", "error")
        elif col not in cols or cols[col]["is_pk"]:
            flash("That column can't be removed.", "error")
        else:
            try:
                db.execute(f"ALTER TABLE Rental.[{table}] DROP COLUMN [{col}]")
                flash(f"Column {col} removed.", "ok")
            except pyodbc.Error as e:
                flash(db_msg(e), "error")
        return redirect(url_for("admin_table", table=table))

    @app.route("/admin/tables/<table>/drop", methods=["POST"])
    @admin
    def table_drop(table):
        table = get_table(table)
        if table in CORE:
            flash(f"{table} is a system table used by the website, so it is protected.", "error")
        elif request.form.get("confirm", "").strip() != table:
            flash("Type the table name exactly to confirm.", "error")
            return redirect(url_for("admin_table", table=table))
        else:
            try:
                db.execute(f"DROP TABLE Rental.[{table}]")
                flash(f"Table {table} removed.", "ok")
                return redirect(url_for("admin_tables"))
            except pyodbc.Error as e:
                flash(db_msg(e), "error")
                return redirect(url_for("admin_table", table=table))
        return redirect(url_for("admin_tables"))
