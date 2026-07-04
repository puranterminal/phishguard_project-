import re
import json
from flask import render_template, request, redirect, url_for, session, flash
from app.database import get_connection


def analyze_url_security(url):
    score = 0
    warnings = []

    if not url.startswith("https://"):
        score += 25
        warnings.append("Missing HTTPS — connection is not encrypted")

    keywords = ["login", "verify", "secure", "account", "update", "confirm", "signin", "banking", "password"]
    for kw in keywords:
        if kw in url.lower():
            score += 10
            warnings.append(f'Suspicious keyword detected: "{kw}"')

    if len(url) > 75:
        score += 15
        warnings.append(f"URL is unusually long ({len(url)} characters)")

    if re.search(r"https?://(\d{1,3}\.){3}\d{1,3}", url):
        score += 30
        warnings.append("URL uses an IP address instead of a domain name")

    typos = ["facebok", "googel", "paypall", "amaz0n", "micr0soft", "gmal", "paypa1", "g00gle", "faceb00k"]
    for t in typos:
        if t in url.lower():
            score += 20
            warnings.append(f'Possible typosquatting detected: "{t}"')

    if score < 30:
        risk_level = "LOW"
    elif score < 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return score, risk_level, warnings


def index():
    result = None
    scans = []

    if session.get("user_id"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM phish_urls WHERE user_id=%s ORDER BY created_at DESC", (session["user_id"],))
        scans = cursor.fetchall()
        cursor.close()
        conn.close()
        for s in scans:
            if s["warnings"]:
                s["warnings"] = json.loads(s["warnings"])

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        if url:
            risk_score, risk_level, warnings = analyze_url_security(url)
            result = {"url": url, "risk_score": risk_score, "risk_level": risk_level, "warnings": warnings}
            if session.get("user_id"):
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO phish_urls (user_id, url, risk_score, risk_level, warnings) VALUES (%s,%s,%s,%s,%s)",
                    (session["user_id"], url, risk_score, risk_level, json.dumps(warnings))
                )
                conn.commit()
                cursor.close()
                conn.close()
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM phish_urls WHERE user_id=%s ORDER BY created_at DESC", (session["user_id"],))
                scans = cursor.fetchall()
                cursor.close()
                conn.close()
                for s in scans:
                    if s["warnings"]:
                        s["warnings"] = json.loads(s["warnings"])

    return render_template("scan.html", result=result, scans=scans)


def delete_scan(scan_id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phish_urls WHERE id=%s AND user_id=%s", (scan_id, session["user_id"]))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Scan record deleted.", "info")
    return redirect(url_for("scan.index"))


def email_analyzer():
    result = None
    if request.method == "POST":
        header_text = request.form.get("headers", "").strip()
        if header_text:
            score = 0
            warnings = []

            spf = re.search(r"spf=(pass|fail|softfail|neutral|none)", header_text, re.I)
            dkim = re.search(r"dkim=(pass|fail|none)", header_text, re.I)
            urgency = ["urgent", "immediate", "verify now", "act now", "suspended", "locked", "confirm immediately"]

            if spf:
                if spf.group(1).lower() in ("fail", "softfail"):
                    score += 30
                    warnings.append(f"SPF check failed ({spf.group(1)}) — sender may be spoofed")
            else:
                score += 15
                warnings.append("No SPF record found in headers")

            if dkim:
                if dkim.group(1).lower() == "fail":
                    score += 25
                    warnings.append("DKIM signature failed — email may have been tampered with")
            else:
                score += 10
                warnings.append("No DKIM signature found")

            for phrase in urgency:
                if phrase in header_text.lower():
                    score += 10
                    warnings.append(f'Urgency phrase detected: "{phrase}"')

            risk_level = "LOW" if score < 30 else ("MEDIUM" if score < 60 else "HIGH")
            result = {"risk_score": score, "risk_level": risk_level, "warnings": warnings}

    return render_template("email_analyzer.html", result=result)
