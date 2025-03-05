# intervals.py
from aiogram import types
from bot_config import dp
from database import cursor, conn
from keyboards import get_main_menu, get_interval_keyboard
from messages import get_user_language, TEXTS

@dp.callback_query(lambda c: c.data == "set_interval")
async def process_set_interval(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    await callback.message.edit_text(TEXTS[lang]['interval_prompt'], reply_markup=get_interval_keyboard(user_id))
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("interval_"))
async def process_interval_choice(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    interval_map = {"interval_1": 60, "interval_3": 180, "interval_10": 600}
    new_interval = interval_map[callback.data]
    cursor.execute("UPDATE users SET interval = ? WHERE user_id = ?", (new_interval, user_id))
    conn.commit()
    await callback.message.edit_text(TEXTS[lang]['interval_set'].format(minutes=new_interval // 60), reply_markup=get_main_menu(user_id))
    await callback.answer()
