# start_stop.py
from aiogram import types
from bot_config import dp, bot
from database import cursor, conn
from keyboards import get_main_menu, get_channel_menu
from messages import get_user_language, TEXTS
from utils import can_perform_action, send_message_loop
from globals import tasks, last_action_time, previous_prices
from time import time
from aiogram.exceptions import TelegramBadRequest

async def process_start_channel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    channel_num = int(callback.data.split('_')[-1])
    can_action, remaining_time = can_perform_action(user_id, "start")
    if not can_action:
        cursor.execute(f"SELECT channel{channel_num}_id, channel{channel_num}_contract FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        chat_id, contract = result if result else (None, None)
        text, keyboard = get_channel_menu(channel_num, chat_id, contract, user_id)
        new_text = TEXTS[lang]['wait'].format(seconds=remaining_time, action="starting" if lang == 'en' else "запуском")
        try:
            if callback.message.text != new_text:
                await callback.message.edit_text(new_text, reply_markup=keyboard)
        except TelegramBadRequest:
            pass
        await callback.answer()
        return
    cursor.execute(f"SELECT channel{channel_num}_id, channel{channel_num}_contract, running FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    chat_id, contract, running = row if row else (None, None, False)
    if chat_id and contract:
        if not running:
            cursor.execute("UPDATE users SET running = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
        task_key = f"{user_id}_{channel_num}"
        if task_key not in tasks:
            tasks[task_key] = asyncio.create_task(send_message_loop(user_id, channel_num))
        text, keyboard = get_channel_menu(channel_num, chat_id, contract, user_id)
        await callback.message.edit_text(TEXTS[lang]['started'].format(channel_num=channel_num), reply_markup=keyboard)
    else:
        text, keyboard = get_channel_menu(channel_num, chat_id, contract, user_id)
        await callback.message.edit_text(TEXTS[lang]['missing_setup'], reply_markup=keyboard)
    await callback.answer()

async def process_stop_channel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    channel_num = int(callback.data.split('_')[-1])
    task_key = f"{user_id}_{channel_num}"
    if task_key in tasks:
        tasks[task_key].cancel()
        del tasks[task_key]
    if task_key in previous_prices:
        del previous_prices[task_key]
    cursor.execute(f"SELECT channel{channel_num}_id, channel{channel_num}_contract FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    chat_id, contract = result if result else (None, None)
    text, keyboard = get_channel_menu(channel_num, chat_id, contract, user_id)
    await callback.message.edit_text(TEXTS[lang]['stopped'], reply_markup=keyboard)
    last_action_time[user_id] = time()
    await callback.answer()

async def process_start_all(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    can_action, remaining_time = can_perform_action(user_id, "start")
    if not can_action:
        new_text = TEXTS[lang]['wait'].format(seconds=remaining_time, action="starting" if lang == 'en' else "запуском")
        try:
            if callback.message.text != new_text:
                await callback.message.edit_text(new_text, reply_markup=get_main_menu(user_id))
        except TelegramBadRequest:
            pass
        await callback.answer()
        return
    cursor.execute("SELECT channel1_id, channel2_id, channel3_id, channel1_contract, channel2_contract, channel3_contract FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone() or (None, None, None, None, None, None)
    channels = result[:3]
    contracts = result[3:]
    if not any(channels) or not any(contracts):
        await callback.message.edit_text(TEXTS[lang]['no_channels'], reply_markup=get_main_menu(user_id))
        await callback.answer()
        return
    cursor.execute("UPDATE users SET running = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    for i, (chat_id, contract) in enumerate(zip(channels, contracts), 1):
        if chat_id and contract:
            task_key = f"{user_id}_{i}"
            if task_key not in tasks:
                tasks[task_key] = asyncio.create_task(send_message_loop(user_id, i))
    await callback.message.edit_text(TEXTS[lang]['all_started'], reply_markup=get_main_menu(user_id))
    await callback.answer()

async def process_stop_all(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    cursor.execute("SELECT channel1_id, channel2_id, channel3_id FROM users WHERE user_id = ?", (user_id,))
    channels = cursor.fetchone() or (None, None, None)
    cursor.execute("UPDATE users SET running = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    for i in range(1, 4):
        task_key = f"{user_id}_{i}"
        if task_key in tasks:
            tasks[task_key].cancel()
            del tasks[task_key]
        if task_key in previous_prices:
            del previous_prices[task_key]
    await callback.message.edit_text(TEXTS[lang]['all_stopped'], reply_markup=get_main_menu(user_id))
    last_action_time[user_id] = time()
    await callback.answer()

# Регистрация обработчиков
dp.callback_query.register(process_start_channel, lambda c: c.data.startswith("start_") and not c.data.endswith("_all"))
dp.callback_query.register(process_stop_channel, lambda c: c.data.startswith("stop_") and not c.data.endswith("_all"))
dp.callback_query.register(process_start_all, lambda c: c.data == "start_all")
dp.callback_query.register(process_stop_all, lambda c: c.data == "stop_all")
