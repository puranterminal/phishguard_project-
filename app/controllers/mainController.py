from flask import render_template
from app.database import get_connection


def home():
    stats = {"lessons": 8, "questions": 15, "users": 0, "scans": 0}
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role != 'admin'")
        stats["users"] = cursor.fetchone()["cnt"]
        cursor.execute("SELECT COUNT(*) as cnt FROM phish_urls")
        stats["scans"] = cursor.fetchone()["cnt"]
        cursor.execute("SELECT COUNT(*) as cnt FROM topics")
        stats["lessons"] = cursor.fetchone()["cnt"]
        cursor.execute("SELECT COUNT(*) as cnt FROM quiz_questions")
        stats["questions"] = cursor.fetchone()["cnt"]
        cursor.close()
        conn.close()
    except Exception as e:
        print("Stats error:", e)
    return render_template("home.html", stats=stats)
