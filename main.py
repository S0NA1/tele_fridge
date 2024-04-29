import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from config import BOT_TOKEN
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3
import kbs
import logging
from fnmatch import *
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

con = sqlite3.connect("product_db.db")
cur = con.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER NOT NULL,
product TEXT,
data TEXT)
''')
con.commit()
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO, filename="loggs.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

logger = logging.getLogger(__name__)


# COMMANDS
@dp.message(Command("help"))
async def help_me(messege: Message):
    await messege.answer('''Чтобы открыть главную клавиатуру, выберете в меню команду 
➡️Открыть меню выбора

Чтобы скрыть клавиатуру, выберите команду 
➡️Закрыть меню выбора

Чтобы удалить свой профиль и данные навсегда, вы модете воспользоваться двумя способами:
➡️команда Удалить свой профиль в меню выбора
➡️кнопка Удалить профиль в главном меню
‼️Данные не сохранятся‼️''', reply_markup=kbs.start_key)


async def send_message(bot: Bot, message: int, user_id: int):
    chek = cur.execute("SELECT product, data FROM Users WHERE id = ?", (message,)).fetchall()
    con.commit()
    now_data = datetime.datetime.now().date()
    tre_days = []
    week_days = []
    for i in chek:
        obj_data = str(i[1]).split("-")
        first = datetime.date(int(obj_data[0]), int(obj_data[1]), int(obj_data[2]))
        if int(str(first - now_data).split()[0]) == 3:
            tre_days.append([i[0], i[1]])
        if int(str(first - now_data).split()[0]) == 7:
            week_days.append([i[0], i[1]])
    if len(tre_days) != 0:
        await bot.send_message(chat_id=int(user_id),
                               text=f'''Осталось три дня до окончания срока годности
{pping(tre_days)}''')
    else:
        await bot.send_message(chat_id=int(user_id),
                               text="У вас нет продуктов, у которых срок годности закончится через 3 дня")
    if len(week_days) != 0:
        await bot.send_message(chat_id=int(user_id),
                               text=f'''Осталась неделя до конца срока годности
{pping(week_days)}''')
    else:
        await bot.send_message(chat_id=int(user_id),
                               text="У вас нет продуктов, у которых срок годности закончится через неделю")


@dp.message(Command("open_choice"))
async def open_menu(message: Message):
    await message.answer('''Меню выбора открылось

Чтобы закрыть меню выбота, выберите в меню команд
➡️Закрыть меню выбора''', reply_markup=kbs.start_key)


@dp.message(Command("start"))
async def start_menu(message: Message):
    chek = cur.execute("SELECT * FROM Users WHERE id = ?", (message.from_user.id,)).fetchall()
    all_user = cur.execute("SELECT id FROM Users").fetchall()
    con.commit()
    scheduler = AsyncIOScheduler()
    timezone = "Asia/Vladivostok"

    scheduler.add_job(send_message,
                      trigger="cron",
                      hour=17, minute=10,
                      start_date=datetime.datetime.now(),
                      kwargs={
                          "bot": bot,
                          "message": message.from_user.id,
                          "user_id": message.chat.id, }, )
    scheduler.start()
    if len(chek) == 0:
        await message.answer(f'''Добро пожаловать в бот-холодильник😊
‼️ВНИМАНИЕ‼️
Если возникли какие-то вопросы, отправьте команду /help

Удачного пользования🙂 ''',
                             reply_markup=kbs.start_key)
    else:
        await message.answer(
            '''Вы повторно нажали на команду /start, ваша работа в боте не прервана. 
Для удаления данных воспользуйтесь кнопкой "удалить профиль"''',
            reply_markup=kbs.start_key)


@dp.message(Command("delete_profile"))
async def delete_datab(message: Message):
    await message.answer(f"Вы уверены, что хотите удалить все свои данные навсегда?😣",
                         reply_markup=kbs.paginator())


# TEXT COMMANDS
@dp.message(F.text.lower() == "удалить профиль")
async def delete_datab(message: Message):
    await message.answer(f"Вы уверены, что хотите удалить все свои данные навсегда?😣",
                         reply_markup=kbs.paginator())


@dp.callback_query(kbs.Pang.filter(F.action.in_(["del", "no_del"])))
async def yes_no_del(call: CallbackQuery, callback_data: kbs.Pang):
    chek = cur.execute("SELECT * FROM Users WHERE id = ?", (call.from_user.id,)).fetchall()
    con.commit()
    now_id = call.from_user.id
    if callback_data.action == "no_del":
        await call.message.answer("Вы не удалили данные, продолжайте работу",
                                  reply_markup=kbs.start_key)

    elif len(chek) == 0:
        await call.message.answer("У вас нет записанных продуктов, поэтому можете начинать работу сначала",
                                  reply_markup=kbs.write_th)

    elif callback_data.action == "del":
        cur.execute('DELETE FROM Users WHERE id = ?', (now_id,))
        con.commit()
        await call.message.answer(f'''Ваши данные удалены.
        
