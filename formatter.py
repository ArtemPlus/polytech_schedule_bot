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
                
    lines.append("----")
    lines.append("Посмотреть оригинал расписания на сайте БТИ - {{SOURCE}}")
    return "\n".join(lines)