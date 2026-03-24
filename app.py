# ========================================================
# ==      © 2026 VPsPs Team. All Rights Reserved.       ==
# ==      SMS Spam Classifier Web App using Flask       ==
# ========================================================

# ========================================================
# ==              DATABASE MIGRATION NOTES              ==
# ==                                                    ==
# ==  We migrated from SQLite → PostgreSQL for Render   ==
# ==  deployment because Render's free tier has an      ==
# ==  ephemeral filesystem (SQLite file gets wiped on   ==
# ==  every redeploy).                                  ==
# ==                                                    ==
# ==  PostgreSQL is free on Render and persists forever ==
# ==                                                    ==
# ==  KEY DIFFERENCES vs SQLite:                        ==
# ==  1. import psycopg2           (was sqlite3)        ==
# ==  2. %s placeholders           (was ?)              ==
# ==  3. RealDictCursor for rows   (was row_factory)    ==
# ==  4. SERIAL primary key        (was AUTOINCREMENT)  ==
# ==  5. NOW() for timestamps      (was datetime('now'))==
# ==  6. Single DATABASE_URL       (was file path)      ==
# ==                                                    ==
# ==  SQLite code is kept below each section as         ==
# ==  comments for reference and future use.            ==
# ========================================================


# ========================================================
# ==              FUTURE FEATURE — EMAIL SETUP          ==
# ==                                                    ==
# ==  STEP 1 — Install Flask-Mail                       ==
# ==     Run: pip install Flask-Mail                    ==
# ==     Add "Flask-Mail" to requirements.txt           ==
# ==                                                    ==
# ==  STEP 2 — Generate Gmail App Password              ==
# ==     a) Go to myaccount.google.com                  ==
# ==     b) Security → 2-Step Verification (enable it)  ==
# ==     c) Search "App Passwords" → Select Mail        ==
# ==     d) Click Generate → copy the 16-char password  ==
# ==                                                    ==
# ==  STEP 3 — Set Environment Variables on Render      ==
# ==     MAIL_USERNAME = yourgmail@gmail.com            ==
# ==     MAIL_PASSWORD = your-16-char-app-password      ==
# ==                                                    ==
# ==  STEP 4 — Uncomment all lines marked [EMAIL]       ==
# ==     There are exactly 3 places to uncomment:       ==
# ==     1. The import at the top                       ==
# ==     2. The mail config block                       ==
# ==     3. The mail.send() block in forgot_password()  ==
# ==                                                    ==
# ==  STEP 5 — Delete the print() line in              ==
# ==     forgot_password() once email is working        ==
# ========================================================


# =========================
# IMPORTS
# =========================
from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, flash, session
)
from joblib import load
from flask_cors import CORS
from functools import wraps

import nltk
import string
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ── Active: PostgreSQL ──────────────────────────────────
import psycopg2
import psycopg2.extras   # provides RealDictCursor (column access by name)

# ── Kept for reference: SQLite ──────────────────────────
# import sqlite3

import bcrypt
import jwt
import os
import datetime

# [EMAIL] STEP 1 — Uncomment this import when ready to enable email
# from flask_mail import Mail, Message


# =========================
# APP CONFIG
# =========================
app = Flask(__name__)
CORS(app)

# Secret key for session encryption
# Generate a strong one: python -c "import secrets; print(secrets.token_hex(32))"
# Set as environment variable on Render — never hardcode in production
app.secret_key                  = os.environ.get("SECRET_KEY",  "VPsPs-dev-secret-CHANGE-IN-PROD")

# Sessions die when browser closes unless Remember Me is ticked
app.config["SESSION_PERMANENT"] = False

# How long Remember Me sessions last
app.permanent_session_lifetime  = datetime.timedelta(days=30)

# JWT secret for signing password reset tokens
JWT_SECRET  = os.environ.get("JWT_SECRET",    "VPsPs-jwt-secret-CHANGE-IN-PROD")

# API key for the Android app — never changes, APK is not affected by DB migration
API_KEY     = os.environ.get("API_KEY",        "VPsPs-2026-secret")

# ── Active: PostgreSQL ──────────────────────────────────
# DATABASE_URL is automatically set by Render when you create a PostgreSQL database
# Format: postgresql://user:password@host:port/dbname
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://vpsps_db_user:3Yi2xnjynQt5VMbUEseGKvXtSLxMe3VA@dpg-d719ik75gffc73fl6gj0-a/vpsps_db")

# ── Kept for reference: SQLite ──────────────────────────
# DATABASE = os.environ.get("DATABASE", "users.db")


