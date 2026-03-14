from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

from fetch_courses import fetch_courses
from fetch_attendance import fetch_attendance

app = Flask(__name__)
CORS(app)

LOGIN_URL = "https://ecampus.psgtech.ac.in/studzone"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded"
}


@app.route("/")
def home():
    return "PSG Attendance Backend Running"


@app.route("/attendance", methods=["POST"])
def attendance():

    data = request.json

    roll = data.get("id")
    password = data.get("password")

    if not roll or not password:
        return jsonify({"error": "Missing credentials"})

    try:

        session = requests.Session()

        # Step 1 — open login page
        r = session.get(LOGIN_URL, headers=HEADERS, timeout=15)

        soup = BeautifulSoup(r.text, "html.parser")

        token = soup.find("input", {"name": "__RequestVerificationToken"})

        if not token:
            return jsonify({"error": "Login token not found"})

        token = token["value"]

        # Step 2 — login
        payload = {
            "__RequestVerificationToken": token,
            "RollNo": roll,
            "Password": password
        }

        login = session.post(LOGIN_URL, data=payload, headers=HEADERS, timeout=15)

        if "Invalid" in login.text:
            return jsonify({"error": "Invalid credentials"})

        # Step 3 — fetch course names
        subject_map = fetch_courses(session)

        # Step 4 — fetch attendance
        attendance, subjects = fetch_attendance(session, subject_map)

        bunkable = 0

        if attendance >= 75:
            total = 100
            attended = (attendance / 100) * total
            bunkable = int((attended / 0.75) - total)

        return jsonify({
            "attendance": attendance,
            "bunkable": bunkable,
            "subjects": subjects
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
