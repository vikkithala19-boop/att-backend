from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# enable CORS so Vercel frontend can call backend
CORS(app)

LOGIN_URL = "https://ecampus.psgtech.ac.in/studzone"
ATT_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/StudentPercentage"


@app.route("/")
def home():
    return "Attendance API Running"


@app.route("/attendance", methods=["POST"])
def attendance():

    data = request.json

    roll = data.get("id", "").upper()
    password = data.get("password", "")

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": LOGIN_URL
    }

    # Step 1 — open login page
    login_page = session.get(LOGIN_URL, headers=headers)

    soup = BeautifulSoup(login_page.text, "html.parser")

    token_input = soup.find("input", {"name": "__RequestVerificationToken"})

    if not token_input:
        return jsonify({"error": "Login token not found"})

    token = token_input["value"]

    # Step 2 — login
    payload = {
        "__RequestVerificationToken": token,
        "Rollno": roll,
        "Password": password
    }

    login_response = session.post(
        LOGIN_URL,
        data=payload,
        headers=headers,
        allow_redirects=True
    )

    # detect wrong password
    if "Student Login" in login_response.text:
        return jsonify({"error": "Invalid roll number or password"})

    # Step 3 — open attendance page
    page = session.get(ATT_URL, headers=headers)

    if "Student Login" in page.text:
        return jsonify({"error": "Login failed"})

    soup = BeautifulSoup(page.text, "html.parser")

    table = soup.find("table")

    if not table:
        return jsonify({"error": "Attendance table not found"})

    rows = table.find_all("tr")

    subjects = []
    percents = []

    for row in rows:

        cols = row.find_all("td")

        if len(cols) >= 6:

            course = cols[0].text.strip()
            percent = cols[5].text.strip()

            try:
                p = float(percent)
                percents.append(p)
            except:
                p = 0

            subjects.append({
                "course": course,
                "percent": percent
            })

    # calculate overall attendance
    if len(percents) > 0:
        avg = sum(percents) / len(percents)
    else:
        avg = 0

    # bunk calculation
    total_classes = 100
    attended = (avg / 100) * total_classes
    bunkable = int(attended / 0.75 - total_classes)

    if bunkable < 0:
        bunkable = 0

    return jsonify({
        "attendance": round(avg, 2),
        "bunkable": bunkable,
        "subjects": subjects
    })


if __name__ == "__main__":
    app.run()
