# ========================================================
# ==      © 2026 VPsPs Team. All Rights Reserved.       ==
# ==      SMS Spam Classifier Web App using Flask       ==
# ========================================================

from flask import Flask, render_template, request, jsonify
from joblib import load
import nltk
import string
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from flask_cors import CORS
import os  # used to read PORT for Render deployment
import logging

app = Flask(__name__)
CORS(app)  # <-- allow cross-origin requests (for Hoppscotch / Android / Browser clients)

# Load trained model and vectorizer
model = load("model/model.joblib")
vectorizer = load("model/vectorizer.joblib")

# Download required nltk resources (only first time)
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

ps = PorterStemmer()
stop_words = set(stopwords.words('english'))  # optimized (not inside loop)

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
        if i not in stop_words and i not in string.punctuation:
            y.append(i)

    text = y[:]
    y.clear()

    for i in text:
        y.append(ps.stem(i))

    return " ".join(y)
# =============================================

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    confidence = None
    message = ""   # store the user message

    if request.method == "POST":
        message = request.form.get("message", "")   # get message from form

        # Apply same preprocessing
        clean = transform_text(message)

        # Vectorization
        vect = vectorizer.transform([clean])

        # Prediction
        pred = model.predict(vect)[0]

        # Confidence score
        prob = model.predict_proba(vect)[0]
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
# API Endpoint (for Android App)
# ========================================================

@app.route("/api/predict", methods=["POST"])
def api_predict():

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Message not provided"}), 400

    message = data["message"]

    # Apply same preprocessing
    clean = transform_text(message)

    # Vectorization
    vect = vectorizer.transform([clean])

    # Prediction
    pred = model.predict(vect)[0]

    # Confidence score
    prob = model.predict_proba(vect)[0]
    confidence = round(max(prob) * 100, 2)

    prediction = "Spam" if pred == 1 else "Ham"

    return jsonify({
        "prediction": prediction,
        "confidence": confidence
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

