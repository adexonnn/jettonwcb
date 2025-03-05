# database.py
import sqlite3
import logging
import os
from bot_config import config, CONFIG_DIR

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(CONFIG_DIR, config['Bot']['db_path']) if not os.path.isabs(config['Bot']['db_path']) else config['Bot']['db_path']

def init_db():
    try:
        if not os.path.exists(DB_PATH):
            logger.warning(f"Database file {DB_PATH} does not exist, creating a new one.")
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        
        default_language = config['Settings']['default_language']
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            channel1_id INTEGER, channel2_id INTEGER, channel3_id INTEGER,
            channel1_contract TEXT, channel2_contract TEXT, channel3_contract TEXT,
            interval INTEGER, running INTEGER DEFAULT 0, language TEXT DEFAULT '{default_language}'
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS blacklist (
            user_id INTEGER PRIMARY KEY
        )''')
        
        conn.commit()
        logger.info(f"Connected to database at {DB_PATH}")
        return conn, cursor
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise

conn, cursor = init_db()
