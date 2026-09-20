import requests
from bs4 import BeautifulSoup
from config import WEEK, BASE_URL

def get_html(num_week):
    response = requests.get(BASE_URL+str(num_week), timeout=10)
    soup = BeautifulSoup(response.text, 'lxml')
    list_lessons = soup.find('table', class_="table align-middle")
    dates = get_date_on_week(list_lessons)
    table_lessons = list_lessons.find_all("tr")
    return table_lessons, dates

def get_data_from_info_lesson(info_lesson: str):
    normalized = " ".join(info_lesson.split())
    if "подгруппа" not in normalized:
        lst = normalized.rsplit(" ", 1)
        return None, lst[0].strip(), lst[1].strip()
    else:
        start = normalized.find("(")
        end = normalized.find(")", start)
        subgroup = normalized[start:end].split(" ")[1]
        normalized = normalized[end+2:].split(" ")
        teacher = normalized[0] + " " + normalized[1] + " " + normalized[2] + " " + normalized[3] # Сборка в строку должности и фио препода
        cabinet = normalized[4]
        return int(subgroup), teacher.strip(), cabinet.strip()

def get_info_from_html(table):
    lesson_type = table.find("div", class_="card-header").text.strip()
    name = table.find("h5", class_="card-title").text.strip()
    info = table.find("p", class_="card-text").text.strip()
    return lesson_type, name, info

def get_date_on_week(list_lessons):
    dates = list_lessons.find_all("center")
    db_day = []
    for i in dates:
        date = " ".join(str(i).split())
        a1 = date.find("/")
        a2 = date.find("/", a1+1)
        normal_day = date[a1+2:a2-1].strip()[:-2].split(".")
        db_day.append(f"{normal_day[2]}-{normal_day[1]}-{normal_day[0]}")
    return {WEEK[i]:db_day[i] for i in range(len(WEEK))}


def get_row_of_lesson(num_row: int, schedule: dict, table_lessons, dates_map):
    row_lessons = table_lessons[num_row].find_all("td")[1:]
    for i in range(len(row_lessons)):       
        number_lesson = num_row+1
        # Проверка наличия пары
        if "div" not in str(row_lessons[i]):
            schedule[WEEK[i]].append({"number": number_lesson, "date":  dates_map[WEEK[i]],"type": None, "subject": None, "subgroup": None, "teacher": None, "cabinet": None})
        else:
            lessons = row_lessons[i]
            quant_lesson_of_day = len(lessons.find_all("div", class_=["card", "mb-3"]))
            # Разделение, если есть пересекающиеся пары в одном слоте
            if quant_lesson_of_day < 2:               
                type_lesson, name_lesson, info_lesson = get_info_from_html(lessons)
                subgroup, teacher, cabinet = get_data_from_info_lesson(info_lesson)
                schedule[WEEK[i]].append({"number": number_lesson, "date":  dates_map[WEEK[i]], "type": type_lesson, "subject": name_lesson, "subgroup": subgroup, "teacher": teacher, "cabinet": cabinet})
            else:
                for lesson in lessons.find_all("div", class_=["card", "mb-3"]):
                    type_lesson, name_lesson, info_lesson = get_info_from_html(lesson)
                    subgroup, teacher, cabinet = get_data_from_info_lesson(info_lesson)
                    schedule[WEEK[i]].append({"number": number_lesson, "date":  dates_map[WEEK[i]], "type": type_lesson, "subject": name_lesson, "subgroup": subgroup, "teacher": teacher, "cabinet": cabinet})

def start_parse(num_week):
    schedule = {day: [] for day in WEEK}
    table_lessons, dates_map = get_html(num_week)
    for i in range(0, 8):
        get_row_of_lesson(i, schedule, table_lessons, dates_map)
    return schedule
