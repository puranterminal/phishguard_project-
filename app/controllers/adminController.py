from flask import render_template, request, redirect, url_for, session, flash
from app.database import get_connection


def dashboard():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role != 'admin'")
    user_count = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM topics")
    lesson_count = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM quiz_questions")
    q_count = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM threat_reports WHERE status='pending'")
    report_count = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM phish_urls")
    scan_count = cursor.fetchone()["cnt"]
    cursor.execute("SELECT * FROM threat_reports ORDER BY created_at DESC")
    reports = cursor.fetchall()
    cursor.execute("SELECT id, name, email, role, created_at FROM users WHERE role != 'admin' ORDER BY created_at DESC")
    users = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("admin/dashboard.html",
                           user_count=user_count, lesson_count=lesson_count,
                           q_count=q_count, report_count=report_count,
                           scan_count=scan_count, reports=reports, users=users)


def resolve_report(rid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE threat_reports SET status='resolved' WHERE id=%s", (rid,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Report marked as resolved.", "success")
    return redirect(url_for("admin.dashboard"))