# [EMAIL] STEP 2 — Uncomment this entire block when ready to enable email
# app.config["MAIL_SERVER"]         = "smtp.gmail.com"
# app.config["MAIL_PORT"]           = 587
# app.config["MAIL_USE_TLS"]        = True
# app.config["MAIL_USE_SSL"]        = False
# app.config["MAIL_USERNAME"]       = os.environ.get("MAIL_USERNAME")
# app.config["MAIL_PASSWORD"]       = os.environ.get("MAIL_PASSWORD")
# app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")
# mail = Mail(app)


# =========================
# DATABASE SETUP
# =========================

def get_db():
    """
    Opens a new PostgreSQL connection using the DATABASE_URL from Render.
    RealDictCursor lets us access columns by name: user["email"]
    instead of by index: user[2]

    ── SQLite equivalent (kept for reference) ──────────────
    # def get_db():
    #     conn = sqlite3.connect(DATABASE)
    #     conn.row_factory = sqlite3.Row
    #     return conn
    # ────────────────────────────────────────────────────────
    """
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def get_cursor(conn):
    """
    Returns a RealDictCursor — every row comes back as a dict.
    e.g. row["username"] instead of row[1]

    ── SQLite equivalent ────────────────────────────────────
    # SQLite handled this automatically via conn.row_factory = sqlite3.Row
    # PostgreSQL needs an explicit cursor type
    # ────────────────────────────────────────────────────────
    """
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def init_db():
    """
    Creates the users table if it does not already exist.
    Called once at startup — safe to call multiple times (IF NOT EXISTS).

    Table structure:
        id            — auto-incrementing primary key (SERIAL in PostgreSQL)
        username      — unique, stored in lowercase
        email         — unique, stored in lowercase
        password_hash — bcrypt hash, never the plain password
        created_at    — auto-set to current UTC time on insert

    ── SQLite equivalent (kept for reference) ──────────────
    # def init_db():
    #     conn = get_db()
    #     conn.execute(
    #         CREATE TABLE IF NOT EXISTS users (
    #             id            INTEGER PRIMARY KEY AUTOINCREMENT,
    #             username      TEXT    NOT NULL UNIQUE,
    #             email         TEXT    NOT NULL UNIQUE,
    #             password_hash TEXT    NOT NULL,
    #             created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
    #         )
    #     )
    #     conn.commit()
    #     conn.close()
    # ────────────────────────────────────────────────────────
    """
    conn   = get_db()
    cursor = get_cursor(conn)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            SERIAL       PRIMARY KEY,
            username      VARCHAR(50)  NOT NULL UNIQUE,
            email         VARCHAR(255) NOT NULL UNIQUE,
            password_hash TEXT         NOT NULL,
            created_at    TIMESTAMP    NOT NULL DEFAULT NOW()
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


# =========================
# DB HELPER FUNCTIONS
# =========================

