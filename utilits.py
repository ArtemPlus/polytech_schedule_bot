import logging
import requests
from json import dumps
from bs4 import BeautifulSoup
from log_config import setup_logging

logger = logging.getLogger(__name__)

base_url = "http://db.biysk.secna.ru/schedule/schedule.test_r.search_fak?"

def get_all_group():
    def _get_name_group(soup):
        if soup is None:
            return []
        all_group = soup.find_all("a", class_="list-group-item")
        res = []
        for i in all_group:
            res.append(i.text.strip())
        return res
    
    def _get_html_group(faculty):
        try:
            response = requests.get(base_url, timeout=10, params={"name_dl": faculty.encode('ISO-8859-5'), "cury": "2026", "cursem": "1"})
            soup = BeautifulSoup(response.text, 'lxml')
            return soup
        except Exception as error:
            logger.error("Ошибка при запросе: %s", error, exc_info=True)
            return None

    list_group = [*_get_name_group(_get_html_group("Технологический")), *_get_name_group(_get_html_group("Инженерный"))]
    return list_group

def save_list_group(list_group):
    if len(list_group) != 0:
        with open("groups.json", "w", encoding="UTF-8") as file:
            file.write(dumps(list_group))
        return "Данные успешно записаны"
    return "В файл нечего записывать"

if __name__ == "__main__":
    setup_logging()
    save_list_group(get_all_group())