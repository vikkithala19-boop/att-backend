from flask import Flask,request,jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app=Flask(__name__)
CORS(app)

LOGIN_PAGE="https://ecampus.psgtech.ac.in/"
LOGIN_POST="https://ecampus.psgtech.ac.in/"
ATT_URL="https://ecampus.psgtech.ac.in/studzone/Attendance/StudentPercentage"

@app.route("/")
def home():
    return "Attendance API Running"

@app.route("/attendance",methods=["POST"])
def attendance():

    data=request.json
    student_id=data["id"]
    password=data["password"]

    session=requests.Session()

    # Step 1: get login page
    r=session.get(LOGIN_PAGE)

    soup=BeautifulSoup(r.text,"html.parser")

    token=soup.find("input",{"name":"__RequestVerificationToken"})["value"]

    # Step 2: login payload
    payload={
        "UserName":student_id,
        "Password":password,
        "__RequestVerificationToken":token
    }

    session.post(LOGIN_POST,data=payload)

    # Step 3: fetch attendance page
    page=session.get(ATT_URL)

    soup=BeautifulSoup(page.text,"html.parser")

    rows=soup.select("table tbody tr")

    subjects=[]

    for r in rows:

        cols=[c.text.strip() for c in r.find_all("td")]

        if len(cols)>5:

            subjects.append({
                "course":cols[0],
                "total":cols[1],
                "absent":cols[3],
                "present":cols[4],
                "percent":cols[5]
            })

    return jsonify(subjects)

if __name__=="__main__":
    app.run()
