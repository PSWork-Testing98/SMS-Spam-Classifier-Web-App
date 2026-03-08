# SMS Spam Classifier Web Application

This project is a **Machine Learning powered SMS Spam Detection Web Application** built using **Python, Flask, and Scikit-Learn**.
The system analyzes a user's message and predicts whether it is **Spam** or **Ham (Not Spam)** using Natural Language Processing (NLP) techniques.

The application includes a **clean and responsive web interface**, allowing users to input a message and instantly receive a prediction along with a **confidence score** indicating how certain the model is about its prediction.

---

# Project Overview

SMS spam messages are commonly used for **phishing, scams, fraud, and malicious advertising**.
Detecting such messages automatically helps users avoid harmful links and suspicious offers.

This project implements a **Machine Learning based spam classifier** that processes user input, converts the text into numerical features, and predicts whether the message is spam or legitimate.

---

# Machine Learning Pipeline

The system follows a typical **Natural Language Processing pipeline**:

User Message
↓
Text Preprocessing
↓
Tokenization
↓
Stopword Removal
↓
Stemming
↓
TF-IDF Vectorization
↓
Machine Learning Model
↓
Spam / Ham Prediction

---

# Text Preprocessing

Before feeding the text to the model, the input message goes through several preprocessing steps:

1. **Lowercasing** – Convert all characters to lowercase
2. **Tokenization** – Split text into individual words
3. **Stopword Removal** – Remove common words like "the", "is", "and"
4. **Punctuation Removal** – Remove special characters
5. **Stemming** – Reduce words to their root form using **PorterStemmer**

Example:

Original Message:
Win a FREE lottery now!!!

After preprocessing:
win free lotteri

---

# Feature Extraction

To convert text into numbers that the machine learning model can understand, the project uses:

**TF-IDF Vectorization**

TF-IDF stands for:

Term Frequency – Inverse Document Frequency

It measures how important a word is within a message relative to the entire dataset.

This helps the model identify **keywords commonly associated with spam messages**.

---

# Machine Learning Model

The classifier used in this project is:

**Multinomial Naive Bayes**

Why Naive Bayes?

* Works very well for **text classification**
* Efficient for large text datasets
* Fast training and prediction
* High accuracy for spam detection problems

---

# Confidence Score

Along with the prediction (Spam or Ham), the system also shows a **confidence score**.

The confidence score represents how certain the model is about its prediction.

Example:

Prediction: Spam
Confidence: 96.4%

This value is calculated using the model's probability output:

```python
prob = model.predict_proba(vect)[0]
confidence = max(prob) * 100
```

Higher confidence indicates the model is **more certain about its prediction**.

---

# Features

* Real-time **Spam / Ham prediction**
* **Confidence score** for prediction reliability
* Advanced **text preprocessing pipeline**
* Uses **TF-IDF feature extraction**
* Machine learning powered classification
* Modern **responsive web interface**
* Built with **Flask web framework**

---

# Tech Stack

### Programming Language

Python

### Machine Learning

Scikit-Learn

### NLP Tools

NLTK

### Feature Extraction

TF-IDF Vectorizer

### Model

Multinomial Naive Bayes

### Backend

Flask

### Frontend

HTML
CSS

### Model Storage

Joblib

---

# How the Web Application Works

1. User enters a message in the text area
2. The message is sent to the Flask backend
3. The backend preprocesses the text
4. TF-IDF converts the message into numerical features
5. The trained model predicts **Spam or Ham**
6. The confidence score is calculated
7. The result is displayed on the webpage

---

# How to Run the Project

### 1 Install dependencies

```bash
pip install -r requirements.txt
```

### 2 Run the Flask application

```bash
python app.py
```

### 3 Open the application in your browser

```
http://127.0.0.1:5000
```

---

# Project Structure

```
sms_spam_web/
│
├── app.py
├── requirements.txt
├── model/
│   ├── model.joblib
│   └── vectorizer.joblib
├── templates/
│   ├── base.html
│   ├── index.html
│   └── about.html
├── static/
│   ├── style.css
│   └── images/
│       ├── Member1.png
│       ├── Member2.png
│       ├── logo.png
│       └── logo2.png
├── .gitignore
├── render.yaml
├── SMS_Spam_Classifier.ipynb
├── spam.csv
├── LICENSE
└── README.md
```

---

# Authors

**Priyanshu Sahoo**

**Vivek Pralhad Salunkhe**
