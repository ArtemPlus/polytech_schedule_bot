from config import SEMESTR_START, BASE_URL, GROUP_URL_MAP
from datetime import datetime, timedelta, date
from parser import start_parse
from time import sleep
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
    url = BASE_URL.replace("{{group}}", GROUP_URL_MAP[group_name])
    url = url + str(current_this_week(target_date))
    return url

def is_group_supported(group_name):
    return group_name in GROUP_URL_MAP

def main():
    print(f"[{datetime.now()}] Парсер запущен")
    stat_error = False
    try:
        create_db()
        today = date.today()
        groups = list(GROUP_URL_MAP.keys())
        number_week = current_this_week(today.isoformat()) 
        for group_name in groups:
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
        stat_error = True
    if stat_error:
        print(f"[{datetime.now()}] Парсер завершен успешно")
    else:
        print(f"Парсер либо бд упали из-за {error}")


if __name__ ==  "__main__":
    main()