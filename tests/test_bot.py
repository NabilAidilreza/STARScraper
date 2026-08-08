"""Static tests for the Telegram bot module.

These tests never contact the Telegram API: bot methods (send_message,
send_document, download_file, get_file) are stubbed, the database session is
replaced with fakes, and PROJECT_ROOT is redirected to a tmp dir. The module is
importable in tests because secrets are resolved from env vars.
"""

import os
import shutil
from types import SimpleNamespace

import pytest

# Secrets are read at import time; dummy values keep the import offline.
# The token must contain a colon to pass telebot's format validation.
os.environ.setdefault("TELEGRAM_API_KEY", "123456:TEST-API-KEY")
os.environ.setdefault("TELEGRAM_BOT_PASSCODE", "abcde")

import zTelegramBot.mod_tracker_telegram_bot as bot_mod

SAMPLE = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "samples", "STARS_SAMPLE.html"))


def _msg(chat_id=1, text=None, document=None):
    return SimpleNamespace(
        chat=SimpleNamespace(id=chat_id),
        from_user=SimpleNamespace(first_name="Test", last_name="User"),
        text=text,
        document=document,
    )


def _doc(name):
    return SimpleNamespace(file_name=name, file_id="FILE_ID_123")


@pytest.fixture
def fake_bot(monkeypatch):
    """Stub all network-facing bot methods and record outbound messages."""
    calls = {"messages": [], "documents": []}

    def send_message(chat_id, text, **kwargs):
        calls["messages"].append((chat_id, text, kwargs))

    def send_document(chat_id, doc, **kwargs):
        calls["documents"].append((chat_id, doc, kwargs))

    def download_file(file_path):
        with open(SAMPLE, "rb") as f:
            return f.read()

    monkeypatch.setattr(bot_mod.bot, "send_message", send_message)
    monkeypatch.setattr(bot_mod.bot, "send_document", send_document)
    monkeypatch.setattr(bot_mod.bot, "download_file", download_file)
    monkeypatch.setattr(bot_mod.bot, "get_file", lambda file_id: SimpleNamespace(file_path="docs/sample.html"))
    return calls


class FakeUser:
    def __init__(self, start_date="15/01/2024", passcode=bot_mod.PASSCODE, mod_dict=None):
        self.start_date = start_date
        self.passcode = passcode
        self._mod_dict = mod_dict if mod_dict is not None else {}

    def get_start_date(self):
        return self.start_date

    def set_start_date(self, value):
        self.start_date = value

    def get_passcode(self):
        return self.passcode

    def set_passcode(self, value):
        self.passcode = value

    def get_mod_dict(self):
        return self._mod_dict

    def set_mod_dict(self, value):
        self._mod_dict = value

    def getusername(self):
        return "Test User"


class FakeQuery:
    def __init__(self, user):
        self._user = user

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._user


class FakeSession:
    def __init__(self, user):
        self._user = user
        self.added = None
        self.committed = False

    def query(self, model):
        return FakeQuery(self._user)

    def add(self, obj):
        self.added = obj

    def commit(self):
        self.committed = True

    def close(self):
        pass


@pytest.fixture
def fake_db(monkeypatch):
    """Replace get_session with an in-memory fake; return the fake session."""
    session = FakeSession(None)
    monkeypatch.setattr(bot_mod, "get_session", lambda: session)
    return session


