from vkbottle import Bot, Keyboard, Callback, GroupEventType
from vkbottle.bot import MessageEvent
from config import WEEK
from dotenv import load_dotenv
from os import getenv
from database.db import get_lesson, track_user, create_db
from formatter import format_day
from parser_run import build_url
from datetime import datetime, timedelta, date
import asyncio

load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")
bot = Bot(BOT_TOKEN)

async def make_answer(target_date: date):
    day = target_date.weekday()
    if day == 6:
        return "Воскресенье - не учебный день!"
    day = WEEK[target_date.weekday()]
    target_date = target_date.isoformat()
    schedule, group_name = await asyncio.to_thread(get_lesson, str(target_date))
    res = await asyncio.to_thread(format_day, schedule, day, group_name)
    url = await asyncio.to_thread(build_url, target_date)
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

@bot.on.message(text=["start", "Start", "Начать"])
async def hello(message):
    await asyncio.to_thread(track_user, message.from_id)
    text = "\n".join([
    "Бот показывает расписание пока только для ИСТ-61",
    "======",
    "today, td, сегодня — расписание на сегодня",
    "tomorrow, tm, завтра — расписание на завтра",
    "week, wk, неделя — расписание на неделю",
])
    await message.answer(text)

@bot.on.message(text=["Today", "today", "сегодня", "td", "Td", "Сегодня"])
async def cmd_td(message):
    await asyncio.to_thread(track_user, message.from_id)
    target_date = datetime.now().date()
    res = await make_answer(target_date) 
    await message.answer(res)

@bot.on.message(text=["Tomorrow", "tomorrow", "tm", "завтра", "Tm", "Завтра"])
async def cmd_tm(message):
    await asyncio.to_thread(track_user, message.from_id)
    target_date = datetime.now().date() + timedelta(days=1)
    res = await make_answer(target_date) 
    await message.answer(res)

@bot.on.message(text=["week", "wk", "Wk", "неделя", "Неделя"])
async def cmd_week(message):
    await asyncio.to_thread(track_user, message.from_id)
    today: date = date.today()
    if today.weekday() == 6:
        today = today + timedelta(days=1)
    else:
        today = today - timedelta(days=today.weekday())
    text = await make_answer(today)
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
    target_date: date = date.fromisoformat(event.payload.get("date"))
    text = await make_answer(target_date)
    keyboard = build_week_keyboard(target_date)
    await event.edit_message(text, keyboard=keyboard)
    
if __name__ == "__main__":
    create_db()
    bot.run()