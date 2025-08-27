# BeautyReserve
A web-based appointment booking system for nail technicians, featuring a dynamic service catalog, a booking form with time slot validation, and an admin dashboard to manage appointments. Built with Flask and MySQL.

# NailBooker – Nail Tech Appointment Booking System

NailBooker is a responsive web-based appointment booking system for nail technicians. It allows clients to browse services and book appointments online, while providing an admin dashboard for managing bookings.

---

## ✅ Features
- **Landing Page:** Displays available services with images, descriptions, and prices.
- **Booking System:** Clients can select a service, choose a date/time, and confirm their appointment.
- **Admin Dashboard:** Business owner can view, approve, or cancel appointments.
- **Responsive Design:** Works on desktop and mobile devices.
- **Database Integration:** Stores services and bookings in MySQL.

---

## 🛠 Tech Stack
- **Backend:** Flask (Python)
- **Frontend:** HTML, CSS (Bootstrap), Jinja2 Templates
- **Database:** MySQL
- **Authentication:** Flask-Login
- **Optional:** Flask-Mail for email confirmations

---

## 📂 Project Structure


nailtech_booking/
│
├── app.py                 # Main Flask app
├── config.py              # Database connection settings
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
│
├── /templates             # HTML templates
│    ├── index.html        # Landing page (services list)
│    ├── booking.html      # Booking form
│    ├── dashboard.html    # Admin dashboard
│    ├── login.html        # Owner login page
│
├── /static                # CSS, JS, images
│    ├── css/style.css
│    ├── images/           # Nail design images
│
└── /models                # (Optional) DB helper functions
     ├── booking_model.py
     ├── service_model.py


