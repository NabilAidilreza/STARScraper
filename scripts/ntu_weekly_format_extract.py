"""Extract structured course data from the NTU STARS *weekly* timetable format.

This is a different HTML export from the usual planner (STARS_*.html): instead of
one row per registered course, the weekly view renders a grid table with time
slots (0800-0830 ... 2300-2330) as rows and MON-SAT as columns. Each non-empty
cell holds one or more `;`-separated entries like::

    IE2107 LEC/STU EELE LKC-LT 0930to1050- Wk1,2,4-13; IE2107 LEC/STU EELE ONLINE 0930to1050- Wk3

The file also contains a course list table (Index / Course / Title / AUs /
Status / @Exam Schedule) that carries the exam schedule.

INTEGRATED: `scripts.ntu_extract_timetable.create_timetable_list` auto-detects
this format and routes here, so all existing main functions (ICS generation,
compare, exam schedules, the bot) accept both formats. `create_weekly_timetable_list`
reshapes the grid into the standard per-week group structure used downstream.
"""

import os
import re

from bs4 import BeautifulSoup

# Standard row layout from scripts/ntu_extract_timetable (for the bridge) #
COURSE_CODE = 0
COURSE_TITLE = 1
AU = 2
COURSE_TYPE = 3
SU_OPTION = 4
GER_TYPE = 5
INDEX_NUMBER = 6
STATUS = 7
CHOICE = 8
CLASS_TYPE = 9
GROUP = 10
DAY = 11
TIME = 12
VENUE = 13
REMARK = 14
EXAM = 15
NUM_COLUMNS = 16

DAYS = ["MON", "TUE", "WED", "THU", "FRI", "SAT"]
MAX_TEACHING_WEEKS = 13

# Grid headers are uppercase; downstream code uses "Mon".."Sat" title case #
DAY_MAP = {"MON": "Mon", "TUE": "Tue", "WED": "Wed", "THU": "Thu", "FRI": "Fri", "SAT": "Sat"}
STANDARD_DAYS = list(DAY_MAP.values())

# Header row stored at index 0 of the standard-shaped output (never consumed downstream) #
STANDARD_HEADER_ROW = ["Course", "Title", "AUs", "Course Type", "S/U", "GER", "Index", "Status", "Choice", "Class Type", "Group", "Day", "Time", "Venue", "Remark", "Exam"]

_ENTRY_RE = re.compile(r"^(\S+)\s+(\S+)\s+(.*?)\s+(\d{4})to(\d{4})(.*)$")
_WEEKS_RE = re.compile(r"^-\s*Wk([0-9,\-]+)$")
_SLOT_RE = re.compile(r"(\d{4})\s*to\s*(\d{4})")

# FILE THAT MANAGES THE WEEKLY-FORMAT EXTRACTOR #

### File Reading ###

