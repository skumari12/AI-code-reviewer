from flask import Flask, render_template, request, jsonify
from flask import redirect, url_for, session, flash

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from database import get_db_connection

from reviewer import review_code


app = Flask(__name__)

app.secret_key = "ai_code_reviewer_secret_key_2026"


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    if "user_id" in session:

        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# ==========================================
# SIGNUP
# ==========================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check empty fields

        if not name or not email or not password:

            flash("All fields are required.")

            return redirect(url_for("signup"))


        # Connect to MySQL

        connection = get_db_connection()

        cursor = connection.cursor()


        # Check whether email already exists

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        existing_user = cursor.fetchone()


        if existing_user:

            cursor.close()
            connection.close()

            flash("Email already registered.")

            return redirect(url_for("signup"))


        # Hash password

        hashed_password = generate_password_hash(password)


        # Insert user

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (
                name,
                email,
                hashed_password
            )
        )


        connection.commit()


        cursor.close()
        connection.close()


        flash("Account created successfully!")

        return redirect(url_for("login"))


    return render_template("signup.html")


# ==========================================
# LOGIN
# ==========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]


        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )


        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )


        user = cursor.fetchone()


        cursor.close()
        connection.close()


        # Check login

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]

            session["user_name"] = user["name"]

            session["user_email"] = user["email"]


            return redirect(
                url_for("dashboard")
            )


        flash("Invalid email or password.")

        return redirect(
            url_for("login")
        )


    return render_template("login.html")


# ==========================================
# DASHBOARD
# ==========================================

@app.route("/dashboard")
def dashboard():

    # User must be logged in

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "dashboard.html",

        name=session["user_name"],

        email=session["user_email"]
    )


# ==========================================
# CODE REVIEW
# ==========================================

@app.route("/review", methods=["POST"])
def review():

    # Check login

    if "user_id" not in session:

        return jsonify({
            "error": "Please login first."
        }), 401


    data = request.get_json()


    code = data.get(
        "code",
        ""
    )


    language = data.get(
        "language",
        "python"
    )


    if not code.strip():

        return jsonify({
            "error": "Please enter some code."
        }), 400


    # Run code reviewer

    result = review_code(
        code,
        language
    )


    # Save review to database

    connection = get_db_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO reviews
        (
            user_id,
            language,
            code,
            score,
            quality,
            summary
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        """,

        (
            session["user_id"],
            language,
            code,
            result.get("score", 0),
            result.get("quality", ""),
            result.get("summary", "")
        )
    )


    connection.commit()


    cursor.close()

    connection.close()


    return jsonify(result)


# ==========================================
# LOGOUT
# ==========================================

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.")

    return redirect(
        url_for("login")
    )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )