from bs4 import BeautifulSoup

ATTENDANCE_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/StudentPercentage"

def fetch_attendance(session, subject_map):

    res = session.get(ATTENDANCE_URL)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch attendance page (status {res.status_code})")

    soup = BeautifulSoup(res.text, "lxml")

    table = soup.find("table")
    if table is None:
        # Try to find an error/notice on the page to provide a better message
        possible_error = soup.find(class_="validation-summary-errors") or soup.find(class_="error") or soup.find("p")
        detail = possible_error.get_text(strip=True) if possible_error else None
        msg = "Attendance table not found. Possible causes: not logged in, page layout changed, or the site returned an unexpected response."
        if detail:
            msg += f" Page message: {detail}"
        raise Exception(msg)

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
        try:
            total_hr = int(cols[1].text.strip())
        except ValueError:
            total_hr = 0
        try:
            absent = int(cols[3].text.strip())
        except ValueError:
            absent = 0
        try:
            present = int(cols[4].text.strip())
        except ValueError:
            present = 0
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

    # guard against division by zero
    if total_hours == 0:
        attendance = 0.0
    else:
        attendance = round((total_present / total_hours) * 100, 2)

    return attendance, subjects, last_updated
