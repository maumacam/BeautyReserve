from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import get_db_connection
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "change-me-in-production"

# ====== Email Configuration ======
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'   # Replace with your Gmail
app.config['MAIL_PASSWORD'] = 'your_app_password'      # Use Gmail App Password
app.config['MAIL_DEFAULT_SENDER'] = ('Nail Booker', 'your_email@gmail.com')

mail = Mail(app)

# ====== Services with multiple images for swipe feature ======
SERVICES = [
    {
        "slug": "classic-french",
        "name": "Classic French",
        "price": 20.00,
        "desc": "Timeless French tips with a natural base.",
        "images": ["acrylic_sculpt.jpg", "chrome_mirror.jpg", "gel_gloss.jpg"]
    },
    {
        "slug": "gel-gloss",
        "name": "Gel Gloss Manicure",
        "price": 28.00,
        "desc": "Long-lasting gel finish with high gloss.",
        "images": ["minimalist_line.jpg", "classic_french.jpg"]
    },
    {
        "slug": "acrylic-sculpt",
        "name": "Acrylic Sculpt",
        "price": 35.00,
        "desc": "Durable acrylic extensions shaped to perfection.",
        "images": ["acrylic_sculpt.jpg", "chrome_mirror.jpg", "gel_gloss.jpg"]
    },
    {
        "slug": "minimalist-line",
        "name": "Minimalist Line Art",
        "price": 25.00,
        "desc": "Clean, modern line designs in your favorite colors.",
        "images": ["minimalist_line.jpg", "classic_french.jpg"]
    },
    {
        "slug": "chrome-mirror",
        "name": "Chrome Mirror",
        "price": 32.00,
        "desc": "Eye-catching chrome finish for a bold look.",
        
    },
]


# Quick lookup for booking
SERVICE_NAME_BY_SLUG = {s["slug"]: s["name"] for s in SERVICES}

# ====== Utility ======
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

        if not all([name, contact, service_slug, date_str, time_str]):
            flash("Please fill out all fields.", "danger")
            return redirect(url_for("book"))

        try:
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

        # ====== Send Email to Admin ======
        try:
            msg = Message("New Booking Received", recipients=["admin_email@gmail.com"])  # Change to real admin email
            msg.body = f"""
Hello Admin,

You have a new booking:

Name: {name}
Contact: {contact}
Service: {service_name}
Date: {date_str}
Time: {time_str}

Please check your system for more details.
"""
            mail.send(msg)
        except Exception as e:
            print(f"Email sending failed: {e}")

        flash("Your appointment request has been submitted!", "success")
        return redirect(url_for("home"))

    return render_template("booking.html", services=SERVICES, title="Book Appointment")

@app.route("/service/<slug>")
def service_detail(slug):
    service = next((s for s in SERVICES if s["slug"] == slug), None)
    if not service:
        return "Service not found", 404
    return render_template("service_detail.html", service=service)

# ====== Admin Dashboard ======
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

if __name__ == "__main__":
    app.run(debug=True)
