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

# ⚡ session reuse
SESSION = None
SESSION_TIME = 0
SESSION_TTL = 300  # 5 minutes

# ⚡ data cache
CACHE_DATA = None
CACHE_TIME = 0
CACHE_TTL = 60


@app.route("/")
def home():
    return "PSG Attendance Backend Running"


def login_psg(roll, password):

    session = requests.Session()

    r = session.get(LOGIN_URL, headers=HEADERS)

    soup = BeautifulSoup(r.text, "html.parser")

    token = soup.find("input", {"name": "__RequestVerificationToken"})

    if not token:
        raise Exception("Login token not found")

    token = token["value"]

    payload = {
        "__RequestVerificationToken": token,
        "RollNo": roll,
        "Password": password
    }

    login = session.post(LOGIN_URL, data=payload, headers=HEADERS)

    if "Invalid" in login.text:
        raise Exception("Invalid credentials")

    return session


@app.route("/attendance", methods=["POST"])
def attendance():

    global SESSION, SESSION_TIME
    global CACHE_DATA, CACHE_TIME

    data = request.json

    roll = data.get("id")
    password = data.get("password")

    if not roll or not password:
        return jsonify({"error": "Missing credentials"})

    # ⚡ return cached data instantly
    if CACHE_DATA and time.time() - CACHE_TIME < CACHE_TTL:
        return jsonify(CACHE_DATA)

    try:

        # ⚡ reuse PSG session
        if SESSION is None or time.time() - SESSION_TIME > SESSION_TTL:
            SESSION = login_psg(roll, password)
            SESSION_TIME = time.time()

        subject_map = fetch_courses(SESSION)

        attendance, subjects, last_updated = fetch_attendance(SESSION, subject_map)

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

        # ⚡ store cache
        CACHE_DATA = result
        CACHE_TIME = time.time()

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
