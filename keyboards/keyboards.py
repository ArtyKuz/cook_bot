from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_kb(width: int, *args, **kwargs) -> InlineKeyboardMarkup:
    # Инициализируем билдер
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Инициализируем список для кнопок
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if kwargs:
        for callback, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=callback))
    if args:
        for button in args:
            # print(button)
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button))



    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)

    # Возвращаем объект инлайн-клавиатуры
    return kb_builder.as_markup(resize_keyboard=True)


def create_pagination_kb(width: int, page, dishes, *args) -> InlineKeyboardMarkup:

    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    current_dishes = dishes[str(page)]
    for callback, text in current_dishes:
        buttons.append(InlineKeyboardButton(
            text=text,
            callback_data=callback))
    kb_builder.row(*buttons, width=width)
    buttons: list[InlineKeyboardButton] = []
    if page - 1 > 0:
        buttons.append(InlineKeyboardButton(
            text='Назад ⬅',
            callback_data='back'))
    if dishes.get(str(page + 1)):
        buttons.append(InlineKeyboardButton(
            text='Вперед ➡',
            callback_data='forward'))
    kb_builder.row(*buttons, width=2)
    buttons: list[InlineKeyboardButton] = []
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=button,
                callback_data=button))
    kb_builder.row(*buttons, width=width)
    return kb_builder.as_markup(resize_keyboard=True)
