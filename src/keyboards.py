# keyboards.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.messages import get_user_language, TEXTS
from src.database import cursor

def get_main_menu(user_id):
    lang = get_user_language(user_id)
    cursor.execute("SELECT channel1_id, channel2_id, channel3_id FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone() or (None, None, None)
    channel1, channel2, channel3 = row
    
    channel1_text = f"{channel1}" if channel1 else "1️⃣"
    channel2_text = f"{channel2}" if channel2 else "2️⃣"
    channel3_text = f"{channel3}" if channel3 else "3️⃣"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=channel1_text, callback_data="manage_channel_1")],
            [InlineKeyboardButton(text=channel2_text, callback_data="manage_channel_2")],
            [InlineKeyboardButton(text=channel3_text, callback_data="manage_channel_3")],
            [InlineKeyboardButton(text=TEXTS[lang]['set_interval_btn'], callback_data="set_interval")],
            [InlineKeyboardButton(text=TEXTS[lang]['start_all_btn'], callback_data="start_all"),
             InlineKeyboardButton(text=TEXTS[lang]['stop_all_btn'], callback_data="stop_all")],
            [InlineKeyboardButton(text=TEXTS[lang]['language_btn'], callback_data="switch_language"),
             InlineKeyboardButton(text=TEXTS[lang]['guide_btn'], url=TEXTS[lang]['guide_url'])]
        ]
    )
    return keyboard

def get_channel_menu(channel_num, chat_id, contract=None, user_id=None):
    lang = get_user_language(user_id) if user_id else 'ru'
    channel_button_text = f"{chat_id}" if chat_id else TEXTS[lang]['set_channel_btn']
    contract_button_text = f"{contract}" if contract else TEXTS[lang]['set_contract_btn']
    
    keyboard_buttons = [
        [InlineKeyboardButton(text=channel_button_text, callback_data=f"set_channel_{channel_num}")],
        [InlineKeyboardButton(text=contract_button_text, callback_data=f"set_contract_{channel_num}")],
        [InlineKeyboardButton(text=TEXTS[lang]['start_btn'], callback_data=f"start_{channel_num}"),
         InlineKeyboardButton(text=TEXTS[lang]['stop_btn'], callback_data=f"stop_{channel_num}")]
    ]
    
    if chat_id:
        keyboard_buttons.append([InlineKeyboardButton(text=TEXTS[lang]['delete_channel_btn'], callback_data=f"delete_channel_{channel_num}")])
    
    keyboard_buttons.append([InlineKeyboardButton(text=TEXTS[lang]['back_btn'], callback_data="back_to_main")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return TEXTS[lang]['channel_settings'].format(channel_num=channel_num), keyboard

def get_back_keyboard(channel_num, user_id=None):
    lang = get_user_language(user_id) if user_id else 'ru'
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=TEXTS[lang]['back_btn'], callback_data=f"back_to_channel_{channel_num}")]
        ]
    )

def get_interval_keyboard(user_id):
    lang = get_user_language(user_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1 min ⏳" if lang == 'en' else "1 мин ⏳", callback_data="interval_1"),
             InlineKeyboardButton(text="3 min ⏳" if lang == 'en' else "3 мин ⏳", callback_data="interval_3"),
             InlineKeyboardButton(text="10 min ⏳" if lang == 'en' else "10 мин ⏳", callback_data="interval_10")],
            [InlineKeyboardButton(text=TEXTS[lang]['back_btn'], callback_data="back_to_main")]
        ]
    )