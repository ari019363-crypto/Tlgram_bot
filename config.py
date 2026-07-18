import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # توکن ربات - از env یا مستقیم
    TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    
    # آیدی ادمین‌ها - از env یا مستقیم
    ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '123456789').split(',')]
    
    # تنظیمات دیتابیس
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'bot_data.db')
    
    # تنظیمات روحیه (دقیقه)
    MOOD_CHANGE_INTERVAL = int(os.getenv('MOOD_CHANGE_INTERVAL', '30'))
    DEFAULT_MOOD = os.getenv('DEFAULT_MOOD', 'happy')
    
    # تنظیمات میوت
    DEFAULT_MUTE_MINUTES = int(os.getenv('DEFAULT_MUTE_MINUTES', '60'))
    MAX_WARNS = int(os.getenv('MAX_WARNS', '3'))
    
    # لاگ
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
