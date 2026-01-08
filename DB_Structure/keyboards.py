from aiogram.types import   InlineKeyboardMarkup, InlineKeyboardButton
def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
    [InlineKeyboardButton(text="📝 Xodim qo'shish", callback_data="register")]
        ]
    )


