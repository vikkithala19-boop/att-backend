from bs4 import BeautifulSoup

COURSEPLAN_URL = "https://ecampus.psgtech.ac.in/studzone/Attendance/courseplan"

# cache
_cached_subjects = None

def fetch_courses(session):
    global _cached_subjects

    # if already fetched, reuse
    if _cached_subjects is not None:
        return _cached_subjects

    res = session.get(COURSEPLAN_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    subject_map = {}

    codes = soup.select(".coursecode")
    names = soup.select(".coursename")

    for c, n in zip(codes, names):
        code = c.text.strip()
        name = n.text.strip()
        subject_map[code] = name

    _cached_subjects = subject_map
    return subject_map
