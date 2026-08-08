import os
import shutil

import pytest

SAMPLE = "samples/STARS_SAMPLE.html"
FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "_fixtures_tmp")
NAMES = ["STARS_AAA.html", "STARS_BBB.html", "STARS_CCC.html"]


@pytest.fixture(scope="module")
def compare_fixtures():
    """Copy the sample timetable into a temp folder under the project root.

    read_html_file resolves inputs against the project root, so fixtures live there.
    """
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    paths = []
    try:
        for name in NAMES:
            dest = os.path.join(FIXTURE_DIR, name)
            shutil.copy(SAMPLE, dest)
            paths.append(os.path.join("tests", "_fixtures_tmp", name))
        yield paths
    finally:
        shutil.rmtree(FIXTURE_DIR, ignore_errors=True)
