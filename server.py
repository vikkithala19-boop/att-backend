from bs4 import BeautifulSoup
import re

ATTENDANCE_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/StudentPercentage"


def _save_debug_html(file_name, html):
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception:
        pass


def _clean_number(value):
    try:
        return int(float(str(value).replace(",", "").replace("%", "")))
    except Exception:
        return 0


def _get_cell_text(cell):
    return cell.get_text(" ", strip=True) if cell else ""


def fetch_attendance(session, subject_map):
    try:
        res = session.get(ATTENDANCE_URL, timeout=20)
        res.raise_for_status()
    except Exception as exc:
        raise Exception(f"Attendance page request failed: {exc}") from exc

    if res.status_code != 200:
        raise Exception(f"Attendance page returned {res.status_code}")

    soup = BeautifulSoup(res.text, "lxml")

    table = None
    for candidate in soup.select("table#example, table.example, table[id*='example'], table[class*='example']"):
        if candidate.find("tr"):
            table = candidate
            break

    if table is None:
        for candidate in soup.select("table"):
            rows = candidate.find_all("tr")
            if rows and any("attendance" in row.get_text(" ", strip=True).lower() for row in rows[:3]):
                table = candidate
                break

    if table is None:
        _save_debug_html("attendance_debug.html", res.text)
        raise Exception("Attendance table not found; page structure may have changed")

    subject_rows = []
    tbody = table.find("tbody")
    if tbody:
        subject_rows = tbody.find_all("tr")
    else:
        subject_rows = table.find_all("tr")

    subjects = []
    total_present = 0
    total_hours = 0
    last_updated = ""

    for row in subject_rows:
        cols = row.find_all(["td", "th"])
        if not cols:
            continue

        texts = [_get_cell_text(col) for col in cols]
        if len(texts) < 4:
            continue

        header_text = " ".join(texts).lower()
        if "course" in header_text or "subject" in header_text or "attendance" in header_text:
            continue

        course = ""
        total = 0
        absent = 0
        present = 0
        percent = "0"

        if len(cols) >= 10:
            course = _get_cell_text(cols[0])
            total = _clean_number(_get_cell_text(cols[1]))
            absent = _clean_number(_get_cell_text(cols[3]))
            present = _clean_number(_get_cell_text(cols[4]))
            percent = _get_cell_text(cols[5])
            last_updated = _get_cell_text(cols[9]) if not last_updated else last_updated
        else:
            course = _get_cell_text(cols[0])
            for idx, cell in enumerate(cols[1:], start=1):
                value = _get_cell_text(cell)
                if not value:
                    continue
                if re.search(r"\d", value):
                    if total == 0 and not any(ch.isalpha() for ch in value):
                        total = _clean_number(value)
                    elif present == 0 and any(word in value.lower() for word in ["present", "attended"]):
                        present = _clean_number(value)
                    elif absent == 0 and any(word in value.lower() for word in ["absent", "missed"]):
                        absent = _clean_number(value)
                    elif percent == "0" and "%" in value:
                        percent = value

            if not present:
                present = max(0, total - absent)

        if not course:
            continue

        if not last_updated:
            last_updated = _get_cell_text(row.find_all("td")[-1]) if row.find_all("td") else ""

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