@pytest.fixture
def tmp_project(monkeypatch, tmp_path):
    """Redirect PROJECT_ROOT writes to a tmp dir and chdir there."""
    monkeypatch.setattr(bot_mod, "PROJECT_ROOT", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _registered_commands():
    cmds = set()
    for handler in bot_mod.bot.message_handlers:
        for cmd in handler["filters"].get("commands", []):
            cmds.add(cmd)
    return cmds


# --------------------------------------------------------------------------
# Module import / secrets
# --------------------------------------------------------------------------

def test_module_imports_offline():
    # Importing the module must not start polling or require live credentials.
    assert bot_mod.API_KEY == "123456:TEST-API-KEY"
    assert bot_mod.PASSCODE == "abcde"
    assert callable(bot_mod.main)


def test_load_secrets_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_PASSCODE", "12345")
    assert bot_mod._load_secrets()[1] == "12345"


def test_read_secret_missing_file_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(bot_mod, "PROJECT_ROOT", str(tmp_path))
    monkeypatch.delenv("TELEGRAM_API_KEY", raising=False)
    with pytest.raises(FileNotFoundError):
        bot_mod._read_secret("TELEGRAM_API_KEY.txt")


# --------------------------------------------------------------------------
# Predicates (pure, no I/O)
# --------------------------------------------------------------------------

def test_check_passcode():
    assert bot_mod.check_passcode(_msg(text="abcde")) is True
    assert bot_mod.check_passcode(_msg(text="wrong")) is False


def test_checksubmissionofSTARTDATE_valid():
    assert bot_mod.checksubmissionofSTARTDATE(_msg(text="15/01/2024")) is True


@pytest.mark.parametrize("text", ["31/13/2024", "hello/world/2024", "15-01-2024", "15/01/24", ""])
def test_checksubmissionofSTARTDATE_invalid(text):
    assert bot_mod.checksubmissionofSTARTDATE(_msg(text=text)) is False


def test_checksubmissionofSTARTDATE_non_text_message():
    # Messages without a .text attribute must not crash the predicate.
    assert bot_mod.checksubmissionofSTARTDATE(SimpleNamespace()) is False


@pytest.mark.parametrize("name,expected", [
    ("STARS_NAB.html", True),
    ("stars_nab.html", False),  # case-sensitive, same as original behavior
    ("STARS_NAB.txt", False),
    ("photo.png", False),
])
def test_checksubmissionofSTARS(name, expected):
    assert bot_mod.checksubmissionofSTARS(_msg(document=_doc(name))) is expected


def test_checksubmissionofSTARS_non_document():
    assert bot_mod.checksubmissionofSTARS(_msg()) is False


def test_is_command():
    assert bot_mod.is_command(_msg(text="/checkmods")) is True
    assert bot_mod.is_command(_msg(text="hello")) is False
    assert bot_mod.is_command(_msg(text=None)) is False


# --------------------------------------------------------------------------
# Access gates
# --------------------------------------------------------------------------

def test_verify_passcode_data_locked(monkeypatch):
    user = FakeUser(passcode="", mod_dict={})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    # no passcode + no data -> blocked
    assert bot_mod.verify_passcode_data(_msg(text="hello")) is True
    # command / passcode / start date are never treated as data
    assert bot_mod.verify_passcode_data(_msg(text="/checkmods")) is False
    assert bot_mod.verify_passcode_data(_msg(text="abcde")) is False
    assert bot_mod.verify_passcode_data(_msg(text="15/01/2024")) is False


def test_verify_passcode_data_unlocked(monkeypatch):
    user = FakeUser(mod_dict={"file_name": "x"})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    assert bot_mod.verify_passcode_data(_msg(text="hello")) is False


def test_verify_empty_data_set(monkeypatch):
    ready = FakeUser(mod_dict={"file_name": "x"})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: ready)
    assert bot_mod.verify_empty_data_set(_msg(text="hello")) is False

    empty = FakeUser(mod_dict={})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: empty)
    assert bot_mod.verify_empty_data_set(_msg(text="hello")) is True
    # commands / passcode / start dates never count as "empty data set" prompts
    assert bot_mod.verify_empty_data_set(_msg(text="/checkmods")) is False


def test_verify_missing_start_date(monkeypatch):
    monkeypatch.setattr(bot_mod, "get_user", lambda message: None)
    assert bot_mod.verify_missing_start_date(_msg()) is True
    monkeypatch.setattr(bot_mod, "get_user", lambda message: FakeUser(start_date=""))
    assert bot_mod.verify_missing_start_date(_msg()) is True
    monkeypatch.setattr(bot_mod, "get_user", lambda message: FakeUser(start_date="15/01/2024"))
    assert bot_mod.verify_missing_start_date(_msg()) is False


def test_require_data_no_user(fake_bot, monkeypatch):
    monkeypatch.setattr(bot_mod, "get_user", lambda message: None)
    assert bot_mod.require_data(_msg()) is None
    assert fake_bot["messages"][0][1] == "Please send /start first."


