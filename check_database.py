# check_database.py
from config import get_db_connection

# Connect to database and check what's stored
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE username='admin'")
admin = cursor.fetchone()

print("=== DATABASE CHECK ===")
print("Full record:", admin)

if admin:
    print(f"Username: {admin[1]}")
    print(f"Password: {admin[2]}")
    print(f"Password type: {type(admin[2])}")
    
    # Check if password looks hashed (contains $ symbols)
    if '$' in admin[2]:
        print("✓ Password appears to be hashed")
    else:
        print("✗ Password appears to be PLAIN TEXT (not hashed)")
else:
    print("No admin user found!")

conn.close()