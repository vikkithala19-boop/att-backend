from bs4 import BeautifulSoup

COURSEPLAN_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/courseplan"

def fetch_courses(session):

    res = session.get(COURSEPLAN_URL)

    soup = BeautifulSoup(res.text, "html.parser")

    subject_map = {}

    codes = soup.select(".coursecode")
    names = soup.select(".coursename")

    for c, n in zip(codes, names):

        code = c.text.strip()
        name = n.text.strip()

        subject_map[code] = name

    return subject_map
