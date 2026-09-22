import requests
from bs4 import BeautifulSoup
from config import WEEK, BASE_URL, GROUP_URL_MAP, ROOMS

def get_html(num_week, group_name):
    url = BASE_URL.replace("{{group}}", GROUP_URL_MAP[group_name])
    url = url + str(num_week)
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'lxml')
    list_lessons = soup.find('table', class_="table align-middle")
    dates = get_date_on_week(list_lessons)
    table_lessons = list_lessons.find_all("tr")
    return table_lessons, dates

def parse_string_info(normalized, subgroup=None):
    teacher = ""
    cabinet = ""
    for i in range(len(normalized)):
        if normalized[i] in ROOMS:
            for j in range(0, i):
                teacher = teacher + normalized[j] + " "
            cabinet = normalized[i]
            break
    if cabinet is None:
        return None
    if subgroup is not None:
        return int(subgroup), teacher.strip(), cabinet
    return teacher.strip(), cabinet

def get_data_from_info_lesson(info_lesson: str):
    normalized = " ".join(info_lesson.split())
    if "подгруппа" not in normalized:
        normalized = normalized.split(" ")
        result = parse_string_info(normalized)
        if result is None:
            print(f"Кабинет не найден: {info_lesson}")
            return None, " ".join(normalized), None
        teacher, cabinet = result
        return None, teacher, cabinet
    else:
        start = normalized.find("(")
        end = normalized.find(")", start)
        subgroup = normalized[start+1:end].strip().split(" ")[0]
        normalized = normalized[end+1:].strip().split(" ")
        subgroup, teacher, cabinet = parse_string_info(normalized, subgroup)
        return subgroup, teacher, cabinet
            
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

def start_parse(num_week, group_name):
    schedule = {day: [] for day in WEEK}
    table_lessons, dates_map = get_html(num_week, group_name)
    for i in range(0, 8):
        get_row_of_lesson(i, schedule, table_lessons, dates_map)
    return schedule