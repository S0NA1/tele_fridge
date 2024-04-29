from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_key = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить продукт"), KeyboardButton(text="Удалить продукт")],
        [KeyboardButton(text="Посмотреть просроченное"), KeyboardButton(text="Список моих продуктов"),
         KeyboardButton(text="Удалить профиль")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Выберите действие",
    selective=True
)


class Pang(CallbackData, prefix="pag"):
    action: str
    page: int


def paginator(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Да", callback_data=Pang(action="del", page=page).pack()),
        InlineKeyboardButton(text="Нет", callback_data=Pang(action="no_del", page=page).pack()),
        width=2
    )
    return builder.as_markup()


start_new_profile = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start")]], resize_keyboard=True,
                                        one_time_keyboard=True)
write_th = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Добавить продукты")], [KeyboardButton(text="В главное меню")]],
    resize_keyboard=True,
    one_time_keyboard=True)

back_to_me = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="В главное меню")]], resize_keyboard=True,
                                 one_time_keyboard=True)


class Old(CallbackData, prefix="older"):
    action: str


def olginator():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Удалить все", callback_data=Old(action="out_del").pack()),
        InlineKeyboardButton(text="Не удалять", callback_data=Old(action="no_out").pack()),
        width=2
    )
    return builder.as_markup()
