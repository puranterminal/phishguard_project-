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
    conn = pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS phishguard_db")
    conn.commit()
    cursor.close()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Topics table
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

    # Quiz attempts table
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

    # Threat reports table
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

    # Lesson likes table
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

    # Lesson comments table
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

    conn.commit()
    cursor.close()
    conn.close()
    _seed_admin()
    _seed_data()


def _seed_admin():
    """Creates default admin if not exists."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        ("admin@admin.com",)
    )
    if not cursor.fetchone():
        from werkzeug.security import generate_password_hash
        cursor.execute(
            "INSERT INTO users (name, email, password, role)"
            " VALUES (%s, %s, %s, %s)",
            ("Admin", "admin@admin.com",
             generate_password_hash("admin123"), "admin"),
        )
        conn.commit()
        print("Admin created: admin@admin.com / admin123")
    cursor.close()
    conn.close()

def _seed_data():
    """Seeds 8 lessons and 15 quiz questions if tables are empty."""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as cnt FROM topics")
    if cursor.fetchone()["cnt"] == 0:
        lessons = [
            (1, "What is Phishing?", "beginner",
             "<h2>What is Phishing?</h2><p>Phishing is a social engineering attack to steal data.</p>"),
            (2, "Types of Phishing Attacks", "beginner",
             "<h2>Types of Phishing</h2><p>Email, Spear, Smishing, Vishing, Whaling.</p>"),
            (3, "Recognizing Phishing Emails", "beginner",
             "<h2>Recognizing Phishing</h2><p>Check sender, links, urgency.</p>"),
            (4, "URL Analysis and Spoofing", "intermediate",
             "<h2>URL Analysis</h2><p>Check the real domain name carefully.</p>"),
            (5, "Social Engineering Tactics", "intermediate",
             "<h2>Social Engineering</h2><p>Authority, urgency, fear triggers.</p>"),
            (6, "Email Header Analysis", "intermediate",
             "<h2>Email Headers</h2><p>SPF, DKIM, DMARC checks explained.</p>"),
            (7, "Advanced Phishing Techniques", "advanced",
             "<h2>Advanced Techniques</h2><p>AiTM, BitB, Quishing attacks.</p>"),
            (8, "Building a Phishing-Resistant Culture", "advanced",
             "<h2>Resistant Culture</h2><p>Training, controls, incident response.</p>"),
        ]
        for order, title, diff, content in lessons:
            cursor.execute(
                "INSERT INTO topics (order_num,title,difficulty,content)"
                " VALUES (%s,%s,%s,%s)",
                (order, title, diff, content))

    cursor.execute("SELECT COUNT(*) as cnt FROM quiz_questions")
    if cursor.fetchone()["cnt"] == 0:
        questions = [
            ("What is phishing?", "A sport", "Cyberattack to steal info",
             "Software update", "A virus", 2, "beginner", "Phishing tricks users."),
            ("Red flag in phishing email?", "Your name", "Colleague email",
             "Urgent language", "Professional letterhead", 3, "beginner",
             "Urgency bypasses thinking."),
            ("Before clicking email link?", "Click if looks real",
             "Hover to preview URL", "Forward to friends", "Reply sender",
             2, "beginner", "Hovering reveals true URL."),
            ("HTTPS indicates?", "Site is safe", "Site is legitimate",
             "Connection encrypted", "Government verified",
             3, "beginner", "HTTPS = encrypted only."),
            ("Most likely phishing email?", "service@paypal.com",
             "support@paypal.com", "security@paypa1-verify.com",
             "help@paypal.com", 3, "beginner", "paypa1 uses 1 not l."),
            ("What is spear phishing?", "Fishing metaphors", "Mass emails",
             "Targeted personal attacks", "Phishing via SMS",
             3, "intermediate", "Spear phishing is targeted."),
            ("SPF stands for?", "Security Protection Framework",
             "Sender Policy Framework", "Spam Prevention Filter",
             "Secure Password Format", 2, "intermediate",
             "SPF authorizes mail servers."),
            ("Account deletes in 24hrs uses?", "Social proof", "Reciprocity",
             "Urgency/Scarcity", "Liking", 3, "intermediate",
             "Urgency bypasses rational thinking."),
            ("What is typosquatting?", "Typo emails",
             "Registering misspelled domains", "Hacking", "Ransomware",
             2, "intermediate", "Typosquatting registers similar domains."),
            ("Bank email asks to verify?", "Click and log in",
             "Reply with details", "Go directly to bank website",
             "Call email number", 3, "intermediate",
             "Always go directly to official site."),
            ("What is AiTM attack?", "Physical mail",
             "Proxy that bypasses MFA", "Wireless attack", "AI detection",
             2, "advanced", "AiTM captures session tokens."),
            ("Which auth resists phishing?", "SMS OTP", "Email codes",
             "TOTP apps", "FIDO2 hardware keys",
             4, "advanced", "FIDO2 verifies domain cryptographically."),
            ("Browser-in-Browser attack?", "Hack session",
             "Install extensions", "Fake popup inside real browser",
             "Denial of service", 3, "advanced", "BitB fakes OAuth login popup."),
            ("DMARC primary function?", "Encrypt email", "Block attachments",
             "Handle SPF and DKIM failures", "Scan malware",
             3, "advanced", "DMARC builds on SPF and DKIM."),
            ("BEC main goal?", "Install ransomware", "Steal passwords",
             "Fraudulent wire transfers", "Deface websites",
             3, "advanced", "BEC targets financial fraud."),
        ]
        for q in questions:
            cursor.execute(
                "INSERT INTO quiz_questions (question,option1,option2,option3,"
                "option4,correct_answer,question_type,explanation)"
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", q)

    conn.commit()
    cursor.close()
    conn.close()