from bs4 import BeautifulSoup

ATTENDANCE_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/StudentPercentage"

def fetch_attendance(session, subject_map):

    res = session.get(ATTENDANCE_URL)

    soup = BeautifulSoup(res.text, "lxml")

    table = soup.find("table")

    subjects = []
    total_present = 0
    total_hours = 0

    last_updated = None

    rows = table.find_all("tr")[1:]

    for r in rows:

        cols = r.find_all("td")

        if len(cols) < 10:
            continue

        course = cols[0].text.strip()
        total_hr = int(cols[1].text.strip())
        absent = int(cols[3].text.strip())
        present = int(cols[4].text.strip())
        percent = cols[5].text.strip()

        attendance_to = cols[9].text.strip()

        if not last_updated:
            last_updated = attendance_to

        total_present += present
        total_hours += total_hr

        subjects.append({
            "course": course,
            "name": subject_map.get(course, "Unknown"),
            "total": total_hr,
            "present": present,
            "absent": absent,
            "percent": percent
        })

    attendance = round((total_present / total_hours) * 100, 2)

    return attendance, subjects, last_updated
