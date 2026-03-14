from bs4 import BeautifulSoup

COURSEPLAN_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/courseplan"

def fetch_courses(session):

    res = session.get(COURSEPLAN_URL)

    soup = BeautifulSoup(res.text, "html.parser")

    subject_map = {}

    cards = soup.find_all("div", class_="card")

    for card in cards:

        text = card.get_text("\n").split("\n")

        clean = [t.strip() for t in text if t.strip() != ""]

        if len(clean) >= 2:

            code = clean[0]
            name = clean[1]

            subject_map[code] = name

    return subject_map
