import sqlite3

db_file = "your_database_name.db"  # <-- Replace with your real DB name

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create the users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'member'))
);
""")

conn.commit()
conn.close()
print("✅ 'users' table created successfully with columns: id, username, password, role.")
