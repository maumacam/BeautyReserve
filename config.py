# config.py
import mysql.connector

def get_db_connection():
    # Adjust these to your XAMPP setup if needed
    return mysql.connector.connect(
        host="localhost",
        user="root",      # default XAMPP user
        password="",      # default empty password
        database="nailbooker"
    )
