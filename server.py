from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import time

from fetch_courses import fetch_courses
from fetch_attendance import fetch_attendance

app = Flask(__name__)
CORS(app)

LOGIN_URL = "https://ecampus.psgtech.ac.in/studzone"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ⚡ cache variables
CACHE_DATA = None
CACHE_TIME = 0
CACHE_TTL = 60  # seconds


@app.route("/")
def home():
    return "PSG Attendance Backend Running"


@app.route("/attendance", methods=["POST"])
def attendance():

    global CACHE_DATA, CACHE_TIME

    data = request.json

    roll = data.get("id")
    password = data.get("password")

    if not roll or not password:
        return jsonify({"error": "Missing credentials"})

    # ⚡ return cached result if still valid
    if CACHE_DATA and time.time() - CACHE_TIME < CACHE_TTL:
        return jsonify(CACHE_DATA)

    try:

        session = requests.Session()

        # open login page
        r = session.get(LOGIN_URL, headers=HEADERS)

        soup = BeautifulSoup(r.text, "html.parser")

        token = soup.find("input", {"name": "__RequestVerificationToken"})

        if not token:
            return jsonify({"error": "Login token not found"})

        token = token["value"]

        payload = {
            "__RequestVerificationToken": token,
            "RollNo": roll,
            "Password": password
        }

        login = session.post(LOGIN_URL, data=payload, headers=HEADERS)

        if "Invalid" in login.text:
            return jsonify({"error": "Invalid credentials"})

        # fetch course names
        subject_map = fetch_courses(session)

        # fetch attendance data
        attendance, subjects, last_updated = fetch_attendance(session, subject_map)

        bunkable = 0

        if attendance >= 75:
            total = 100
            attended = (attendance / 100) * total
            bunkable = int((attended / 0.75) - total)

        result = {
            "attendance": attendance,
            "bunkable": bunkable,
            "updated": last_updated,
            "subjects": subjects
        }

        # ⚡ store in cache
        CACHE_DATA = result
        CACHE_TIME = time.time()

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