def resolve_file_path(file_name):
    """Resolve a weekly HTML file against the cwd, project root, or this folder."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    candidates = [file_name, os.path.join(project_root, file_name), os.path.join(script_dir, file_name)]
    for path in candidates:
        if os.path.isfile(path):
            return path
    raise FileNotFoundError(f"Weekly HTML file not found: {file_name}")


def read_weekly_html(file_name):
    """Read and parse a weekly-format HTML file into a BeautifulSoup object."""
    file_path = resolve_file_path(file_name)
    with open(file_path, "rb") as f:
        raw = f.read()
    for encoding in ("utf-8", "windows-1252"):
        try:
            return BeautifulSoup(raw.decode(encoding), "html.parser")
        except UnicodeDecodeError:
            continue
    return BeautifulSoup(raw.decode("utf-8", errors="replace"), "html.parser")


### Table Locators ###

def find_grid_table(soup):
    """Locate the weekly grid table (TIME\\DAY header + time-slot rows)."""
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        header = rows[0].find_all("td", recursive=False) if rows else []
        header_texts = [td.get_text(" ", strip=True) for td in header]
        if not header_texts or "TIME" not in header_texts[0].upper():
            continue
        slot_rows = 0
        for tr in rows[1:]:
            cells = tr.find_all("td", recursive=False)
            if cells and _SLOT_RE.search(cells[0].get_text(" ", strip=True)):
                slot_rows += 1
        if slot_rows >= 10:  # a real grid has 31 half-hour slots
            return table
    raise ValueError("Could not locate the weekly grid table in the HTML.")


def find_course_list_table(soup):
    """Locate the course list table (Index / Course / Title / AUs / Status / @Exam Schedule)."""
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = [td.get_text(" ", strip=True) for td in tr.find_all("td", recursive=False)]
            if len(cells) >= 6 and cells[0] == "Index" and "@Exam" in cells[-1]:
                return table
    raise ValueError("Could not locate the course list table in the HTML.")


### Grid Entry Parsing ###

def expand_weeks(spec):
    """Expand a week spec like '1,2,4-13' into a sorted list of week numbers."""
    if not spec:
        return list(range(1, MAX_TEACHING_WEEKS + 1))
    weeks = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            try:
                start, end = part.split("-")
                weeks.extend(range(int(start), int(end) + 1))
            except ValueError:
                continue
        else:
            try:
                weeks.append(int(part))
            except ValueError:
                continue
    return sorted(set(weeks))


def parse_entry(entry, day, slot):
    """Parse one `;`-separated grid entry into a structured dict.

    Entry shape: ``{code} {class_type} {venue...} {start}to{end}[- Wk<spec>]``
    Returns None if the entry cannot be parsed.
    """
    text = entry.replace("\xa0", " ").strip()
    if not text:
        return None
    match = _ENTRY_RE.match(text)
    if not match:
        return None
    course, class_type, venue, start, end, rest = match.groups()
    rest = rest.strip()
    weeks_spec = ""
    if rest:
        week_match = _WEEKS_RE.match(rest)
        if week_match:
            weeks_spec = week_match.group(1)
        elif rest != "-":
            return None  # unexpected trailing text; skip this entry
    slot_match = _SLOT_RE.search(slot)
    return {
        "course": course,
        "class_type": class_type,
        "venue": venue.strip(),
        "day": day,
        "time": f"{start}to{end}",
        "slot": slot,
        "slot_start": slot_match.group(1) if slot_match else start,
        "slot_end": slot_match.group(2) if slot_match else end,
        "weeks_spec": weeks_spec or "1-13",
        "weeks": expand_weeks(weeks_spec),
    }


def extract_grid_entries(soup):
    """Walk the weekly grid (rowspan-aware) and return one dict per course entry.

    The grid uses rowspan cells for classes spanning several half-hour slots, so a
    column tracker is required to map cells back to their day. Duplicate entries
    (the same class rendered again in a later rowspan block) are dropped.
    """
    grid = find_grid_table(soup)
    rows = grid.find_all("tr")

    # Header row -> day names #
    header_cells = rows[0].find_all("td", recursive=False)
    header_texts = [td.get_text(" ", strip=True) for td in header_cells]
    day_names = header_texts[1 : 1 + len(DAYS)]

    entries = []
    seen = set()
    pending = [0] * (len(DAYS) + 1)  # +1 reserves index 0 for the time column

    for tr in rows[1:]:
        cells = tr.find_all("td", recursive=False)
        cell_iter = iter(cells)
        row_entries = []
        try:
            time_cell = next(cell_iter)
        except StopIteration:
            continue
        slot = time_cell.get_text(" ", strip=True)
        for col in range(len(DAYS)):
            if pending[col + 1] > 0:
                pending[col + 1] -= 1
                continue
            try:
                cell = next(cell_iter)
            except StopIteration:
                break
            day = day_names[col] if col < len(day_names) else DAYS[col]
            day = DAY_MAP.get(day.strip().upper(), day)
            rowspan = cell.get("rowspan")
            if rowspan and rowspan.isdigit():
                pending[col + 1] = int(rowspan) - 1
            for part in cell.get_text(" ", strip=True).split(";"):
                parsed = parse_entry(part, day, slot)
                if parsed is None:
                    continue
                key = (day, parsed["course"], parsed["class_type"], parsed["venue"], parsed["time"], parsed["weeks_spec"])
                if key in seen:
                    continue
                seen.add(key)
                row_entries.append(parsed)
        entries.extend(row_entries)
    return entries


### Course List Parsing ###

def extract_course_list(soup):
    """Parse the course list table into {course_code: info_dict}, keyed by course."""
    table = find_course_list_table(soup)
    courses = {}
    semester = ""
    started = False
    for tr in table.find_all("tr"):
        cells = [td.get_text(" ", strip=True) for td in tr.find_all("td", recursive=False)]
        if not cells:
            continue
        # Semester banner row (e.g. "Academic Year 2026,Semester 1")
        if cells[0].startswith("Academic Year"):
            semester = cells[0]
            continue
        # Header row
        if cells[0] == "Index":
            started = True
            continue
        if not started:
            continue
        if cells[0] == "Total":
            break
        if len(cells) < 6:
            continue
        index, course, title, aus, status, exam = cells[:6]
        courses[course] = {
            "index": index,
            "title": title,
            "aus": aus,
            "status": status,
            "exam": exam,
        }
    return semester, courses


### Public API ###

def parse_weekly_file(file_name):
    """Parse a weekly-format HTML file into grid entries + course list."""
    soup = read_weekly_html(file_name)
    entries = extract_grid_entries(soup)
    semester, courses = extract_course_list(soup)
    return {"semester": semester, "entries": entries, "courses": courses}


### Bridge To Standard Format ###

def to_standard_rows(parsed):
    """Reshape weekly data into the standard 16-column row format.

    One row per grid entry, with fields filled from the course list table where
    available. The REMARK column carries the week spec (e.g. 'Teaching Wk1,2,4-13')
    so rows can be expanded per teaching week via `create_weekly_timetable_list`.
    Days are normalised to the standard 'Mon'..'Sat' title case.
    """
    rows = []
    for entry in parsed["entries"]:
        course = entry["course"]
        info = parsed["courses"].get(course, {})
        rows.append([
            course,                                   # COURSE_CODE
            info.get("title", ""),                    # COURSE_TITLE
            info.get("aus", ""),                      # AU
            "",                                       # COURSE_TYPE
            "",                                       # SU_OPTION
            "",                                       # GER_TYPE
            info.get("index", ""),                    # INDEX_NUMBER
            info.get("status", "Registered"),         # STATUS
            "",                                       # CHOICE
            entry["class_type"],                      # CLASS_TYPE
            "",                                       # GROUP
            entry["day"],                             # DAY
            entry["time"],                            # TIME
            entry["venue"],                           # VENUE
            "Teaching Wk" + entry["weeks_spec"],      # REMARK
            info.get("exam", ""),                     # EXAM
        ])
    return rows


def create_weekly_timetable_list(FILE_NAME):
    """Return weekly data in the same shape as `create_timetable_list`.

    [header_group, week_1_group, ..., week_13_group]
    where every week group holds 16-column rows with REMARK 'Teaching Wk<n>' and
    each grid entry is expanded into one row per teaching week it runs. All 13
    week groups are always present so week indices map 1:1 to teaching weeks.
    """
    parsed = parse_weekly_file(FILE_NAME)
    rows = to_standard_rows(parsed)
    groups = [[] for _ in range(MAX_TEACHING_WEEKS + 1)]
    for row in rows:
        spec = row[REMARK].replace("Teaching Wk", "")
        for week in expand_weeks(spec):
            expanded = list(row)
            expanded[REMARK] = f"Teaching Wk{week}"
            groups[week].append(expanded)
    return [STANDARD_HEADER_ROW] + groups[1:]


### CLI Demo ###

def main(file_name="WEEKLY_NAB.html"):
    parsed = parse_weekly_file(file_name)
    print("Semester:", parsed["semester"])
    print(f"\nGrid entries ({len(parsed['entries'])}):")
    for e in sorted(parsed["entries"], key=lambda x: (x["day"], x["slot"])):
        print(f"  {e['day']} {e['slot']}: {e['course']} {e['class_type']} "
              f"{e['venue']} {e['time']} Wk{e['weeks_spec']}")
    print(f"\nCourses ({len(parsed['courses'])}):")
    for code, info in parsed["courses"].items():
        print(f"  {code}: {info['title']} | {info['aus']} AUs | {info['status']} | {info['exam']}")
    print(f"\nStandard rows ({len(to_standard_rows(parsed))}):")
    for row in to_standard_rows(parsed)[:3]:
        print("  ", row)


if __name__ == "__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else "WEEKLY_NAB.html")
