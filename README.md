<div align="center">

<img src="static/images/logo.png" alt="SpamShield Logo" width="180"/>
<h1 style=font-weight: bold;>VPsPs Projects</h1>

# 🛡️ SMS Spam Filter using Machine Learning and Android Application

### An **AI-powered SMS spam detection system** that classifies messages as **Spam or Ham (Not Spam)** using Machine Learning

### The system integrates a **Flask-based backend API**, a **web application**, and an **Android application** for real-time SMS classification

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![NLTK](https://img.shields.io/badge/NLTK-NLP-154F3C?style=for-the-badge)](https://www.nltk.org/)
[![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://vpsps-projects-spam-sms-classifier-web.onrender.com/)

**[🌐 Live Demo →](https://vpsps-projects-spam-sms-classifier-web.onrender.com/)**

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Live Demo](#-live-demo)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Project Structure](#-project-structure)
- [Sample Test Messages](#-sample-test-messages)
- [How It Works](#️-how-it-works)
- [Authors](#-authors)
- [Android Version](#-android-version)
- [License](#-license)

---

## 🧩 Overview

SMS spam messages have become a major threat due to their involvement in **phishing attacks, fraud, malicious links, and unwanted advertisements**. Manual detection of such messages is inefficient and unreliable, creating a need for an automated and intelligent solution.

**SMS Spam Filter using Machine Learning and Android Application** is an end-to-end system that classifies SMS messages as **Spam or Ham (Not Spam)** using advanced Machine Learning techniques. The system integrates a **Flask-based backend API**, a **web application**, and an **Android application** to enable both manual and real-time SMS classification.

The Machine Learning model is built using a robust NLP pipeline that includes **text preprocessing, TF-IDF feature extraction (unigrams and bigrams), and additional numerical features** such as message length and word count. To handle class imbalance, **SMOTE (Synthetic Minority OverSampling Technique)** is applied, and the final model is implemented using a **Support Vector Machine (SVM)**, achieving high accuracy on real-world datasets.

The system is deployed on a cloud platform and provides a **scalable, secure, and practical solution** for real-time spam detection across multiple platforms.

---

## 🌐 Live Demo

> Experience the Spam SMS Classifier in action — explore how messages are detected and categorized instantly.

🔗 **[https://vpsps-projects-spam-sms-classifier-web.onrender.com/](https://vpsps-projects-spam-sms-classifier-web.onrender.com/)**

### 🔑 Login Credentials

- **Username**: `VPsPs`  
- **Password**: `Hello@1234`

---

## ✨ Features

### ⚡ What makes this system powerful?

🧠 **Advanced Machine Learning Pipeline**

- NLP-based text preprocessing (tokenization, stopword removal, normalization)
- **TF-IDF Vectorization** (Unigrams + Bigrams)
- Additional engineered features (message length, word count, sentence count)
- **SMOTE** for handling class imbalance
- Final model: **Support Vector Machine (SVM)** with high accuracy

---

### 🌐 Multi-Platform Architecture

🔗 **Flask REST API (Core Engine)**

- Centralized prediction system
- Secure and scalable cloud deployment

💻 **Web Application**

- User-friendly interface for manual SMS classification
- Authentication system (Login / Register / Reset Password)

📱 **Android Application**

- Manual + real-time SMS analysis
- **BroadcastReceiver** for automatic detection of incoming messages
- Seamless API communication using **Retrofit**

---

### 🎯 Final Outcome

✨ A **robust, scalable, and real-world ready SMS spam detection system** that combines:

> 🤖 Machine Learning + 🌐 Web Development + 📱 Mobile Computing + ☁️ Cloud Deployment

---

## 🛠️ Tech Stack

| Layer              | Technology        |
| ------------------ | ----------------- |
| Language           | Python, Kotlin    |
| ML Framework       | Scikit-learn      |
| NLP                | NLTK              |
| Feature Extraction | TF-IDF            |
| Backend            | Flask             |
| Frontend           | HTML, CSS, Jinja2 |
| Android            | Kotlin, Retrofit  |
| Database           | PostgreSQL        |
| Security           | bcrypt, JWT       |
| Deployment         | Render            |

---

## 📂 Project Structure

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
│   ├── forgot_password.html
│   ├── login.html
│   ├── register.html
│   ├── reset_password.html
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
├── OverSampler_sms_detection.ipynb
├── SMOTE_sms_detection.ipynb
├── spam.csv
├── spam_ham_india4.csv
├── LICENSE
└── README.md
```

---

## 🧪 Sample Test Messages

Use the following sample messages to test the system and verify classification performance.

---

### 🚨 Spam Test Messages

```text
Congratulations! You have won a $1000 Walmart gift card. Click here to claim now.

URGENT! Your mobile number has won 50000 cash prize. Call now.

Free entry in a weekly competition to win FA Cup tickets. Text WIN to 87121.

You have been selected for a guaranteed loan approval. Apply now.

Dear user, your account has been suspended. Click this link to verify your details immediately.

Congratulations! You are the lucky winner of our lottery draw. Send your details to claim.

Your email has won 355,000 GBP. Your email was selected by the BMW Promo of the year 2026. Kindly send your name, phone number, age, sex, address, country for claim.
```

---

### 🟢 Ham (Not Spam) Test Messages

```text
Hey, are we still meeting for lunch today?

Please send me the notes from yesterday's class.

I will call you when I reach home.

Don't forget to bring the documents tomorrow.
```

---

### 🎯 Expected Output

| Message Type | Prediction |
| ------------ | ---------- |
| Spam Samples | ❌ Spam     |
| Ham Samples  | ✅ Not Spam |


---

## ⚙️ How It Works

```
1. User types a message in the input box
2. Message is sent to the Flask backend via POST request
3. Backend runs NLP preprocessing (lowercase → tokenize → stem → clean)
4. TF-IDF vectorizer converts cleaned text into numerical features
5. Trained Naive Bayes model predicts: Spam or Ham
6. Confidence score is calculated from model probabilities
7. Result is rendered instantly on the webpage
```

---

## 👨‍💻 Authors

Developed as a **Final Year BCA Project at KIIT University**, this project represents a complete end-to-end implementation of a real-world problem — combining **Machine Learning, Backend Systems, and Mobile Application Development** to build a scalable SMS spam detection solution.

<table align="center">
  <tr>
    <td align="center">
      <img src="static/images/Member1.png" width="100" height="100" style="border-radius:50%; object-fit:cover;"/><br/><br/>
      <b>Priyanshu Sahoo</b><br/>
      <a href="https://in.linkedin.com/in/priyanshusahoo-ps98">
        <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin&logoColor=white"/>
      </a>
    </td>
    <td align="center">
      <img src="static/images/Member2.png" width="100" height="100" style="border-radius:50%; object-fit:cover;"/><br/><br/>
      <b>Vivek Pralhad Salunkhe</b><br/>
      <a href="https://in.linkedin.com/">
        <img src="https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat&logo=linkedin&logoColor=white"/>
      </a>
    </td>
  </tr>
</table>

---

## 📱 Android Version

> Interested in the **Android version** of this SMS Spam Filter app?

Reach out directly via LinkedIn — happy to share more details!

🔗 **[Connect with Priyanshu Sahoo on LinkedIn](https://in.linkedin.com/in/priyanshusahoo-ps98)**

---

## 📄 License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

---

<div align="center">

Made with ❤️ by **Priyanshu Sahoo** & **Vivek Pralhad Salunkhe**

⭐ If you found this project helpful, please consider giving it a star!

</div>

---

<div align="center"> <h1 style=font-weight: bold;>@VPsPs Team</h1> </div>
