from bs4 import BeautifulSoup
import re

COURSEPLAN_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/courseplan"

# cache
_cached_subjects = None


def _save_debug_html(file_name, html):
    try:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception:
        pass


def _extract_subject_map(soup):
    subject_map = {}

    for table in soup.select("table"):
        for row in table.find_all("tr"):
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            if len(cells) < 2:
                continue

            code = ""
            name = ""

            for cell in cells:
                if not cell:
                    continue
                if re.fullmatch(r"[A-Za-z0-9/.-]+", cell) and len(cell) <= 12:
                    if not code:
                        code = cell
                elif any(ch.isalpha() for ch in cell):
                    if not name:
                        name = cell

            if code and name and code not in subject_map:
                subject_map[code] = name

    if subject_map:
        return subject_map

    for row in soup.select("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
        if len(cells) < 2:
            continue

        text = " | ".join(cells)
        if "Course" in text and "Name" in text:
            continue

        candidate = [cell for cell in cells if cell and not re.fullmatch(r"[\d%\s.-]+", cell)]
        if len(candidate) >= 2:
            code = candidate[0]
            name = candidate[1]
            if code and name:
                subject_map[code] = name

    return subject_map


def fetch_courses(session):
    global _cached_subjects

    if _cached_subjects is not None:
        return _cached_subjects

    try:
        res = session.get(COURSEPLAN_URL, timeout=20)
        res.raise_for_status()
    except Exception as exc:
        raise Exception(f"Course plan request failed: {exc}") from exc

    soup = BeautifulSoup(res.text, "html.parser")
    subject_map = {}

    codes = soup.select(".coursecode, [class*='coursecode'], td.coursecode, span.coursecode")
    names = soup.select(".coursename, [class*='coursename'], td.coursename, span.coursename")

    if codes or names:
        for c, n in zip(codes, names):
            code = c.get_text(" ", strip=True)
            name = n.get_text(" ", strip=True)
            if code and name:
                subject_map[code] = name

    if not subject_map:
        subject_map = _extract_subject_map(soup)

    if not subject_map:
        _save_debug_html("courseplan_debug.html", res.text)
        raise Exception("Course plan page structure changed or no subject codes were found")

    _cached_subjects = subject_map
    return subject_map
