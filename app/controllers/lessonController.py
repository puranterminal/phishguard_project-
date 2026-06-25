from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.database import get_connection


def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics ORDER BY order_num")
    lessons = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("lessons.html", lessons=lessons)


def detail(lesson_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM topics WHERE id = %s", (lesson_id,))
    lesson = cursor.fetchone()
    if not lesson:
        flash("Lesson not found.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("lessons.index"))

    cursor.execute("""
        SELECT lc.*, u.name as username
        FROM lesson_comments lc
        JOIN users u ON lc.user_id = u.id
        WHERE lc.lesson_id = %s
        ORDER BY lc.created_at DESC
    """, (lesson_id,))
    comments = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) as cnt FROM lesson_likes WHERE lesson_id=%s AND like_type='like'", (lesson_id,))
    likes = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM lesson_likes WHERE lesson_id=%s AND like_type='dislike'", (lesson_id,))
    dislikes = cursor.fetchone()["cnt"]

    user_vote = None
    if session.get("user_id"):
        cursor.execute("SELECT like_type FROM lesson_likes WHERE user_id=%s AND lesson_id=%s",
                       (session["user_id"], lesson_id))
        row = cursor.fetchone()
        user_vote = row["like_type"] if row else None

    cursor.execute("SELECT id, title FROM topics WHERE order_num > %s ORDER BY order_num LIMIT 1",
                   (lesson["order_num"],))
    next_lesson = cursor.fetchone()

    cursor.execute("SELECT id, title FROM topics WHERE order_num < %s ORDER BY order_num DESC LIMIT 1",
                   (lesson["order_num"],))
    prev_lesson = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template("lesson_detail.html", lesson=lesson, comments=comments,
                           likes=likes, dislikes=dislikes, user_vote=user_vote,
                           next_lesson=next_lesson, prev_lesson=prev_lesson)


def vote(lesson_id):
    if not session.get("user_id"):
        return jsonify({"error": "Login required"}), 401

    vote_type = request.form.get("type")
    if vote_type not in ("like", "dislike"):
        return jsonify({"error": "Invalid vote"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM lesson_likes WHERE user_id=%s AND lesson_id=%s",
                   (session["user_id"], lesson_id))
    existing = cursor.fetchone()

    if existing:
        if existing["like_type"] == vote_type:
            cursor.execute("DELETE FROM lesson_likes WHERE user_id=%s AND lesson_id=%s",
                           (session["user_id"], lesson_id))
        else:
            cursor.execute("UPDATE lesson_likes SET like_type=%s WHERE user_id=%s AND lesson_id=%s",
                           (vote_type, session["user_id"], lesson_id))
    else:
        cursor.execute("INSERT INTO lesson_likes (user_id, lesson_id, like_type) VALUES (%s,%s,%s)",
                       (session["user_id"], lesson_id, vote_type))

    conn.commit()

    cursor.execute("SELECT COUNT(*) as cnt FROM lesson_likes WHERE lesson_id=%s AND like_type='like'", (lesson_id,))
    likes = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM lesson_likes WHERE lesson_id=%s AND like_type='dislike'", (lesson_id,))
    dislikes = cursor.fetchone()["cnt"]
    cursor.execute("SELECT like_type FROM lesson_likes WHERE user_id=%s AND lesson_id=%s",
                   (session["user_id"], lesson_id))
    row = cursor.fetchone()
    user_vote = row["like_type"] if row else None

    cursor.close()
    conn.close()
    return jsonify({"likes": likes, "dislikes": dislikes, "user_vote": user_vote})


def add_comment(lesson_id):
    if not session.get("user_id"):
        flash("Login required to comment.", "danger")
        return redirect(url_for("auth.login"))

    text = request.form.get("comment", "").strip()
    if not text:
        flash("Comment cannot be empty.", "danger")
        return redirect(url_for("lessons.detail", lesson_id=lesson_id))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lesson_comments (user_id, lesson_id, comment) VALUES (%s,%s,%s)",
                   (session["user_id"], lesson_id, text))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Comment added!", "success")
    return redirect(url_for("lessons.detail", lesson_id=lesson_id))


def delete_comment(comment_id):
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lesson_comments WHERE id=%s", (comment_id,))
    c = cursor.fetchone()

    if c and (c["user_id"] == session["user_id"] or session.get("is_admin")):
        lesson_id = c["lesson_id"]
        cursor.execute("DELETE FROM lesson_comments WHERE id=%s", (comment_id,))
        conn.commit()
        flash("Comment deleted.", "info")
        cursor.close()
        conn.close()
        return redirect(url_for("lessons.detail", lesson_id=lesson_id))

    flash("Not authorized.", "danger")
    cursor.close()
    conn.close()
    return redirect(url_for("lessons.index"))


# Admin CRUD
def admin_index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics ORDER BY order_num")
    lessons = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/lessons.html", lessons=lessons)


def admin_new():
    if request.method == "POST":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO topics (title, content, difficulty, order_num) VALUES (%s,%s,%s,%s)",
                       (request.form["title"], request.form["content"],
                        request.form["difficulty"], request.form["order_num"]))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Lesson created!", "success")
        return redirect(url_for("lessons.admin_index"))
    return render_template("admin/lesson_form.html", lesson=None)


def admin_edit(lesson_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics WHERE id=%s", (lesson_id,))
    lesson = cursor.fetchone()

    if request.method == "POST":
        cursor.execute("UPDATE topics SET title=%s, content=%s, difficulty=%s, order_num=%s WHERE id=%s",
                       (request.form["title"], request.form["content"],
                        request.form["difficulty"], request.form["order_num"], lesson_id))
        conn.commit()
        flash("Lesson updated!", "success")
        cursor.close()
        conn.close()
        return redirect(url_for("lessons.admin_index"))

    cursor.close()
    conn.close()
    return render_template("admin/lesson_form.html", lesson=lesson)


def admin_delete(lesson_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM topics WHERE id=%s", (lesson_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Lesson deleted.", "info")
    return redirect(url_for("lessons.admin_index"))
