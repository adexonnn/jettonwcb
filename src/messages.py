# messages.py
from bot_config import config

TEXTS = {
    'ru': {
        'welcome': "📖 Добро пожаловать!\n\n🪄 <b>Выберите канал и установите ID</b>\n💰 <b>Установите контракт токена</b>\n⏳ <b>Установите интервал отправки</b>\n\n⚠️ Добавьте меня в каналы как администратора!",
        'price': "💰 Цена токена: {price_usd} USD₮ ≈ {price_rub} RUB\n💎 Цена в TON: {price_ton} TON\n⛽️ Капитализация: {fdv} USD₮",
        'price_with_change': "💰 Цена токена: {price_usd} USD₮ ≈ {price_rub} RUB\n💎 Цена в TON: {price_ton} TON\n⛽️ Капитализация: {fdv} USD₮\n\n⚙️ Изменение: {change}% {change_emoji}\n[Создать такого же бота](https://t.me/{bot_name})",
        'price_error': "Цена {token_name}: {price}",
        'set_channel': "📢 Введите ID для канала {channel_num}:",
        'set_contract': "💰 Введите контракт пары токена для канала {channel_num}:",
        'channel_settings': "Настройки канала {channel_num}:",
        'set_channel_btn': "📢 Установить канал",
        'set_contract_btn': "💰 Установить контракт",
        'start_btn': "🔋 Начать",
        'stop_btn': "🪫 Остановить",
        'delete_channel_btn': "🗑️ Удалить канал",
        'back_btn': "⬅️ Назад",
        'set_interval_btn': "⏱️ Установить интервал",
        'start_all_btn': "🔋 Запустить всех",
        'stop_all_btn': "🪫 Остановить всех",
        'language_btn': "🇷🇺 Язык",
        'guide_btn': "📚 Гайд",
        'guide_url': "https://telegra.ph/JettonWatcher-03-04",  # Можно изменить URL гайда
        'interval_prompt': "⏱️ Выберите интервал отправки сообщений:",
        'interval_set': "Интервал установлен: {minutes} мин",
        'wait': "⏳ Подождите {seconds} секунд перед {action}!",
        'invalid_contract': "Неверный формат контракта!",
        'contract_set': "Контракт установлен: {contract}",
        'invalid_channel_id': "Введите ID в формате -100..:",
        'not_admin': "Бот не является администратором канала!",
        'channel_check_error': "Не удалось проверить канал!",
        'channel_set': "Канал {channel_num} установлен: {chat_id}",
        'no_channels': "Нет установленных каналов или контрактов!",
        'started': "🛎 Бот запущен для канала {channel_num}",
        'stopped': "Успешно остановлен!",
        'all_started': "Все боты запущены",
        'all_stopped': "🛎 Все боты остановлены",
        'missing_setup': "Установите ID канала и контракт!"
    },
    'en': {
        'welcome': "📖 Welcome!\n\n🪄 <b>Select a channel and set its ID</b>\n💰 <b>Set the token contract</b>\n⏳ <b>Set the sending interval</b>\n\n⚠️ Add me to channels as an administrator!",
        'price': "💰 Price: {price_usd} USD₮\n💎 Price TON: {price_ton} TON\n⛽️ FDV: {fdv} USD₮",
        'price_with_change': "💰 Price: {price_usd} USD₮\n💎 Price TON: {price_ton} TON\n⛽️ FDV: {fdv} USD₮\n\n⚙️ Change: {change}% {change_emoji}\n[Create same bot](https://t.me/{bot_name})",
        'price_error': "Price of {token_name}: {price}",
        'set_channel': "📢 Enter ID for channel {channel_num}:",
        'set_contract': "💰 Enter token pair contract for channel {channel_num}:",
        'channel_settings': "Channel {channel_num} settings:",
        'set_channel_btn': "📢 Set channel",
        'set_contract_btn': "💰 Set contract",
        'start_btn': "🔋 Start",
        'stop_btn': "🪫 Stop",
        'delete_channel_btn': "🗑️ Delete channel",
        'back_btn': "⬅️ Back",
        'set_interval_btn': "⏱️ Set interval",
        'start_all_btn': "🔋 Start all",
        'stop_all_btn': "🪫 Stop all",
        'language_btn': "🇬🇧 Language",
        'guide_btn': "📚 Guide",
        'guide_url': "https://telegra.ph/JettonWatcher-EN-03-04",  # Можно изменить URL гайда
        'interval_prompt': "⏱️ Choose message sending interval:",
        'interval_set': "Interval set: {minutes} min",
        'wait': "⏳ Wait {seconds} seconds before {action}!",
        'invalid_contract': "Invalid contract format!",
        'contract_set': "Contract set: {contract}",
        'invalid_channel_id': "Enter ID in format -100..:",
        'not_admin': "Bot is not an administrator of the channel!",
        'channel_check_error': "Failed to check channel!",
        'channel_set': "Channel {channel_num} set: {chat_id}",
        'no_channels': "No channels or contracts set!",
        'started': "🛎 Bot started for channel {channel_num}",
        'stopped': "Successfully stopped!",
        'all_started': "All bots started",
        'all_stopped': "🛎 All bots stopped",
        'missing_setup': "Set channel ID and contract!"
    }
}

def get_user_language(user_id):
    from src.database import cursor, conn
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, language) VALUES (?, ?)", (user_id, config['Settings']['default_language']))
        conn.commit()
        return config['Settings']['default_language']
    return result[0] if result[0] is not None else config['Settings']['default_language']
