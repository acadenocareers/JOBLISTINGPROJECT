import sqlite3
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

conn = sqlite3.connect("users.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT,
    email TEXT
)
""")

print("\nCreate Admin Account")

admin_email = input("Admin Email: ")
admin_password = input("Admin Password: ")

hashed = bcrypt.generate_password_hash(admin_password).decode()

c.execute("""
INSERT OR IGNORE INTO users(username,password,role,email)
VALUES (?,?,?,?)
""", (admin_email, hashed, "admin", admin_email))

conn.commit()
conn.close()

print("\n✅ Admin account created successfully  ")