def test_require_data_no_data(fake_bot, monkeypatch):
    monkeypatch.setattr(bot_mod, "get_user", lambda message: FakeUser(mod_dict={}))
    assert bot_mod.require_data(_msg()) is None
    assert fake_bot["messages"][0][1] == "Error. STARS not initialized yet!!!"


def test_require_data_ready(fake_bot, monkeypatch):
    user = FakeUser(mod_dict={"file_name": "STARS_TEST_1.html"})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    assert bot_mod.require_data(_msg()) is user


# --------------------------------------------------------------------------
# Initialization handlers
# --------------------------------------------------------------------------

def test_start_new_user(fake_bot, fake_db):
    fake_db._user = None
    bot_mod.start(_msg(chat_id=99))
    assert fake_db.added is not None
    assert fake_db.committed
    texts = [t for _, t, _ in fake_bot["messages"]]
    assert any("Welcome: Test User" in t for t in texts)


def test_start_returning_user(fake_bot, fake_db):
    fake_db._user = FakeUser(mod_dict={"file_name": "STARS_TEST_1.html"})
    bot_mod.start(_msg(chat_id=99))
    texts = [t for _, t, _ in fake_bot["messages"]]
    assert any("Welcome back" in t for t in texts)
    assert any("Last file registered" in t for t in texts)
    # returning users with data also get the command menu
    assert any("checkmods" in t for t in texts)


def test_lock_passcode_sets_user(fake_bot, fake_db):
    user = FakeUser(passcode="")
    fake_db._user = user
    bot_mod.lock_passcode(_msg(text="abcde"))
    assert user.get_passcode() == "abcde"
    assert any("unlocked" in t for _, t, _ in fake_bot["messages"])


def test_extractstartdate_sets_user(fake_bot, fake_db):
    user = FakeUser(start_date="")
    fake_db._user = user
    bot_mod.extractstartdate(_msg(text="15/01/2024"))
    assert user.get_start_date() == "15/01/2024"


def test_filteroutstars_processing(fake_bot, fake_db, tmp_project):
    user = FakeUser(start_date="15/01/2024")
    fake_db._user = user
    bot_mod.filteroutStars(_msg(chat_id=7, document=_doc("STARS_NAB.html")))
    mod_dict = user.get_mod_dict()
    assert mod_dict["file_name"] == "STARS_NAB_7.html"
    assert mod_dict["mods"]  # compiled modules present
    assert len(mod_dict["timeline"]) == 13
    # downloaded file persisted under PROJECT_ROOT/submitted_htmls
    saved = os.path.join(tmp_project, "submitted_htmls", "STARS_NAB_7.html")
    assert os.path.exists(saved)
    texts = [t for _, t, _ in fake_bot["messages"]]
    assert any("Data verified" in t for t in texts)


def test_filteroutstars_missing_start_date(fake_bot, fake_db):
    fake_db._user = FakeUser(start_date="")
    bot_mod.filteroutStars(_msg(document=_doc("STARS_NAB.html")))
    texts = [t for _, t, _ in fake_bot["messages"]]
    assert any("Start date empty" in t for t in texts)


def test_filteroutstars_bad_html(fake_bot, fake_db, tmp_project, monkeypatch):
    fake_db._user = FakeUser(start_date="15/01/2024")
    monkeypatch.setattr(bot_mod.bot, "download_file", lambda path: b"<html><body>garbage</body></html>")
    bot_mod.filteroutStars(_msg(chat_id=7, document=_doc("STARS_BAD.html")))
    # invalid HTML must be reported to the user, not crash the handler
    texts = [t for _, t, _ in fake_bot["messages"]]
    assert any("Failed to process" in t for t in texts)


# --------------------------------------------------------------------------
# Command handlers
# --------------------------------------------------------------------------

def test_check_mods(fake_bot, monkeypatch):
    user = FakeUser(mod_dict={"mods": {
        "MH1000": {"Course_Info": {"Name": "Math", "AU": "3", "Status": "Registered",
                                   "Type": "LEC", "Index": "10000", "Grp": "1",
                                   "Venue": "LT20", "Finals": "Not Applicable"},
                   "Timeline": {}},
    }})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    bot_mod.check_mods(_msg())
    texts = [t for _, t, _ in fake_bot["messages"]]
    assert any("MH1000" in t for t in texts)


