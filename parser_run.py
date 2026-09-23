from config import SEMESTR_START, BASE_URL, GROUP_URL_MAP
from datetime import datetime, timedelta, date
from parser import start_parse
from time import sleep
from database.db import save_lesson, create_db

def current_this_week(isodate: datetime.date):
    today =  datetime.fromisoformat(str(isodate))
    if isinstance(today, datetime):
        today = today.date()
    monday = today - timedelta(days=today.weekday())
    number_week = ((monday - SEMESTR_START).days // 7) + 1
    return number_week

def build_url(target_date, group_name):
    url = BASE_URL.replace("{{group}}", GROUP_URL_MAP[group_name])
    url = url + str(current_this_week(target_date))
    return url

def is_group_supported(group_name):
    return group_name in GROUP_URL_MAP

def main():
    print(f"[{datetime.now()}] Парсер запущен")
    create_db()
    today = date.today()
    groups = list(GROUP_URL_MAP.keys())
    number_week = current_this_week(today.isoformat()) 
    for group_name in groups:
        try:
            week1 = start_parse(number_week, group_name)
            week2 = start_parse(number_week+1, group_name)
            save_lesson(week1, group_name)
            save_lesson(week2, group_name)
            print(f"{group_name}: Недели {number_week} и {number_week + 1} сохранены")
        except Exception as error:
            print(f"{group_name} не сохрнилась из-за {error}")
        sleep(13)
    print(f"[{datetime.now()}] Парсер завершен")


if __name__ ==  "__main__":
    main()