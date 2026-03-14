from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Attendance API Running"

@app.route("/attendance", methods=["POST"])
def attendance():

    data = request.json
    student_id = data["id"]
    password = data["password"]

    # Example response (replace later with scraping)
    attended = 42
    total = 50

    return jsonify({
        "attended": attended,
        "total": total
    })

if __name__ == "__main__":
    app.run()
