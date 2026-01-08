# main_py

import asyncio
import logging
import sys
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ----------------- CONFIG -----------------      
TOKEN = "8526235095:AAGSSg4sVAi0xctRAv6hpolDqI-SjVV7q_E"
ADMIN_ID = 6450678728

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ----------------- DB -----------------
DB_NAME = "employee.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS employee_db (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        first_name TEXT,
        last_name TEXT,
        direction TEXT,
        experience INTEGER,
        duty TEXT,
        registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
    conn.close()

def add_employee(user_id, first_name, last_name, direction, experience, duty):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO employee_db (user_id, first_name, last_name, direction, experience, duty)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, first_name, last_name, direction, experience, duty))
    conn.commit()
    conn.close()

# ----------------- FSM -----------------
class RegisterUser(StatesGroup):
    first_name = State()
    last_name = State()
    direction = State()
    experience = State()
    duty = State()
    confirm = State()

# ----------------- Keyboards -----------------
def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="register")]
        ]
    )

def direction_keyboard():
    # **Muhim:** keyword-only style: text=..., callback_data=...
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Backend Developer", callback_data="backend"),
                InlineKeyboardButton(text="Data Analyst", callback_data="data_analyst")
            ],
            [
                InlineKeyboardButton(text="Graphic Designer", callback_data="designer"),
                InlineKeyboardButton(text="Frontend Developer", callback_data="frontend")
            ]
        ]
    )

def confirm_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlayman", callback_data="confirm")]
        ]
    )

# ----------------- Handlers -----------------
@dp.message(F.text == "/register")
async def cmd_register(message: Message):
    await message.answer("👋 Xush kelibsiz!", reply_markup=main_menu())

@dp.callback_query(F.data == "register")
async def start_registration(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Ismingizni kiriting:")
    await state.set_state(RegisterUser.first_name)
    await cb.answer()

@dp.message(RegisterUser.first_name)
async def handle_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text.strip())
    await message.answer("Familiyangizni kiriting:")
    await state.set_state(RegisterUser.last_name)

@dp.message(RegisterUser.last_name)
async def handle_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text.strip())
    await message.answer("Yo'nalishingizni tanlang:", reply_markup=direction_keyboard())
    await state.set_state(RegisterUser.direction)

@dp.callback_query(RegisterUser.direction)
async def handle_direction(cb: CallbackQuery, state: FSMContext):
    # callback.data qiymati callback_data da berilgan string bo'ladi
    await state.update_data(direction=cb.data)
    await cb.message.answer("Tajribangizni oylar bilan kiriting (faqat raqam):")
    await state.set_state(RegisterUser.experience)
    await cb.answer()

@dp.message(RegisterUser.experience)
async def handle_experience(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        return await message.answer("❌ Iltimos faqat raqam kiriting! (masalan: 12)")

    await state.update_data(experience=int(text))
    await message.answer("Lavozimingizni kiriting (masalan: Senior Backend Developer):")
    await state.set_state(RegisterUser.duty)

@dp.message(RegisterUser.duty)
async def handle_duty(message: Message, state: FSMContext):
    await state.update_data(duty=message.text.strip())
    data = await state.get_data()

    await message.answer(
        f"📋 Ma'lumotlarni tasdiqlang:\n\n"
        f"👤 {data.get('first_name','')} {data.get('last_name','')}\n"
        f"💼 Yo'nalish: {data.get('direction','')}\n"
        f"📊 Tajriba: {data.get('experience','')} oy\n"
        f"📝 Lavozim: {data.get('duty','')}\n\n"
        f"Tasdiqlaysizmi?",
        reply_markup=confirm_keyboard()
    )
    await state.set_state(RegisterUser.confirm)

@dp.callback_query(F.data == "confirm")
async def handle_confirm(cb: CallbackQuery, state: FSMContext):
    # aiogram 3.x da state filtiri dekoratorda ishlatmang — ichida tekshiring
    current = await state.get_state()
    if current != RegisterUser.confirm.state:
        # Bu confirm callback boshqa holatdan kelgan bo'lishi mumkin — shunchaki bekor qiling
        await cb.answer()
        return

    data = await state.get_data()
    user_id = cb.from_user.id

    # DB ga yozish
    add_employee(
        user_id,
        data.get("first_name", ""),
        data.get("last_name", ""),
        data.get("direction", ""),
        data.get("experience", 0),
        data.get("duty", "")
    )

    await cb.message.answer("✅ Ma'lumot saqlandi! Rahmat!")
    # adminga xabar
    await bot.send_message(
        ADMIN_ID,
        f"📥 Yangi xodim ro'yxatdan o'tdi:\n\n"
        f"👤 {data.get('first_name','')} {data.get('last_name','')}\n"
        f"💼 {data.get('direction','')}\n"
        f"📊 {data.get('experience',0)} oy\n"
        f"📝 {data.get('duty','')}\n"
        f"🆔 ID: {user_id}"
    )

    await state.clear()
    await cb.answer()

# --------------- RUN -----------------
async def main():
    init_db()
    print("🤖 Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
