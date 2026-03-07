# app.py
# ========================================================
# SMS Spam Classifier Web App (Flask) — API + UI
# ========================================================

from flask import Flask, render_template, request, jsonify
from joblib import load
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from flask_cors import CORS
import os
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)  # <-- allow cross-origin requests (for Hoppscotch / Android / Browser clients)

# Load trained model and vectorizer (ensure these files exist in model/)
model = load("model/model.joblib")
vectorizer = load("model/vectorizer.joblib")

# Ensure required NLTK resources are present (first startup will download them)
nltk.download('punkt')
nltk.download('stopwords')

ps = PorterStemmer()
stop_words = set(stopwords.words('english'))


def transform_text(text: str) -> str:
    """Same preprocessing used during training."""
    if not isinstance(text, str):
        text = str(text)
    text = text.lower()
    text = nltk.word_tokenize(text)

    y = []
    for i in text:
        if i.isalnum():
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        if i not in stop_words and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)


# ---------- Web UI routes (unchanged) ----------
@app.route("/", methods=["GET", "POST"])
def index():
    # This route renders the UI and uses form POST (for the website).
    prediction = None
    confidence = None
    message = ""

    if request.method == "POST":
        message = request.form.get("message", "")
        clean = transform_text(message)
        vect = vectorizer.transform([clean])
        pred = model.predict(vect)[0]
        prob = model.predict_proba(vect)[0]
        confidence = round(max(prob) * 100, 2)
        prediction = "Spam" if pred == 1 else "Ham"

    return render_template("index.html", prediction=prediction, confidence=confidence, message=message)


@app.route("/about")
def about():
    return render_template("about.html")


# ---------- API route for JSON clients (Hoppscotch / Android) ----------
@app.route("/api/predict", methods=["POST"])
def api_predict():
    try:
        # Accept JSON body { "message": "..." }
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid or empty JSON body. Expected { 'message': '...' }"}), 400

        message = data.get("message", "")
        if not message:
            return jsonify({"error": "Missing 'message' field in JSON body."}), 400

        # Preprocess, vectorize, predict
        clean = transform_text(message)
        vect = vectorizer.transform([clean])

        pred = model.predict(vect)[0]
        prob = model.predict_proba(vect)[0]
        confidence = round(max(prob) * 100, 2)
        label = "Spam" if pred == 1 else "Ham"

        return jsonify({
            "prediction": label,
            "confidence": confidence,
            "message": message
        }), 200

    except Exception as e:
        logging.exception("Error in /api/predict")
        return jsonify({"error": "Server error", "details": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # bind to 0.0.0.0 for Render
    app.run(host="0.0.0.0", port=port)
