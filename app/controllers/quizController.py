from flask import render_template, request, redirect, url_for, session, flash
from app.database import get_connection


def index():
    if not session.get("user_id"):
        flash("Please login to take the quiz.", "warning")
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_questions ORDER BY question_type, id")
    questions = cursor.fetchall()
    cursor.execute("SELECT * FROM quiz_attempts WHERE user_id=%s ORDER BY completed_at DESC LIMIT 5",
                   (session["user_id"],))
    past_attempts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("quiz.html", questions=questions, past_attempts=past_attempts)


def submit():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_questions ORDER BY question_type, id")
    questions = cursor.fetchall()

    score = 0
    results = []
    for q in questions:
        user_ans = request.form.get(f"q_{q['id']}")
        correct = str(q["correct_answer"])
        is_correct = user_ans == correct
        if is_correct:
            score += 1
        results.append({
            "question": q["question"],
            "options": [q["option1"], q["option2"], q["option3"], q["option4"]],
            "user_answer": int(user_ans) if user_ans else None,
            "correct_answer": q["correct_answer"],
            "is_correct": is_correct,
            "explanation": q["explanation"],
            "type": q["question_type"],
        })

    total = len(questions)
    percentage = round((score / total) * 100, 1) if total else 0
    passed = percentage >= 60

    cursor.execute(
        "INSERT INTO quiz_attempts (user_id, score, total_questions, percentage, passed) VALUES (%s,%s,%s,%s,%s)",
        (session["user_id"], score, total, percentage, int(passed))
    )
    conn.commit()
    cursor.close()
    conn.close()

    return render_template("quiz_result.html", score=score, total=total,
                           percentage=percentage, passed=passed, results=results)


def admin_index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_questions ORDER BY question_type, id")
    questions = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/questions.html", questions=questions)


def admin_new():
    if request.method == "POST":
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO quiz_questions (question, option1, option2, option3, option4,
               correct_answer, question_type, explanation) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
            (request.form["question"], request.form["option1"], request.form["option2"],
             request.form["option3"], request.form["option4"], request.form["correct_answer"],
             request.form["question_type"], request.form["explanation"])
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Question created!", "success")
        return redirect(url_for("quiz.admin_index"))
    return render_template("admin/question_form.html", question=None)


def admin_edit(qid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quiz_questions WHERE id=%s", (qid,))
    question = cursor.fetchone()

    if request.method == "POST":
        cursor.execute(
            """UPDATE quiz_questions SET question=%s, option1=%s, option2=%s, option3=%s,
               option4=%s, correct_answer=%s, question_type=%s, explanation=%s WHERE id=%s""",
            (request.form["question"], request.form["option1"], request.form["option2"],
             request.form["option3"], request.form["option4"], request.form["correct_answer"],
             request.form["question_type"], request.form["explanation"], qid)
        )
        conn.commit()
        flash("Question updated!", "success")
        cursor.close()
        conn.close()
        return redirect(url_for("quiz.admin_index"))

    cursor.close()
    conn.close()
    return render_template("admin/question_form.html", question=question)


def admin_delete(qid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quiz_questions WHERE id=%s", (qid,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Question deleted.", "info")
    return redirect(url_for("quiz.admin_index"))