Чтобы возобновить работу бота, нажмите на команду
➡️/start''',
                                  reply_markup=kbs.start_new_profile)


def pping(spis):
    a = ""
    k = 0
    for i in spis:
        k += 1
        a += str(k) + "." + " " + " ".join([i[0], i[1]]) + ";" + "\n"
    return a


@dp.message(F.text.lower() == "список моих продуктов")
async def chek_product(message: Message):
    now_product = cur.execute("SELECT product, data FROM Users WHERE id = ?", (message.from_user.id,)).fetchall()
    con.commit()
    if len(now_product) == 0:
        await message.answer("Вы еще не записали в таблицу продукты, начните заполнение сейчас!⬇️",
                             reply_markup=kbs.write_th)
    else:
        await message.answer(f'''Ваши продукты:
{pping(now_product)}''',
                             reply_markup=kbs.start_key)


@dp.message(F.text.lower() == "посмотреть просроченное")
async def see_old(messege: Message):
    old_data = cur.execute("SELECT * FROM Users WHERE id = ?", (messege.from_user.id,)).fetchall()
    con.commit()
    now_data = datetime.datetime.now().date()
    convert_result = []
    for i in old_data:
        obj_data = str(i[2]).split("-")
        first = datetime.date(int(obj_data[0]), int(obj_data[1]), int(obj_data[2]))
        if int(str(first - now_data).split()[0]) <= 0:
            convert_result.append([i[1], i[2]])
    if len(convert_result) == 0:
        await messege.answer("У вас нет просроченных продуктов🌱",
                             reply_markup=kbs.start_key)
    else:
        await messege.answer(f'''Ваши просроченные продукты:
{pping(convert_result)}''',
                             reply_markup=kbs.olginator())


@dp.callback_query(kbs.Old.filter(F.action.in_(["out_del", "no_out"])))
async def old_thing(call: CallbackQuery, callback_data: kbs.Old):
    if callback_data.action == "out_del":
        old_data = cur.execute("SELECT * FROM Users WHERE id = ?", (call.from_user.id,)).fetchall()
        con.commit()
        now_data = datetime.datetime.now().date()
        convert_result = []
        if len(old_data) != 0:
            for i in old_data:
                obj_data = str(i[2]).split("-")
                first = datetime.date(int(obj_data[0]), int(obj_data[1]), int(obj_data[2]))
                if int(str(first - now_data).split()[0]) <= 0:
                    convert_result.append([i[1], i[2]])
        for i in convert_result:
            cur.execute("DELETE FROM Users WHERE (product, data) = (?, ?)", (i[0], i[1]))
            con.commit()
        await call.message.answer("Все просроченное удалено✅",
                                  reply_markup=kbs.start_key)
    elif callback_data.action == "no_out":
        await call.message.answer("Вы не удалили просроченное, продолжайте работу",
                                  reply_markup=kbs.start_key)


@dp.message(F.text.lower() == "в главное меню")
async def beck_to_men(messege: Message):
    await messege.answer("Выберите действие⬇️",
                         reply_markup=kbs.start_key)


class Dele(StatesGroup):
    del_object = State()


@dp.message(F.text.lower() == "удалить продукт")
async def del_norm(message: Message, state: FSMContext):
    now_product = cur.execute("SELECT product, data FROM Users WHERE id = ?", (message.from_user.id,)).fetchall()
    con.commit()
    if len(now_product) > 0:
        await state.set_state(Dele.del_object)
        await message.answer(pping(now_product))
        await message.answer('''Отправьте номер продукта, чтобы удалить его📲''')
    else:
        await message.answer("У вас нет записанных продуктов, начните заполнять таблицу⬇️",
                             reply_markup=kbs.write_th)


@dp.message(Dele.del_object)
async def start_delete(message: Message, state: FSMContext):
    await state.update_data(del_norm=message.text)
    now_product = cur.execute("SELECT id, product, data FROM Users WHERE id = ?",
                              (message.from_user.id,)).fetchall()
    now_work = now_product[int(message.text) - 1]
    cur.execute("DELETE FROM Users WHERE (id, product, data) = (?, ?, ?)", (now_work[0], now_work[1], now_work[2]))
    con.commit()
    await message.answer('''Продукт удалён✅

Если хотите удалить что-то ещё, снова нажмите на кнопку
➡ удалить продукт''',
                         reply_markup=kbs.start_key)


class Form(StatesGroup):
    obje = State()
    date = State()


@dp.message(F.text.lower() == "добавить продукт")
async def fill_db(message: Message, state: FSMContext):
    await state.set_state(Form.obje)
    await message.answer("Введите только название продукта⬇️")


@dp.message(Form.obje)
async def name_prod(message: Message, state: FSMContext):
    await state.update_data(obje=message.text)
    await state.set_state(Form.date)
    await message.answer(f'''Введите конец срока годности в виде {datetime.date.today()}
(год, месяц, число)⬇️''')


chis = "0123456789-"


def check_data(n):
    if fnmatch(str(n), "????-??-??"):
        for i in n:
            if i not in chis:
                return 0
        now = n.split("-")
        if int(now[1]) > 12:
            return 0
        if int(now[2]) > 31:
            return 0
        if int(now[1]) == 2 and int(now[2]) > 29:
            return 0
        return 1
    return 0


@dp.message(Form.date)
async def name_da(message: Message, state: FSMContext):
    if check_data(message.text):
        await state.update_data(date=message.text)
        all_data = await state.get_data()
        now = message.from_user.id
        await state.clear()
        i_need = []
        [
            i_need.append(f"{value}")
            for key, value in all_data.items()
        ]
        cur.execute("INSERT INTO Users (id, product, data) VALUES (?, ?, ?)", (now, i_need[0], i_need[1]))
        con.commit()
        await message.answer(f'''Супер, запись создана👍
Что дальше?🤔''',
                             reply_markup=kbs.start_key)

    else:
        while not check_data(message.text):
            await message.reply(f'''Вы ввели дату в неправильном формате.😢
            
‼️Попытайтесь еще раз в формате {datetime.date.today()}
(год, месяц, число)⬇️''',
                                reply_markup=kbs.back_to_me)
            name_prod()


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
