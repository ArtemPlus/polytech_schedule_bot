from config import SEMESTR_START, BASE_URL
from datetime import datetime, timedelta, date
from parser import start_parse
from database.db import save_lesson, create_db

def current_this_week(isodate: datetime.date):
    today =  datetime.fromisoformat(str(isodate))
    if isinstance(today, datetime):
        today = today.date()
    monday = today - timedelta(days=today.weekday())
    number_week = ((monday - SEMESTR_START).days // 7) + 1
    return number_week

def build_url(target_date):
    url = BASE_URL + str(current_this_week(target_date))
    return url

def main():
    create_db()
    today = date.today()
    number_week = current_this_week(date.isoformat(today)) 
    week1 = start_parse(number_week)
    week2 = start_parse(number_week+1)
    save_lesson(week1)
    save_lesson(week2)
    print(f"Недели {number_week} и {number_week + 1} сохранены")


if __name__ ==  "__main__":
    main()
# испраивть баг с номером недели