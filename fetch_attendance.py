from bs4 import BeautifulSoup

ATTENDANCE_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/StudentPercentage"

def fetch_attendance(session, subject_map):

    res = session.get(ATTENDANCE_URL)

    if res.status_code != 200:
        raise Exception(f"Attendance page returned {res.status_code}")

    soup = BeautifulSoup(res.text, "lxml")

    table = soup.find("table", id="example")

    if table is None:
        with open("attendance_debug.html", "w", encoding="utf-8") as f:
            f.write(res.text)

        raise Exception("Attendance table (#example) not found")

    subjects = []
    total_present = 0
    total_hours = 0
    last_updated = ""

    rows = table.find("tbody").find_all("tr")

    for row in rows:

        cols = row.find_all("td")

        if len(cols) < 10:
            continue

        course = cols[0].get_text(strip=True)

        try:
            total = int(cols[1].get_text(strip=True))
        except:
            total = 0

        try:
            absent = int(cols[3].get_text(strip=True))
        except:
            absent = 0

        try:
            present = int(cols[4].get_text(strip=True))
        except:
            present = 0

        percent = cols[5].get_text(strip=True)

        attendance_to = cols[9].get_text(strip=True)

        if not last_updated:
            last_updated = attendance_to

        total_present += present
        total_hours += total

        subjects.append({
            "course": course,
            "name": subject_map.get(course, "Unknown"),
            "total": total,
            "present": present,
            "absent": absent,
            "percent": percent
        })

    attendance = round((total_present / total_hours) * 100, 2) if total_hours else 0

    return attendance, subjects, last_updated
