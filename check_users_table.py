import sqlite3

# Change this to your actual database name (e.g., 'chama.db' or similar)
db_file = "your_database_name.db"  # <-- UPDATE THIS with correct DB name

conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# List all tables
print("📋 Available tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for t in tables:
    print(f" - {t[0]}")

# Try showing the structure of users table
print("\n📦 Structure of 'users' table (if exists):")
try:
    cursor.execute("PRAGMA table_info(users);")
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            print(row)
    else:
        print("No columns found in 'users' table.")
except Exception as e:
    print(f"Error: {e}")

conn.close()
