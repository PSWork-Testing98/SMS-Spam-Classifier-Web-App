# ========================================================
# ==      © 2026 VPsPs Team. All Rights Reserved.       ==
# ==      SMS Spam Classifier Web App using Flask       ==
# ========================================================

from flask import Flask, render_template, request, jsonify
from joblib import load
import nltk
import string
import numpy as np
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from flask_cors import CORS
import os  # used to read PORT for Render deployment

# =========================
# CONFIG
# =========================
# API key for security (optional, can be used in future for authentication)
API_KEY = os.environ.get("API_KEY", "VPsPs-2026-secret")

app = Flask(__name__)
CORS(app)  # <-- allow cross-origin requests (for Hoppscotch / Android / Browser clients)

# =========================
# LOAD MODEL
# =========================
# Load trained model and vectorizer
model = load("model/model.joblib")
vectorizer = load("model/vectorizer.joblib")

# =========================
# NLTK SETUP
# =========================
# Download required nltk resources (only first time), added 'quiet=True' for the cleaner logs.
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

stop_words = set(stopwords.words('english'))  # optimized (not inside loop)
lemmatizer = WordNetLemmatizer()  # initialized once

# =========================
# TEXT PREPROCESSING (MATCH TRAINING)
# =========================
# ===== SAME FUNCTION USED DURING TRAINING =====
def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []
    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i.isalpha() and i not in stop_words and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(lemmatizer.lemmatize(i))

    return " ".join(y)

# =========================
# FEATURE BUILDER (IMPORTANT)
# =========================
def build_features(message):
    clean = transform_text(message)

    # TF-IDF
    vect = vectorizer.transform([clean]).toarray()

    # Extra features (same as training)
    num_characters = len(message)
    num_words = len(nltk.word_tokenize(message))
    num_sentences = len(nltk.sent_tokenize(message))

    extra_features = np.array([[num_characters, num_words, num_sentences]])

    # Combine → FINAL = 7003 features
    final_features = np.hstack((vect, extra_features))

    return final_features

# =========================
# WEB ROUTES
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    confidence = None
    message = ""   # store the user message

    if request.method == "POST":
        message = request.form.get("message", "")   # get message from form

        features = build_features(message)

        pred = model.predict(features)[0]
        prob = model.predict_proba(features)[0]

        confidence = round(max(prob) * 100, 2)
        prediction = "Spam" if pred == 1 else "Ham"

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence,
        message=message   # send message back to template
    )

@app.route("/about")
def about():
    return render_template("about.html")

# ========================================================
# API Endpoint ROUTE (for Android App)
# ========================================================

@app.route("/api/predict", methods=["POST"])
def api_predict():

    # API key verification
    client_key = request.headers.get("x-api-key")

    if client_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Message not provided"}), 400

    message = data["message"]

    features = build_features(message)

    pred = model.predict(features)[0]
    prob = model.predict_proba(features)[0]

    confidence = round(max(prob) * 100, 2)
    prediction = "Spam" if pred == 1 else "Ham"

    return jsonify({
        "prediction": prediction,
        "confidence": confidence
    })

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
