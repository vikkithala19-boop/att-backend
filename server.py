from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

from fetch_courses import fetch_courses
from fetch_attendance import fetch_attendance

app = Flask(__name__)

LOGIN_URL = "https://ecampus.psgtech.ac.in/studzone"

@app.route("/")
def home():
    return "PSG Attendance API Running"

@app.route("/attendance", methods=["POST"])
def attendance():

    data = request.json

    roll = data.get("id")
    password = data.get("password")

    session = requests.Session()

    # open login page first
    r = session.get(LOGIN_URL)

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

    login = session.post(LOGIN_URL, data=payload)

    if "Invalid" in login.text:
        return jsonify({"error": "Invalid roll number or password"})

    # fetch subjects
    subject_map = fetch_courses(session)

    # fetch attendance
    attendance, subjects = fetch_attendance(session, subject_map)

    # calculate bunkable classes
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


if __name__ == "__main__":
    app.run(debug=True)
