from bs4 import BeautifulSoup

ATTENDANCE_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/StudentPercentage"

def fetch_attendance(session, subject_map):

    res = session.get(ATTENDANCE_URL)
    soup = BeautifulSoup(res.text, "lxml")  # faster parser

    table = soup.find("table")

    subjects = []
    total_present = 0
    total_hours = 0

    rows = table.find_all("tr")[1:]

    for r in rows:
        cols = r.find_all("td")

        if len(cols) < 6:
            continue

        course = cols[0].text.strip()
        total_hr = int(cols[1].text.strip())
        present = int(cols[4].text.strip())
        percent = cols[5].text.strip()

        total_present += present
        total_hours += total_hr

        subjects.append({
            "course": course,
            "name": subject_map.get(course, "Unknown"),
            "percent": percent
        })

    attendance = round((total_present / total_hours) * 100, 2)

    return attendance, subjects
