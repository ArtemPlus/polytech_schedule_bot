import sqlite3
from datetime import date, timedelta
from config import WEEK, DB_PATH


def create_db(db_name=DB_PATH):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS lessons (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name  TEXT NOT NULL,
    number      INTEGER NOT NULL,
    date        TEXT NOT NULL,
    type        TEXT,
    subject     TEXT,
    subgroup    INTEGER,
    teacher     TEXT,
    cabinet     TEXT
    );''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    user_id    TEXT NOT NULL,
    group_name TEXT,
    first_seen TEXT NOT NULL,
    last_seen  TEXT NOT NULL,
    PRIMARY KEY (user_id)
    );
                   ''')
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_lessons_group_date
    ON lessons(group_name, date);
                   ''')
    connection.commit()
    connection.close()

def prepare_data(schedule, group_info):
    common_lst = []
    dates = set()
    for day in schedule:
        for pair in schedule[day]:
            dates.add(pair["date"])
            common_lst.append(pair)
    rows = [(group_info, p["number"], p["date"], p["type"],
     p["subject"], p["subgroup"], p["teacher"], p["cabinet"]) for p in common_lst]
    return rows, dates

def save_lesson(schedule, group_info, db_name=DB_PATH):
    connection = sqlite3.connect(db_name)
    try:
        rows, dates = prepare_data(schedule, group_info)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        placeholders = ",".join("?" * len(dates))
        cursor.execute(f"DELETE FROM lessons WHERE group_name = ? AND date IN ({placeholders})", [group_info, *dates])
        cursor.executemany('''
                        INSERT INTO lessons 
                        (group_name, number, date, type, subject, subgroup, teacher, cabinet) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', rows)
        connection.commit()
    finally:
        connection.close()

def get_lesson(iso_date, group_name, db_name=DB_PATH):
    connection = sqlite3.connect(db_name)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    today = date.fromisoformat(iso_date)
    monday = today - timedelta(days=today.weekday())
    saturday = monday + timedelta(days=5)
    response = cursor.execute('''
                SELECT number, date, type, subject, subgroup, teacher, cabinet
                FROM lessons
                WHERE date BETWEEN ? AND ?
                AND group_name = ?
                ORDER BY date, number, subgroup
                              ''', [monday.isoformat(), saturday.isoformat(), group_name])
    response_dict = [dict(i) for i in response.fetchall()]
    schedule = {day: [] for day in WEEK}
    day_pair = monday
    for day_week in schedule:
        for pair in response_dict:
            if day_pair.isoformat() == pair["date"]:
                schedule[day_week].append(pair)
        day_pair = day_pair + timedelta(days=1)
    return schedule

def get_group_by_id(user_id: str, db_name=DB_PATH) -> str:
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute('''
                        SELECT group_name
                        FROM users
                        WHERE user_id=?
                           ''', [str(user_id)]).fetchone()
        if row is None:
            return None
        group = row["group_name"]
    finally:
        conn.close()
    return group

def set_group_by_id(user_id: str, group_name: str, db_name=DB_PATH):
    conn = sqlite3.connect(db_name)
    now = date.today().isoformat()
    try:
        with conn:
            conn.execute('''
                    INSERT INTO users (user_id, group_name, first_seen, last_seen)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                       group_name = excluded.group_name,
                       last_seen = excluded.last_seen''', 
                    (str(user_id), group_name, now, now)
                    )
    finally:
        conn.close()

def reset_user_group(user_id, db_name=DB_PATH):
    conn = sqlite3.connect(db_name)
    try:
        with conn:
            conn.execute('''
                        UPDATE users SET group_name = NULL WHERE user_id = ?
                         ''', (user_id,))
            conn.commit()
    finally:
        conn.close()

def track_user(user_id, db_name=DB_PATH):
    now = date.today().isoformat()
    conn = sqlite3.connect(db_name)
    try:
        with conn:
            conn.execute(
                '''
                INSERT INTO users (user_id, first_seen, last_seen)
                VALUES (?, ?, ?)
                ON CONFLICT (user_id) DO UPDATE SET last_seen = excluded.last_seen
                ''',
                (user_id, now, now)
            )
    finally:
        conn.close()
