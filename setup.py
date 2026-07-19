import os
import pymysql

print("=" * 40)
print("  PhishGuard — Setup")
print("=" * 40)

host     = input("MySQL Host (default: localhost): ").strip() or "localhost"
user     = input("MySQL Username (default: root): ").strip() or "root"
password = input("MySQL Password: ").strip()
database = input("Database name (default: phishguard_db): ").strip() or "phishguard_db"

env_content = f"""SECRET_KEY=phishguard-secret-2024
MYSQL_HOST={host}
MYSQL_USER={user}
MYSQL_PASSWORD={password}
MYSQL_DATABASE={database}
SQLALCHEMY_DATABASE_URI=mysql+pymysql://{user}:{password}@{host}/{database}
"""

with open(".env", "w") as f:
    f.write(env_content)

print("\n.env file created successfully.")
print("Creating database...")

try:
    conn = pymysql.connect(host=host, user=user, password=password)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Database '{database}' created successfully.")
except Exception as e:
    print(f"Database error: {e}")
    print("Please create the database manually in MySQL Workbench.")

print("\nSetup complete! Now run:")
print("  python run.py")
print("=" * 40)