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

# URL scan results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS phish_urls (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            url VARCHAR(2000) NOT NULL,
            risk_score INT NOT NULL,
            risk_level VARCHAR(20) NOT NULL,
            warnings TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE SET NULL
        )
    """)

    # Threat reports from users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threat_reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            reported_url VARCHAR(2000) NOT NULL,
            threat_type VARCHAR(100),
            description TEXT,
            reporter_email VARCHAR(120),
            status VARCHAR(20) DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Lesson votes — UNIQUE KEY means one vote per user per lesson
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lesson_likes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            lesson_id INT NOT NULL,
            like_type VARCHAR(10) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_vote (user_id, lesson_id),
            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES topics(id)
                ON DELETE CASCADE
        )
    """)

    # Lesson comments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lesson_comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            lesson_id INT NOT NULL,
            comment TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
                ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES topics(id)
                ON DELETE CASCADE
        )
    """)