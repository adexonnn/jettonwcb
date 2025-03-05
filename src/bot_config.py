# bot_config.py
import configparser
import os
import argparse
from aiogram import Bot, Dispatcher

parser = argparse.ArgumentParser(description="Telegram Token Price Bot")
parser.add_argument('--config', default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.ini'), help='Path to config.ini')
args = parser.parse_args()

config = configparser.ConfigParser()
CONFIG_PATH = args.config if 'BOT_CONFIG_PATH' not in os.environ else os.environ['BOT_CONFIG_PATH']

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Config file {CONFIG_PATH} not found")

config.read(CONFIG_PATH)
if 'Bot' not in config:
    raise ValueError(f"Section [Bot] missing in {CONFIG_PATH}. Check config.ini.")

BOT_TOKEN = config['Bot']['token']
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot=bot)

# Определяем CONFIG_DIR как директорию, где лежит config.ini
CONFIG_DIR = os.path.dirname(os.path.abspath(CONFIG_PATH))