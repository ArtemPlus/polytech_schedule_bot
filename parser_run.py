from config import SEMESTR_START, BASE_URL, GROUP_LIST
from datetime import datetime, timedelta, date
from parser import start_parse
from time import sleep
from requests import Request
from random import randint
from database.db import save_lesson, create_db

def current_this_week(isodate: datetime.date):
    today =  datetime.fromisoformat(str(isodate))
    if isinstance(today, datetime):
        today = today.date()
    monday = today - timedelta(days=today.weekday())
    number_week = ((monday - SEMESTR_START).days // 7) + 1
    return number_week

def build_url(target_date, group_name):
    num_week = current_this_week(target_date)
    params = {"name_group_dl": group_name.encode("ISO-8859-5"), "cury": "2026", "cursem": "1", "ned_dl": num_week}
    obj = Request("GET", BASE_URL, params=params).prepare()
    return obj.url

def is_group_supported(group_name):
    return group_name in GROUP_LIST

def main():
    print(f"[{datetime.now()}] Парсер запущен")
    stat_error = False
    try:
        create_db()
        today = date.today()
        number_week = current_this_week(today.isoformat()) 
        for group_name in GROUP_LIST:
            weeks = []
            try:
                if 0 <= today.weekday() <= 3:
                    weeks.append(number_week)
                elif today.weekday() in (4, 5):
                    weeks.append(number_week)
                    weeks.append(number_week+1)
                else:
                    weeks.append(number_week+1)
                for num_week in weeks:
                    week = start_parse(num_week, group_name)
                    save_lesson(week, group_name)
                    print(f"{group_name}: Неделя {num_week} сохранены")
            except Exception as error_group:
                print(f"{group_name} не сохранилась из-за {error_group}")
            sleep(randint(10, 20))
    except Exception as error:
        print(f"[{datetime.now()}] Парсер либо бд упали из-за {error}")
        stat_error = True
    if not(stat_error):
        print(f"[{datetime.now()}] Парсер завершен успешно")
        


if __name__ ==  "__main__":
    main()