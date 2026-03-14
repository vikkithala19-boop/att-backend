from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

LOGIN_URL = "https://ecampus.psgtech.ac.in/studzone"
ATT_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/StudentPercentage"

@app.route("/")
def home():
    return "Attendance API Running"


@app.route("/attendance", methods=["POST"])
def attendance():

    try:

        data = request.json
        student_id = data.get("id")
        password = data.get("password")

        session = requests.Session()

        # LOGIN REQUEST
        payload = {
            "Rollno": student_id,
            "Password": password
        }

        login = session.post(LOGIN_URL, data=payload)

        # GET ATTENDANCE PAGE
        page = session.get(ATT_URL)

        soup = BeautifulSoup(page.text, "html.parser")

        # FIND TABLE ROWS
        rows = soup.select("#StudentPercentageTable tbody tr")

        subjects = []

        for r in rows:

            cols = [c.text.strip() for c in r.find_all("td")]

            if len(cols) >= 6:

                subjects.append({
                    "course": cols[0],
                    "total": cols[1],
                    "absent": cols[3],
                    "present": cols[4],
                    "percent": cols[5]
                })

        return jsonify(subjects)

    except Exception as e:

        return jsonify({
            "error": str(e)
        })


if __name__ == "__main__":
    app.run()
