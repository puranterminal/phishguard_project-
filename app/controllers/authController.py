from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import get_connection
from app.repository.user_repo import get_user_by_id


def login():
    if session.get("user_id"):
        user = get_user_by_id(session["user_id"])
        if user and user["role"] == "admin":
            return redirect(url_for("auth.dashboard"))
        return redirect(url_for("main.home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return render_template("login.html")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Login successful!", "success")
            if user["role"] == "admin":
                return redirect(url_for("auth.dashboard"))
            return redirect(url_for("main.home"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


def register():
    if session.get("user_id"):
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")
        if len(name) > 100:
            flash("Name must be under 100 characters.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("Email already exists.", "danger")
            cursor.close()
            conn.close()
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_password, "user"),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("auth.login"))


def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role FROM users WHERE role != 'admin'")
    total_users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("dashboard.html", users=total_users)


def profile():
    user_id = session["user_id"]
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")

        if not name or not email:
            flash("Name and email are required.", "danger")
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return render_template("profile.html", user=user)

        cursor.execute("SELECT * FROM users WHERE email = %s AND id != %s", (email, user_id))
        if cursor.fetchone():
            flash("Email already taken by another user.", "danger")
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            return render_template("profile.html", user=user)

        if new_password:
            if len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                return render_template("profile.html", user=user)

            cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
            stored = cursor.fetchone()
            if not check_password_hash(stored["password"], current_password):
                flash("Current password is incorrect.", "danger")
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cursor.fetchone()
                cursor.close()
                conn.close()
                return render_template("profile.html", user=user)

            hashed = generate_password_hash(new_password)
            cursor.execute(
                "UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s",
                (name, email, hashed, user_id),
            )
        else:
            cursor.execute(
                "UPDATE users SET name=%s, email=%s WHERE id=%s",
                (name, email, user_id),
            )

        conn.commit()
        session["user_name"] = name
        flash("Profile updated successfully!", "success")
        cursor.close()
        conn.close()
        return redirect(url_for("auth.profile"))

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("profile.html", user=user)


def editUsers(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
    user = cursor.fetchone()

    if not user:
        flash("User not found.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email:
            flash("Name and email are required.", "danger")
            cursor.close()
            conn.close()
            return render_template("editUser.html", user=user)

        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND id != %s", (email, id)
        )
        if cursor.fetchone():
            flash("Email already exists.", "danger")
            cursor.close()
            conn.close()
            return render_template("editUser.html", user=user)

        if password:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "UPDATE users SET name=%s, email=%s, password=%s WHERE id=%s",
                (name, email, hashed_password, id)
            )
        else:
            cursor.execute(
                "UPDATE users SET name=%s, email=%s WHERE id=%s",
                (name, email, id)
            )

        conn.commit()
        flash("User updated successfully.", "success")
        cursor.close()
        conn.close()
        return redirect(url_for("auth.dashboard"))

    cursor.close()
    conn.close()
    return render_template("editUser.html", user=user)


def deleteUser(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("User deleted successfully.", "success")
    return redirect(url_for("auth.dashboard"))