# channels.py
from aiogram import types
from aiogram.fsm.context import FSMContext
from src.bot_config import bot, dp
from src.database import cursor, conn
from src.states import ChannelSetup
from src.keyboards import get_main_menu, get_channel_menu, get_back_keyboard
from src.messages import get_user_language, TEXTS
from src.utils import can_perform_action
from src.globals import last_contract_change_time

@dp.message(lambda message: message.text == "/start")
async def send_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT user_id FROM blacklist WHERE user_id = ?", (user_id,))
    if cursor.fetchone():
        await message.answer("Access denied!")
        return
    cursor.execute("INSERT OR IGNORE INTO users (user_id, language) VALUES (?, ?)", (user_id, 'ru'))
    conn.commit()
    lang = get_user_language(user_id)
    await bot.send_message(chat_id=message.chat.id, text=TEXTS[lang]['welcome'], reply_markup=get_main_menu(user_id), parse_mode="HTML")
    await state.clear()

@dp.callback_query(lambda c: c.data == "switch_language")
async def process_switch_language(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    current_lang = get_user_language(user_id)
    new_lang = 'en' if current_lang == 'ru' else 'ru'
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (new_lang, user_id))
    conn.commit()
    await callback.message.edit_text(TEXTS[new_lang]['welcome'], reply_markup=get_main_menu(user_id), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_main")
async def process_back_to_main(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    await callback.message.edit_text(TEXTS[lang]['welcome'], reply_markup=get_main_menu(user_id), parse_mode="HTML")
    await state.clear()
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("back_to_channel_"))
async def process_back_to_channel(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    channel_num = int(callback.data.split('_')[-1])
    cursor.execute(f"SELECT channel{channel_num}_id, channel{channel_num}_contract FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    chat_id, contract = result if result else (None, None)
    text, keyboard = get_channel_menu(channel_num, chat_id, contract, user_id)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.clear()
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("manage_channel_"))
async def process_manage_channel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    channel_num = int(callback.data.split('_')[-1])
    cursor.execute(f"SELECT channel{channel_num}_id, channel{channel_num}_contract FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    chat_id, contract = result if result else (None, None)
    text, keyboard = get_channel_menu(channel_num, chat_id, contract, user_id)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("set_channel_"))
async def process_set_channel(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    channel_num = int(callback.data.split('_')[-1])
    await callback.message.edit_text(
        TEXTS[lang]['set_channel'].format(channel_num=channel_num),
        reply_markup=get_back_keyboard(channel_num, user_id)
    )
    await state.set_state(ChannelSetup.waiting_for_channel_id)
    await state.update_data(channel_num=channel_num)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("set_contract_"))
async def process_set_contract(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    channel_num = int(callback.data.split('_')[-1])
    can_action, remaining_time = can_perform_action(user_id, "contract")
    if not can_action:
        cursor.execute(f"SELECT channel{channel_num}_id, channel{channel_num}_contract FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        chat_id, contract = result if result else (None, None)
        text, keyboard = get_channel_menu(channel_num, chat_id, contract, user_id)
        await callback.message.edit_text(
            TEXTS[lang]['wait'].format(seconds=remaining_time, action="contract change" if lang == 'en' else "сменой контракта"),
            reply_markup=keyboard
        )
        await callback.answer()
        return
    await callback.message.edit_text(
        TEXTS[lang]['set_contract'].format(channel_num=channel_num),
        reply_markup=get_back_keyboard(channel_num, user_id)
    )
    await state.set_state(ChannelSetup.waiting_for_contract)
    await state.update_data(channel_num=channel_num)
    await callback.answer()

@dp.message(ChannelSetup.waiting_for_channel_id)
async def handle_channel_id(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    data = await state.get_data()
    channel_num = data.get('channel_num')
    lang = get_user_language(user_id)
    text = message.text.strip()
    if not re.match(r'^-100\d+$', text):
        await bot.send_message(chat_id=message.chat.id, text=TEXTS[lang]['invalid_channel_id'], reply_markup=get_back_keyboard(channel_num, user_id))
        return
    chat_id = int(text)
    try:
        bot_member = await bot.get_chat_member(chat_id, bot.id)
        if bot_member.status != "administrator":
            await bot.send_message(chat_id=message.chat.id, text=TEXTS[lang]['not_admin'], reply_markup=get_back_keyboard(channel_num, user_id))
            return
        cursor.execute(f"UPDATE users SET channel{channel_num}_id = ? WHERE user_id = ?", (chat_id, user_id))
        conn.commit()
        cursor.execute(f"SELECT channel{channel_num}_contract FROM users WHERE user_id = ?", (user_id,))
        contract = cursor.fetchone()[0] if cursor.fetchone() else None
        text, keyboard = get_channel_menu(channel_num, chat_id, contract, user_id)
        await bot.send_message(chat_id=message.chat.id, text=TEXTS[lang]['channel_set'].format(channel_num=channel_num, chat_id=chat_id), reply_markup=keyboard)
        await state.clear()
    except Exception as e:
        logger.error(f"Channel check error {chat_id}: {e}")
        await bot.send_message(chat_id=message.chat.id, text=TEXTS[lang]['channel_check_error'], reply_markup=get_back_keyboard(channel_num, user_id))

@dp.message(ChannelSetup.waiting_for_contract)
async def handle_contract(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = get_user_language(user_id)
    data = await state.get_data()
    channel_num = data.get('channel_num')
    contract = message.text.strip()
    if not re.match(r'^EQ[0-9A-Za-z\-_]{46}$', contract):
        text, keyboard = get_channel_menu(channel_num, None, user_id=user_id)
        await bot.send_message(chat_id=message.chat.id, text=TEXTS[lang]['invalid_contract'], reply_markup=keyboard)
        return
    cursor.execute(f"UPDATE users SET channel{channel_num}_contract = ? WHERE user_id = ?", (contract, user_id))
    conn.commit()
    last_contract_change_time[user_id] = time()
    cursor.execute(f"SELECT channel{channel_num}_id FROM users WHERE user_id = ?", (user_id,))
    chat_id = cursor.fetchone()[0] if cursor.fetchone() else None
    text, keyboard = get_channel_menu(channel_num, chat_id, contract, user_id)
    await bot.send_message(chat_id=message.chat.id, text=TEXTS[lang]['contract_set'].format(contract=contract), reply_markup=keyboard)
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith("delete_channel_"))
async def process_delete_channel(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    lang = get_user_language(user_id)
    channel_num = int(callback.data.split('_')[-1])
    from globals import tasks, previous_prices
    task_key = f"{user_id}_{channel_num}"
    if task_key in tasks:
        tasks[task_key].cancel()
        del tasks[task_key]
    if task_key in previous_prices:
        del previous_prices[task_key]
    cursor.execute(f"UPDATE users SET channel{channel_num}_id = NULL, channel{channel_num}_contract = NULL WHERE user_id = ?", (user_id,))
    conn.commit()
    text, keyboard = get_channel_menu(channel_num, None, user_id=user_id)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()