def get_user_by_email(email: str):
    """
    Fetch one user row by email. Returns None if not found.

    ── SQLite equivalent ────────────────────────────────────
    # conn = get_db()
    # user = conn.execute(
    #     "SELECT * FROM users WHERE email = ?", (email.lower(),)
    # ).fetchone()
    # conn.close()
    # return user
    # ────────────────────────────────────────────────────────
    """
    conn   = get_db()
    cursor = get_cursor(conn)
    cursor.execute(
        "SELECT * FROM users WHERE email = %s", (email.lower(),)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def get_user_by_username(username: str):
    """
    Fetch one user row by username. Returns None if not found.

    ── SQLite equivalent ────────────────────────────────────
    # conn = get_db()
    # user = conn.execute(
    #     "SELECT * FROM users WHERE username = ?", (username.lower(),)
    # ).fetchone()
    # conn.close()
    # return user
    # ────────────────────────────────────────────────────────
    """
    conn   = get_db()
    cursor = get_cursor(conn)
    cursor.execute(
        "SELECT * FROM users WHERE username = %s", (username.lower(),)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def get_user_by_id(user_id: int):
    """
    Fetch one user row by ID. Used after token verification.

    ── SQLite equivalent ────────────────────────────────────
    # conn = get_db()
    # user = conn.execute(
    #     "SELECT * FROM users WHERE id = ?", (user_id,)
    # ).fetchone()
    # conn.close()
    # return user
    # ────────────────────────────────────────────────────────
    """
    conn   = get_db()
    cursor = get_cursor(conn)
    cursor.execute(
        "SELECT * FROM users WHERE id = %s", (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def create_user(username: str, email: str, password: str) -> bool:
    """
    Hashes the password with bcrypt and inserts a new user.
    Returns True on success, False if username or email already exists.

    bcrypt.gensalt() generates a unique salt per user so two users
    with the same password will always have different hashes.

    ── SQLite equivalent ────────────────────────────────────
    # try:
    #     conn = get_db()
    #     conn.execute(
    #         "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
    #         (username.lower(), email.lower(), password_hash)
    #     )
    #     conn.commit()
    #     conn.close()
    #     return True
    # except sqlite3.IntegrityError:
    #     return False
    # ────────────────────────────────────────────────────────
    """
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    try:
        conn   = get_db()
        cursor = get_cursor(conn)
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
            (username.lower(), email.lower(), password_hash)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except psycopg2.IntegrityError:
        # Triggered when username or email violates the UNIQUE constraint
        conn.rollback()
        conn.close()
        return False


def update_password(user_id: int, new_password: str):
    """
    Hashes the new password and saves it to the database.
    Called after a successful password reset token verification.

    ── SQLite equivalent ────────────────────────────────────
    # conn = get_db()
    # conn.execute(
    #     "UPDATE users SET password_hash = ? WHERE id = ?",
    #     (password_hash, user_id)
    # )
    # conn.commit()
    # conn.close()
    # ────────────────────────────────────────────────────────
    """
    password_hash = bcrypt.hashpw(
        new_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    conn   = get_db()
    cursor = get_cursor(conn)
    cursor.execute(
        "UPDATE users SET password_hash = %s WHERE id = %s",
        (password_hash, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def verify_password(plain: str, hashed: str) -> bool:
    """
    Compares plain-text password against stored bcrypt hash.
    bcrypt.checkpw handles salt extraction automatically.
    This function is identical for both SQLite and PostgreSQL.
    """
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# =========================
# JWT HELPERS
# =========================

def generate_reset_token(user_id: int) -> str:
    """
    Creates a signed JWT for password reset.
    Expires in 30 minutes. purpose claim prevents token reuse.
    Identical for both SQLite and PostgreSQL.
    """
    payload = {
        "user_id": user_id,
        "purpose": "reset",
        "exp":     datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_reset_token(token: str):
    """
    Decodes and validates a reset token.
    Returns user_id on success, None on any failure.
    Identical for both SQLite and PostgreSQL.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("purpose") != "reset":
            return None
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# =========================
# LOAD ML MODEL
# =========================

# Load trained Naive Bayes model and TF-IDF vectorizer
# Completely unaffected by the database migration
model      = load("model/model.joblib")
vectorizer = load("model/vectorizer.joblib")


# =========================
# NLTK SETUP
# =========================

nltk.download("punkt",      quiet=True)
nltk.download("punkt_tab",  quiet=True)
nltk.download("stopwords",  quiet=True)
nltk.download("wordnet",    quiet=True)

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


# =========================
# NLP FUNCTIONS
# =========================

def transform_text(text: str) -> str:
    """
    Preprocesses raw message — must match training pipeline exactly.
    Unaffected by database migration.
    """
    text = text.lower()
    text = nltk.word_tokenize(text)
    y    = [i for i in text if i.isalnum()]
    y    = [i for i in y if i.isalpha()
            and i not in stop_words
            and i not in string.punctuation]
    y    = [lemmatizer.lemmatize(i) for i in y]
    return " ".join(y)


def build_features(message: str):
    """
    Builds 7003-feature vector (7000 TF-IDF + 3 extra).
    Unaffected by database migration.
    """
    clean          = transform_text(message)
    vect           = vectorizer.transform([clean]).toarray()
    num_characters = len(message)
    num_words      = len(nltk.word_tokenize(message))
    num_sentences  = len(nltk.sent_tokenize(message))
    extra          = np.array([[num_characters, num_words, num_sentences]])
    return np.hstack((vect, extra))


# =========================
# AUTH DECORATOR
# =========================

def login_required(f):
    """
    Blocks unauthenticated users and redirects to login.
    Unaffected by database migration.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please sign in to continue.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ========================================================
# WEB ROUTES
# ========================================================

# ─── Home (protected) ────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    prediction = None
    confidence = None
    message    = ""

    if request.method == "POST":
        message    = request.form.get("message", "")
        features   = build_features(message)
        pred       = model.predict(features)[0]
        prob       = model.predict_proba(features)[0]
        confidence = round(max(prob) * 100, 2)
        prediction = "Spam" if pred == 1 else "Ham"

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence,
        message=message
    )


# ─── About ───────────────────────────────────────────────
@app.route("/about")
def about():
    return render_template("about.html")


# ─── Login ───────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("index"))

    if request.method == "POST":
        identifier = request.form.get("username", "").strip()
        password   = request.form.get("password", "").strip()
        remember   = request.form.get("remember")

        if not identifier or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("login"))

        user = get_user_by_email(identifier) or get_user_by_username(identifier)

        if user is None or not verify_password(password, user["password_hash"]):
            flash("Invalid credentials. Please try again.", "error")
            return redirect(url_for("login"))

        session["logged_in"] = True
        session["user_id"]   = user["id"]
        session["username"]  = user["username"]

        if remember:
            session.permanent = True
        else:
            session.permanent = False

        return redirect(url_for("index"))

    return render_template("login.html")


# ─── Logout ──────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))


# ─── Register ────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("logged_in"):
        return redirect(url_for("index"))

    if request.method == "POST":
        username         = request.form.get("username", "").strip()
        email            = request.form.get("email", "").strip()
        password         = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if len(username) < 3:
            flash("Username must be at least 3 characters.", "error")
            return redirect(url_for("register"))

        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("register"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        if get_user_by_email(email):
            flash("An account with this email already exists.", "error")
            return redirect(url_for("register"))

        if get_user_by_username(username):
            flash("Username is already taken. Please choose another.", "error")
            return redirect(url_for("register"))

        success = create_user(username, email, password)
        if success:
            flash("Account created successfully! Please sign in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Registration failed. Please try again.", "error")
            return redirect(url_for("register"))

    return render_template("register.html")


# ─── Forgot Password ─────────────────────────────────────
@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if session.get("logged_in"):
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email:
            flash("Please enter your email address.", "error")
            return redirect(url_for("forgot_password"))

        user = get_user_by_email(email)

        if user:
            token     = generate_reset_token(user["id"])
            reset_url = url_for("reset_password", token=token, _external=True)

            # ════════════════════════════════════════════════
            # [EMAIL] STEP 3 — Uncomment this block to send
            # the reset email via Gmail SMTP.
            # ────────────────────────────────────────────────
            # msg      = Message(subject="Reset Your VPsPs Password",
            #                    recipients=[email])
            # msg.body = f"""Hello,
            #
            # You requested a password reset for your VPsPs account.
            #
            # Click the link below to reset your password.
            # This link expires in 30 minutes.
            #
            # {reset_url}
            #
            # If you did not request this, you can safely ignore this email.
            # Your password will not be changed.
            #
            # — VPsPs Team
            # """
            # mail.send(msg)
            # ════════════════════════════════════════════════

            # [EMAIL] STEP 4 — Delete this print() once email is working
            # For now the reset link prints to terminal for local testing
            print(f"\n[DEV] Password reset link for {email}:\n{reset_url}\n")

        # Always same message — never reveal if email exists
        flash(
            "If that email is registered, a reset link has been sent. "
            "Check your inbox.",
            "success"
        )
        return redirect(url_for("forgot_password"))

    return render_template("forgot_password.html")


# ─── Reset Password ──────────────────────────────────────
@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if session.get("logged_in"):
        return redirect(url_for("index"))

    user_id = verify_reset_token(token)
    if user_id is None:
        flash(
            "This reset link is invalid or has expired. "
            "Please request a new one.",
            "error"
        )
        return redirect(url_for("forgot_password"))

    if request.method == "POST":
        password         = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not password or not confirm_password:
            flash("Both fields are required.", "error")
            return redirect(url_for("reset_password", token=token))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return redirect(url_for("reset_password", token=token))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("reset_password", token=token))

        update_password(user_id, password)
        flash(
            "Password reset successfully! "
            "Please sign in with your new password.",
            "success"
        )
        return redirect(url_for("login"))

    return render_template("reset_password.html", token=token)


# ========================================================
# API ENDPOINT — Android App
# ========================================================

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """
    Protected API for the Android app.
    Uses API key authentication — completely unaffected by DB migration.
    Database is never touched in this route.
    """
    client_key = request.headers.get("x-api-key")
    if client_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message not provided"}), 400

    message    = data["message"]
    features   = build_features(message)
    pred       = model.predict(features)[0]
    prob       = model.predict_proba(features)[0]
    confidence = round(max(prob) * 100, 2)
    prediction = "Spam" if pred == 1 else "Ham"

    return jsonify({"prediction": prediction, "confidence": confidence})


# ========================================================
# STARTUP
# ========================================================

# CORRECT — runs on import, so gunicorn triggers it too
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
