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
    # Create DB if missing
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

# Topics table — stores all phishing lessons
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            content LONGTEXT NOT NULL,
            difficulty VARCHAR(20) DEFAULT 'beginner',
            order_num INT DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    ON UPDATE CURRENT_TIMESTAMP
        )
    """)

    # Quiz questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question TEXT NOT NULL,
            option1 VARCHAR(300) NOT NULL,
            option2 VARCHAR(300) NOT NULL,
            option3 VARCHAR(300) NOT NULL,
            option4 VARCHAR(300) NOT NULL,
            correct_answer INT NOT NULL,
            question_type VARCHAR(20) DEFAULT 'beginner',
            explanation TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Quiz attempts — records every quiz score
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            score INT NOT NULL,
            total_questions INT NOT NULL,
            percentage FLOAT NOT NULL,
            passed TINYINT(1) DEFAULT 0,
            completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)