def test_check_today(fake_bot, monkeypatch):
    user = FakeUser(mod_dict={"mods": {"MH1000": {"Timeline": {
        "Wk1": {"Mon": {"0830to0920": ["LEC", "LT20", "15/01/2024"]}}}}}})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    bot_mod.check_today(_msg())
    assert fake_bot["messages"]  # handler ran without raising


def test_check_forecast_invalid_week(fake_bot, monkeypatch):
    monkeypatch.setattr(bot_mod, "get_user", lambda message: FakeUser(mod_dict={"mods": {}}))
    bot_mod.check_forecast(_msg(text="/checkweekx"))
    texts = [t for _, t, _ in fake_bot["messages"]]
    assert any("Invalid week number" in t for t in texts)


def test_check_weekly_no_events(fake_bot, monkeypatch):
    user = FakeUser(mod_dict={"mods": {}, "timeline": [["15/01/2024"]]})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    bot_mod.check_weekly(_msg())
    texts = [t for _, t, _ in fake_bot["messages"]]
    assert any("No events this week" in t for t in texts)


def test_gen_ics_file_sends_document(fake_bot, monkeypatch, tmp_project):
    submitted = tmp_project / "submitted_htmls"
    submitted.mkdir()
    shutil.copy(SAMPLE, submitted / "STARS_TEST.html")
    user = FakeUser(mod_dict={"file_name": "STARS_TEST.html"})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    bot_mod.gen_ics_file(_msg())
    assert fake_bot["documents"], "expected a calendar document to be sent"
    assert (tmp_project / "calendars" / "TEST_calendar.ics").exists()


def test_gen_exam_ics_file_sends_document(fake_bot, monkeypatch, tmp_project):
    submitted = tmp_project / "submitted_htmls"
    submitted.mkdir()
    shutil.copy(SAMPLE, submitted / "STARS_TEST.html")
    user = FakeUser(mod_dict={"file_name": "STARS_TEST.html"})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    bot_mod.gen_exam_ics_file(_msg())
    assert fake_bot["documents"], "expected an exam calendar document to be sent"
    assert (tmp_project / "calendars" / "TEST_exams.ics").exists()


def test_gen_ics_file_failure_message(fake_bot, monkeypatch, tmp_project):
    (tmp_project / "submitted_htmls").mkdir()
    # missing file -> generator returns None after reporting an error
    user = FakeUser(mod_dict={"file_name": "STARS_MISSING_1.html"})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    bot_mod.gen_ics_file(_msg())
    texts = [t for _, t, _ in fake_bot["messages"]]
    assert any("Failed to generate" in t for t in texts)


def test_compare_schedules_not_enough_data(fake_bot, monkeypatch, tmp_project):
    (tmp_project / "submitted_htmls").mkdir()
    user = FakeUser(mod_dict={"file_name": "x"})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    bot_mod.compare_schedules(_msg(text="/compareschedules_wk2"))
    texts = [t for _, t, _ in fake_bot["messages"]]
    assert any("Not enough data" in t for t in texts)


def test_compare_schedules_sends_document(fake_bot, monkeypatch, tmp_project):
    submitted = tmp_project / "submitted_htmls"
    submitted.mkdir()
    for name in ("STARS_AAA.html", "STARS_BBB.html", "STARS_CCC.html"):
        shutil.copy(SAMPLE, submitted / name)
    user = FakeUser(mod_dict={"file_name": "x"})
    monkeypatch.setattr(bot_mod, "get_user", lambda message: user)
    bot_mod.compare_schedules(_msg(text="/compareschedules_wk2"))
    assert fake_bot["documents"], "expected a comparison table document"
    assert (tmp_project / "comparison_tables" / "WEEK_2_TABLE.html").exists()


def test_commands_registered():
    cmds = _registered_commands()
    # checkweek and compareschedules must cover the full 1-13 range
    for week in range(1, 14):
        assert f"checkweek{week}" in cmds
        assert f"compareschedules_wk{week}" in cmds
    assert "genicsfile" in cmds
    assert "genexamicsfile" in cmds
