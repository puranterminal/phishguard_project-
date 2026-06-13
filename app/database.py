import pymysql
import config

def get_connection():
    try:
        return pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            cursorclass=pymysql.cursors.DictCursor,
        )
    except Exception as e:
        print("DB failed:", e)

def create_tables():

    conn = pymysql.connect(host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS phishguard_db")
    conn.commit(); cursor.close(); conn.close()

    conn = get_connection()
    cursor = conn.cursor()
    # Users table — name email password role
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(20) DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")