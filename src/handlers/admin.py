# admin.py
from aiogram import types
from bot_config import bot, dp, config
from database import cursor, conn

def is_admin(user_id):
    return str(user_id) == config['Settings']['admin_id']

@dp.message(lambda message: message.text.startswith("/whitelist ") and not message.text.startswith("/whitelist list"))
async def add_to_whitelist(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("вайтлистик :)")
        return
    try:
        target_id = int(message.text.split()[1])
        cursor.execute("INSERT OR IGNORE INTO whitelist (user_id) VALUES (?)", (target_id,))
        conn.commit()
        await message.answer(f"Юзер {target_id} добавлен")
    except (IndexError, ValueError):
        await message.answer("Используй: /whitelist <id>")

@dp.message(lambda message: message.text.startswith("/blacklist "))
async def add_to_blacklist(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("вайтлистик :(")
        return
    try:
        target_id = int(message.text.split()[1])
        cursor.execute("INSERT OR IGNORE INTO blacklist (user_id) VALUES (?)", (target_id,))
        conn.commit()
        await message.answer(f"User {target_id} added to blacklist")
    except (IndexError, ValueError):
        await message.answer("Используй: /blacklist <id>")

@dp.message(lambda message: message.text == "/list")
async def show_users_list(message: types.Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        await message.answer("вайт_лис_тик :>")
        return
    cursor.execute("SELECT user_id, channel1_id, channel2_id, channel3_id FROM users")
    all_users = cursor.fetchall()
    if not all_users:
        await message.answer("пусто")
        return
    text = "List of users:\n\n"
    for user_id, ch1, ch2, ch3 in all_users:
        try:
            user = await bot.get_chat(user_id)
            username = user.username or "No username"
        except:
            username = "Unknown"
        channels = [f"Channel {i}: {ch_id}" for i, ch_id in enumerate((ch1, ch2, ch3), 1) if ch_id]
        text += f"ID: {user_id}\nUsername: @{username}\nChannels: {', '.join(channels) or 'None'}\n\n"
    await message.answer(text)
