from config import BELL_TIMES, MONTH
from datetime import date
from parser_run import current_this_week

def append_info_about_pair(lines, pair):    
    lines.append(f"{pair['number']}. {BELL_TIMES[pair['number']]} - {pair['subject']}")
    if pair["subgroup"] is not None:
        lines.append(f"   • Подгруппа: {pair['subgroup']}")
    lines.append(f"   • Тип: {pair["type"]}")
    lines.append(f"   • Препод: {pair['teacher']}")
    lines.append(f"   • Кабинет: {pair['cabinet']}")
    if str(pair["number"]) != "8":
        lines.append(" ")

def format_day(lessons: list[dict], day: str, group_name):
    try:
        day_lesson = lessons[day]
        lines = []
        date_today = day_lesson[0]["date"]
        normal_date_today = date.fromisoformat(date_today)
        lines.append(f"📅 {day} - {normal_date_today.day} {MONTH[normal_date_today.month]} {normal_date_today.year}")
        lines.append(f"📚 Учебная неделя - {current_this_week(normal_date_today)}")
        lines.append(f"👥 Учебная группа - {group_name}")
        lines.append("----")
        for pair in day_lesson:
            if pair["subject"] is None:
                lines.append(f"{pair['number']}. {BELL_TIMES[pair['number']]} - ❌ Пары нет")
                if str(pair["number"]) != "8":
                    lines.append(" ")
            else:
                append_info_about_pair(lines, pair)
    except Exception as error:
        print(f"Форматтер упал из-за {error}")
                
    lines.append("----")
    lines.append("Посмотреть оригинал расписания на сайте БТИ - {{SOURCE}}")
    return "\n".join(lines)

def format_search(lessons):
    print(date_today)
    for lesson in lessons:
        if lesson["date"] != current_date:
            current_date = lesson["date"]
            print(f"\n📅 {current_date}")
        print(f'{lesson["number"]}: {lesson["group_name"]}')
        if lesson["subgroup"] is not None:
            print(f"   • Подгруппа: {lesson['subgroup']}")
        print(f"   • Тип: {lesson["type"]}")
        print(f"   • Препод: {lesson['teacher']}")
        print(f"   • Кабинет: {lesson['cabinet']}")
format_search([{'group_name': 'БТ-61', 'number': 2, 'date': '2026-10-06', 'type': 'Лекция', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '02Б'}, {'group_name': 'ИСТ-61', 'number': 2, 'date': '2026-10-06', 'type': 'Лекция', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '02Б'}, {'group_name': 'ИСТ-62', 'number': 2, 'date': '2026-10-06', 'type': 'Лекция', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '02Б'}, {'group_name': 'КТМ-61', 'number': 2, 'date': '2026-10-06', 'type': 'Лекция', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '02Б'}, {'group_name': 'ПС-61', 'number': 2, 'date': '2026-10-06', 'type': 'Лекция', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '02Б'}, {'group_name': 'С-61', 'number': 2, 'date': '2026-10-06', 'type': 'Лекция', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '02Б'}, {'group_name': 'БТ-61', 'number': 4, 'date': '2026-10-06', 'type': 'Практическое занятие', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '216А'}, {'group_name': 'ПС-61', 'number': 4, 'date': '2026-10-06', 'type': 'Практическое занятие', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '216А'}, {'group_name': 'С-61', 'number': 5, 'date': '2026-10-06', 'type': 'Практическое занятие', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '216А'}, {'group_name': 'КТМ-61', 'number': 3, 'date': '2026-10-07', 'type': 'Практическое занятие', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '216А'}, {'group_name': 'ИСТ-61', 'number': 4, 'date': '2026-10-07', 'type': 'Практическое занятие', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '216А'}, {'group_name': 'ИСТ-62', 'number': 5, 'date': '2026-10-07', 'type': 'Практическое занятие', 'subject': 'История России', 'subgroup': None, 'teacher': 'проф. д.н. Дегальцева Е.А.', 'cabinet': '216А'}])