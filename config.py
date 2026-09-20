from pathlib import Path
from datetime import date

BELL_TIMES = {
    1: ("8.00-9.30"),
    2: ("9.40-11.10"),
    3: ("11.20-12.50"),
    4: ("13.30-15.00"),
    5: ("15.10-16.40"),
    6: ("16.50-18.20"),
    7: ("18.30-20.00"),
    8: ("20.10-21.40"),
}

WEEK = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
MONTH = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря",
}

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "database.db"
BASE_URL = "http://db.biysk.secna.ru/schedule/schedule.test_r.timetable_teacher?name_group_dl=%B8%C1%C2-61&cury=2026&cursem=1&ned_dl=" #Хакдкод под ист-61

SEMESTR_START = date(2026, 8, 31)