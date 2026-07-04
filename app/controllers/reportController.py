from flask import render_template, request, redirect, url_for, flash
from app.database import get_connection


def index():
    if request.method == "POST":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO threat_reports (reported_url, threat_type, description, reporter_email) VALUES (%s,%s,%s,%s)",
            (request.form.get("url"), request.form.get("threat_type"),
             request.form.get("description"), request.form.get("email"))
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Report submitted. Thank you for helping keep the internet safe!", "success")
        return redirect(url_for("report.index"))
    return render_template("report.html")
