# states.py
from aiogram.fsm.state import State, StatesGroup

class ChannelSetup(StatesGroup):
    waiting_for_channel_id = State()
    waiting_for_contract = State()
    selecting_channel = State()