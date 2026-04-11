# ========================================================
# ==      © 2026 VPsPs Team. All Rights Reserved.       ==
# ==      SMS Spam Classifier Web App using Flask       ==
# ========================================================

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
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import bcrypt
import jwt
import gdown
import os
import datetime
import re
app = Flask(__name__)
CORS(app)
app.secret_key                  = os.environ.get("SECRET_KEY",  "VPsPs-dev-secret-CHANGE-IN-PROD")
app.config["SESSION_PERMANENT"] = False
app.permanent_session_lifetime  = datetime.timedelta(days=30)
JWT_SECRET  = os.environ.get("JWT_SECRET",    "VPsPs-jwt-secret-CHANGE-IN-PROD")
API_KEY     = os.environ.get("API_KEY",        "VPsPs-2026-secret")
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://vpsps_db_user:3Yi2xnjynQt5VMbUEseGKvXtSLxMe3VA@dpg-d719ik75gffc73fl6gj0-a/vpsps_db")
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn
def get_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
def init_db():
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
def get_user_by_email(email: str):
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
        conn.rollback()
        conn.close()
        return False
def update_password(user_id: int, new_password: str):
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
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
def generate_reset_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "purpose": "reset",
        "exp":     datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
def verify_reset_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("purpose") != "reset":
            return None
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
def download_models():
    os.makedirs("model", exist_ok=True)
    if not os.path.exists("model/model.joblib"):
        print("Downloading model.joblib...")
        gdown.download("https://drive.google.com/uc?id=1oOxltj5kX83cdOQeIO4MkE9YpKVbuTqe",
                       "model/model.joblib", quiet=False)
    if not os.path.exists("model/vectorizer.joblib"):
        print("Downloading vectorizer.joblib...")
        gdown.download("https://drive.google.com/uc?id=1cyM3Y9MsndI3xnKEDj1amPZei92mFykN",
                       "model/vectorizer.joblib", quiet=False)
download_models()
model      = load("model/model.joblib")
vectorizer = load("model/vectorizer.joblib")
nltk.download("punkt",      quiet=True)
nltk.download("punkt_tab",  quiet=True)
nltk.download("stopwords",  quiet=True)
nltk.download("wordnet",    quiet=True)
stop_words = set(stopwords.words("english")) # optimized (not inside loop)
lemmatizer = WordNetLemmatizer() # initialized once
def transform_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'(.)\1+', r'\1\1', text)
    words = nltk.word_tokenize(text)
    words = [
        word for word in words
        if word.isalpha()
        and word not in stop_words
        and len(word) > 1
    ]
    words = [lemmatizer.lemmatize(word) for word in words]
    return " ".join(words)
def build_features(message: str):
    clean = transform_text(message)
    vect = vectorizer.transform([clean]).toarray()
    num_characters = len(message)
    num_words      = len(nltk.word_tokenize(message))
    num_sentences  = len(nltk.sent_tokenize(message))
    extra_features = np.array([[num_characters, num_words, num_sentences]])
    return np.hstack((vect, extra_features))
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please sign in to continue.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    prediction = None
    message    = ""
    error      = None
    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if not message:
            error = "Please enter a message."
        else:
            features   = build_features(message)
            pred       = model.predict(features)[0]
            prediction = "Spam" if pred == 1 else "Ham"
    return render_template(
        "index.html",
        prediction=prediction,
        message=message,
        error=error
    )
@app.route("/about")
def about():
    return render_template("about.html")
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
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("login"))
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
            print(f"\n[DEV] Password reset link for {email}:\n{reset_url}\n")
        flash(
            "If that email is registered, a reset link has been sent. "
            "Check your inbox.",
            "success"
        )
        return redirect(url_for("forgot_password"))
    return render_template("forgot_password.html")
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
@app.route("/api/predict", methods=["POST"])
def api_predict():
    client_key = request.headers.get("x-api-key")
    if client_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Message not provided"}), 400
    message    = data["message"]
    features   = build_features(message)
    pred       = model.predict(features)[0]
    prediction = "Spam" if pred == 1 else "Ham"
    return jsonify({"prediction": prediction})
init_db()
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
