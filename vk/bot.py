from vkbottle import Bot, Keyboard, Callback, GroupEventType
from vkbottle.bot import MessageEvent
from config import WEEK
from dotenv import load_dotenv
from os import getenv
from database.db import get_lesson, track_user, create_db, get_group_by_id, set_group_by_id, reset_user_group
from formatter import format_day
from parser_run import build_url, is_group_supported
from datetime import datetime, timedelta, date
import asyncio

load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")
bot = Bot(BOT_TOKEN)

async def make_answer(target_date: date, group_name: str):
    day = target_date.weekday()
    if day == 6:
        return "Воскресенье - не учебный день!"
    day = WEEK[target_date.weekday()]
    target_date = target_date.isoformat()
    schedule = await asyncio.to_thread(get_lesson, str(target_date), group_name)
    res = await asyncio.to_thread(format_day, schedule, day, group_name)
    url = await asyncio.to_thread(build_url, target_date, group_name)
    res = res.replace("{{SOURCE}}", url)
    return res

def build_week_keyboard(target_date: date):
    keyboard = Keyboard(inline=True)
    monday = target_date - timedelta(days=target_date.weekday())
    saturday = monday + timedelta(days=5)
    if target_date > monday:
        prev_date: date = target_date - timedelta(days=1)
        keyboard.add(Callback("◀", payload={"cmd": "week", "date": prev_date.isoformat()}))
    if target_date < saturday:
        next_day: date = target_date + timedelta(days=1)
        keyboard.add(Callback("▶", payload={"cmd": "week", "date": next_day.isoformat()}))
    return keyboard.get_json()

@bot.on.message(text=["Начать"])
async def cmd_begin(message):
    text = "\n".join([
        "Привет! Этот бот показывает расписание для выбранной группы. (пока только 1 и 2 курсов)",
        "Показ расписания производится на основе данных с сайта БТИ.",
        "Актуализация расписания в боте происходит каждые 6 часов, начиная с полуночи текущего дня."
        "Для начала работы с ботом в ответном сообщении введи свою группу.",
        "Вводи её официальное название, соблюдая регистр, например, ИСТ-61, КТМ-61 и т.д."
    ])
    await message.answer(text)

@bot.on.message(text=["start", "Start"])
async def hello(message):
    await asyncio.to_thread(track_user, message.from_id)
    text = "\n".join([
    "Бот показывает расписание пока только для групп первого/второго курса Технологического Факультета",
    "======",
    "Today, today, td, Td -> расписание на сегодня",
    "Tomorrow, tomorrow, tm, Tm -> расписание на завтра",
    "Week, week, wk, Wk -> расписание на неделю"
    "======"
    "Change, change, cg, Cg -> сбросить текущую группу и задать новую"
])
    await message.answer(text)

@bot.on.message(text=["Change", "change", "cg", "Cg"])
async def cmd_change(message):
    await asyncio.to_thread(track_user, message.from_id)
    await asyncio.to_thread(reset_user_group, message.from_id)
    await message.answer("Текущая группа сброшена. Напиши название группы, для которой ты хочешь получить расписание")

@bot.on.message(text=["Today", "today", "td", "Td"])
async def cmd_td(message):
    await asyncio.to_thread(track_user, message.from_id)
    target_date = datetime.now().date()
    group_name = get_group_by_id(message.from_id)
    if group_name is None:
        await message.answer("Сначала выбери группу")
        return
    res = await make_answer(target_date, group_name) 
    await message.answer(res)

@bot.on.message(text=["Tomorrow", "tomorrow", "tm", "Tm"])
async def cmd_tm(message):
    await asyncio.to_thread(track_user, message.from_id)
    target_date = datetime.now().date() + timedelta(days=1)
    group_name = get_group_by_id(message.from_id)
    if group_name is None:
        await message.answer("Сначала выбери группу")
        return
    res = await make_answer(target_date, group_name) 
    await message.answer(res)

@bot.on.message(text=["week", "wk", "Wk", "Week"])
async def cmd_week(message):
    await asyncio.to_thread(track_user, message.from_id)
    today: date = date.today()
    if today.weekday() == 6:
        today = today + timedelta(days=1)
    else:
        today = today - timedelta(days=today.weekday())
    group_name = get_group_by_id(message.from_id)
    if group_name is None:
        await message.answer("Сначала выбери группу")
        return
    text = await make_answer(today, group_name)
    keyboard = build_week_keyboard(today)
    await message.answer(text, keyboard=keyboard)

@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent)
async def handle_week(event: MessageEvent):
    if event.payload.get("cmd") != "week":
        return
    await event.ctx_api.messages.send_message_event_answer(
        event_id=event.event_id,
        user_id=event.user_id,
        peer_id=event.peer_id,
    )
    group_name = get_group_by_id(event.user_id)
    if group_name is None:
        await event.answer("Для показа расписания выбери напиши свою группу, соблюдая регистр, например, ИСТ-61")
        return
    target_date: date = date.fromisoformat(event.payload.get("date"))
    text = await make_answer(target_date, group_name)
    keyboard = build_week_keyboard(target_date)
    await event.edit_message(text, keyboard=keyboard)

@bot.on.message()
async def handler(message):
    if not message.text:
        return
    user_id = message.from_id
    await asyncio.to_thread(track_user, user_id)
    if await asyncio.to_thread(get_group_by_id, user_id):
        return
        #await message.answer("Твоя группа уже в БД, либо команда введена неправильно. Пропиши Start или start (без / в начале), чтобы увидеть список доступных команд")
    else:
        if await asyncio.to_thread(is_group_supported, message.text.strip()):
            group_name = message.text.strip()
            await asyncio.to_thread(set_group_by_id, user_id, group_name)
            await message.answer(f"Записал! Твоя группа - {group_name}. Введи Start или start (без / в начале) для просмотра доступных команд")
        else:
            await message.answer("Такая группа не найдена, либо к тебе ни привязана никакая группа. Попробуй ввести свою группу ещё раз, соблюдая регистр, например, ИСТ-61")

    
    
if __name__ == "__main__":
    create_db()
    bot.run()