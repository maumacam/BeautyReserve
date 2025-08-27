# fix_password.py
from werkzeug.security import generate_password_hash
from config import get_db_connection

# Generate hashed version of 'admin123'
hashed_password = generate_password_hash('admin123')
print(f"New hashed password: {hashed_password}")

# Update database
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("UPDATE users SET password=%s WHERE username='admin'", (hashed_password,))
conn.commit()
conn.close()

print("✓ Password updated successfully! Now try logging in.")