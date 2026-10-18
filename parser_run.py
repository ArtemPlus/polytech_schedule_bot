import logging
from config import SEMESTR_START, BASE_URL, GROUP_LIST
from datetime import datetime, timedelta, date
from parser import start_parse
from time import sleep
from requests import Request
from random import randint
from database.db import save_lesson, create_db
from log_config import setup_logging

logger = logging.getLogger(__name__)

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
    setup_logging()
    logger.info("Парсер запущен")
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
                    logger.info("%s: Неделя %s сохранена", group_name, num_week)
            except Exception as error_group:
                logger.error("Группа %s не сохранилась из-за %s", group_name, error_group, exc_info=True)
            sleep(randint(10, 20))
    except Exception as error:
        logger.error("Парсер либо бд упали из-за %s", error, exc_info=True)
        stat_error = True
    if not(stat_error):
        logger.info("Парсер завершен успешно")
        


if __name__ ==  "__main__":
    main()