# utils.py
import aiohttp
import logging
import asyncio
from time import time
from bot_config import config, bot
from messages import get_user_language, TEXTS
from globals import tasks, previous_prices, last_action_time, last_contract_change_time
from database import cursor

logger = logging.getLogger(__name__)

def format_number(value):
    value = float(value)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    return f"{value:.8f}".rstrip('0').rstrip('.')

async def get_usd_rub_rate():
    url = config['API']['exchange_rate_api']
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['rates']['RUB']
                return 75 
        except Exception as e:
            logger.error(f"USD/RUB rate error: {e}")
            return 75

async def get_token_price(contract):
    url = f"{config['API']['dexscreener_api']}{contract}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, dict) and 'pairs' in data and data['pairs']:
                        pair = data['pairs'][0]
                        price_usd = pair.get('priceUsd', 'Недоступно')
                        price_ton = pair.get('priceNative', 'Недоступно')
                        fdv = pair.get('fdv', 'Недоступно')
                        token_name = pair.get('baseToken', {}).get('name', 'Неизвестная пара')
                        return price_usd, price_ton, fdv, token_name
                    return "Пара не найдена", "Недоступно", "Недоступно", "Неизвестная пара"
                return f"Ошибка API: {response.status}", "Недоступно", "Недоступно", "Неизвестная пара"
        except Exception as e:
            logger.error(f"Token price error: {e}")
            return "Ошибка", "Недоступно", "Недоступно", "Неизвестная пара"

async def send_message_loop(user_id: int, channel_num: int):
    lang = get_user_language(user_id)
    task_key = f"{user_id}_{channel_num}"
    usd_rub_rate = await get_usd_rub_rate()
    
    while True:
        try:
            cursor.execute(f"SELECT channel{channel_num}_id, channel{channel_num}_contract, interval, running FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if not row or not row[3]:
                break
            chat_id, contract, interval, _ = row
            if chat_id and contract:
                price_usd, price_ton, fdv, token_name = await get_token_price(contract)
                if price_usd in ["Ошибка", "Недоступно", "Пара не найдена", "Ошибка сети"]:
                    message_text = TEXTS[lang]['price_error'].format(token_name=token_name, price=price_usd)
                else:
                    price_usd_float = float(price_usd)
                    price_rub = price_usd_float * usd_rub_rate
                    
                    price_usd_formatted = format_number(price_usd_float)
                    price_rub_formatted = format_number(price_rub)
                    fdv_formatted = format_number(fdv) if fdv != "Недоступно" else "Недоступно"
                    
                    prev_price = previous_prices.get(task_key, None)
                    if prev_price and prev_price != "Недоступно":
                        change = ((price_usd_float - float(prev_price)) / float(prev_price)) * 100
                        change_emoji = "🟢" if change > 0 else "🔴" if change < 0 else ""
                        change_text = f"{change:.2f}" if change != 0 else "0.00"
                    else:
                        change_text = "0.00"
                        change_emoji = ""
                    
                    previous_prices[task_key] = price_usd
                    
                    message_text = TEXTS[lang]['price_with_change'].format(
                        bot_name=config['Bot']['bot_name'],
                        price_usd=price_usd_formatted,
                        price_rub=price_rub_formatted if lang == 'ru' else "",
                        price_ton=price_ton,
                        fdv=fdv_formatted,
                        change=change_text,
                        change_emoji=change_emoji
                    )
                
                await bot.send_message(chat_id=chat_id, text=message_text, parse_mode="Markdown")
            await asyncio.sleep(interval)
        except Exception as e:
            logger.error(f"Send message error for user {user_id}, channel {channel_num}: {e}")
            await asyncio.sleep(5)

def can_perform_action(user_id, action_type="start"):
    cooldown = int(config['Settings']['cooldown'])
    current_time = time()
    tracker = last_action_time if action_type == "start" else last_contract_change_time
    last_time = tracker.get(user_id, 0)
    if current_time - last_time < cooldown:
        return False, int(cooldown - (current_time - last_time))
    return True, 0

async def resume_tasks():
    cursor.execute("SELECT user_id, channel1_id, channel2_id, channel3_id, channel1_contract, channel2_contract, channel3_contract, running FROM users WHERE running = 1")
    active_users = cursor.fetchall()
    for user_id, ch1, ch2, ch3, cont1, cont2, cont3, _ in active_users:
        for i, (chat_id, contract) in enumerate(zip((ch1, ch2, ch3), (cont1, cont2, cont3)), 1):
            if chat_id and contract:
                tasks[f"{user_id}_{i}"] = asyncio.create_task(send_message_loop(user_id, i))
                logger.info(f"Resumed task for user_id {user_id}, channel {i}")
