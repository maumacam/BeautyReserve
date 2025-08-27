from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import get_db_connection

app = Flask(__name__)
app.secret_key = "change-me-in-production"

# ====== Hard-coded Nail Services for Homepage & Booking Select ======
SERVICES = [
    {
        "slug": "classic-french",
        "name": "Classic French",
        "price": 20.00,
        "desc": "Timeless French tips with a natural base.",
        "image": "classic_french.jpg"
    },
    {
        "slug": "gel-gloss",
        "name": "Gel Gloss Manicure",
        "price": 28.00,
        "desc": "Long-lasting gel finish with high gloss.",
        "image": "gel_gloss.jpg"
    },
    {
        "slug": "acrylic-sculpt",
        "name": "Acrylic Sculpt",
        "price": 35.00,
        "desc": "Durable acrylic extensions shaped to perfection.",
        "image": "acrylic_sculpt.jpg"
    },
    {
        "slug": "minimalist-line",
        "name": "Minimalist Line Art",
        "price": 25.00,
        "desc": "Clean, modern line designs in your favorite colors.",
        "image": "minimalist_line.jpg"
    },
    {
        "slug": "chrome-mirror",
        "name": "Chrome Mirror",
        "price": 32.00,
        "desc": "Eye-catching chrome finish for a bold look.",
        "image": "chrome_mirror.jpg"
    },
]

# Map slug -> name for quick lookup in booking form
SERVICE_NAME_BY_SLUG = {s["slug"]: s["name"] for s in SERVICES}

# ====== Utility: protect routes ======
def admin_required():
    return ('admin_logged_in' in session) and (session['admin_logged_in'] is True)

# ====== Routes ======

@app.route("/")
def home():
    return render_template("index.html", services=SERVICES, title="NailBooker")

@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        contact = request.form.get("contact", "").strip()
        service_slug = request.form.get("service")
        date_str = request.form.get("date")
        time_str = request.form.get("time")

        # Basic validation
        if not all([name, contact, service_slug, date_str, time_str]):
            flash("Please fill out all fields.", "danger")
            return redirect(url_for("book"))

        # Convert date/time
        try:
            # (Also ensures valid values)
            _ = datetime.strptime(date_str, "%Y-%m-%d")
            _ = datetime.strptime(time_str, "%H:%M")
        except ValueError:
            flash("Invalid date or time.", "danger")
            return redirect(url_for("book"))

        service_name = SERVICE_NAME_BY_SLUG.get(service_slug)
        if not service_name:
            flash("Selected service is invalid.", "danger")
            return redirect(url_for("book"))

        # Save booking
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bookings (customer_name, contact, service, date, time, status)
            VALUES (%s, %s, %s, %s, %s, 'Pending')
        """, (name, contact, service_name, date_str, time_str))
        conn.commit()
        cur.close()
        conn.close()

        flash("Your appointment request has been submitted!", "success")
        return redirect(url_for("home"))

    # GET -> show booking form
    return render_template("booking.html", services=SERVICES, title="Book Appointment")

@app.route("/dashboard")
def dashboard():
    if not admin_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, customer_name, contact, service, date, time, status
        FROM bookings
        ORDER BY date ASC, time ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("dashboard.html", bookings=rows, title="Dashboard")

@app.route("/approve/<int:booking_id>")
def approve(booking_id):
    if not admin_required():
        return redirect(url_for("login"))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET status='Approved' WHERE id=%s", (booking_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Booking approved.", "success")
    return redirect(url_for("dashboard"))

@app.route("/cancel/<int:booking_id>")
def cancel(booking_id):
    if not admin_required():
        return redirect(url_for("login"))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE bookings SET status='Cancelled' WHERE id=%s", (booking_id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Booking cancelled.", "warning")
    return redirect(url_for("dashboard"))

# ====== Auth ======
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form.get("username", "").strip()
        pw = request.form.get("password", "")

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM admins WHERE username=%s", (uname,))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row and check_password_hash(row[2], pw):
            session['admin_logged_in'] = True
            session['admin_username'] = row[1]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", title="Admin Login")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# ====== One-time helper to seed an admin with hashed password ======
# Visit /seed-admin once, then remove or protect it.
@app.route("/seed-admin")
def seed_admin():
    # CHANGE THESE BEFORE USING IN REAL PROJECT
    username = "admin"
    password = "admin123"

    hashed = generate_password_hash(password)
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO admins (username, password) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        msg = "Admin user created."
    except Exception as e:
        msg = f"Error: {e}"
    finally:
        cur.close()
        conn.close()

    return msg

if __name__ == "__main__":
    app.run(debug=True)
