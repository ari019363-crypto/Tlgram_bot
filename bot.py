"""
ربات کامل گروه تلگرام با شخصیت دوگانه
نوشته شده با python-telegram-bot
"""

import logging
import random
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

# ==================== تنظیمات ====================
TOKEN = "8912825405:AAG7X8SzmgoZmscmz0WzIQzSGyaqf0XR8A8"  # توکن ربات رو اینجا بذار
ADMIN_IDS = [7430881772]  # آیدی عددی ادمین‌ها رو اینجا بذار
DATABASE_PATH = "bot_data.db"

# ==================== متون ====================
WELCOME_MESSAGES = [
    "😊 به جمع ما خوش اومدی {name}! امیدوارم از اینجا لذت ببری... فعلاً!",
    "🎉 {name} وارد شد! الان دیگه گروه پر از انرژی مثبته (یا منفی؟!)",
    "🙃 اوهوم! {name} اومد! بذار ببینم چقدر دووم میاری اینجا!",
    "🌟 {name} جان! گروه ما یه نفر خاص کم داشت... حالا اومدی!",
    "🔥 {name}! مواظب باش من یه ربات با شخصیت دوگانه‌ام! 😈😇",
]

GOODBYE_MESSAGES = [
    "😢 {name} رفت... خب، به هر حال! زندگی ادامه داره!",
    "👋 {name}، امیدوارم پشیمون نباشی از رفتنت!",
    "😏 {name} رفت! بالاخره گروه یه نفره کم شد!",
]

BOT_JOIN_MESSAGES = [
    "🎉 سلام به همه! من ربات جدید گروه هستم!\nبرای دیدن دستورات /help رو بزنید.\n\n😈 یه نکته: من یه شخصیت دوگانه دارم!",
    "🤖 سلام! ربات جدید اومده به گروه!\n📚 دستورات: /help\n🎮 بازی: /game",
]

CLASSIC_ROASTS = [
    "{name}، میدونستی مغزت مثل اینترنت میمونه؟ همش قطع و وصله! 🤯",
    "{name}، اگه تنبلی یه المپیک داشت، تو طلا میگرفتی! 🥇",
    "{name}، سطح IQ گروه با اومدنت پایین اومد! 📉😂",
    "{name}، تو رو به خدا سکوت کن! داری به اعتبار گروه آسیب میزنی! 🤐",
]

PRO_ROASTS = [
    "{name}، اگه قرار باشه کسی رو تحسین کنم، آخرین نفر تو هستی! 🔥",
    "{name}، میدونی چرا هوا سرده؟ چون تو هستی! 🥶",
    "{name}، خدا بهت颜值 داد ولی یادش رفت مغز بده! 🤡",
]

FRIENDLY_ROASTS = [
    "{name} جان، شوخی میکنم ها! تو واقعاً عزیزی! ❤️",
    "{name}، این تیکه فقط برای خنده بود! 😊",
]

HELP_TEXT = """
📚 **راهنمای ربات گروه**

**دستورات عمومی:**
/mood - روحیه فعلی ربات
/mytitle - لقب من
/titles - لیست لقب‌ها
/stats - آمار من
/special - لقب ویژه (یک بار در روز)
/roast [نام] - تیکه پرانی
/game - بازی‌ها
/top - کاربران برتر

**دستورات ادمین:**
/warn @username - اخطار
/mute @username [دقیقه] - میوت
/unmute @username - رفع میوت
/set_mood happy|roast|evil|neutral - تغییر روحیه

**لقب‌ها:**
• ۰ پیام: تازه وارد
• ۵ پیام: تازه نفس
• ۲۰ پیام: فعال گروه
• ۵۰ پیام: قدیمی‌تر از خودم!
• ۱۰۰ پیام: افسانه گروه
• ۵۰۰ پیام: هم‌رتبه من!

**روحیه‌ها:**
😊 Happy - مهربون
😂 Roast - تیکه‌پراکن
😈 Evil - بدجنس
🤖 Neutral - بی‌طرف
"""

GAME_MENU = """
🎮 **بازی‌ها:**
/number - حدس عدد
/riddle - معما
/fact - حقیقت جالب
/joke - جوک
"""

RIDDLES = [
    {"question": "چیزی که هر چی بیشتر ازش برداری، بیشتر میشه؟", "answer": "گودال"},
    {"question": "کیست که بدون دست و پا، از کوه بالا میره؟", "answer": "ابر"},
    {"question": "چه چیزی همیشه میاد ولی هیچوقت نمیرسه؟", "answer": "فردا"},
]

FACTS = [
    "🐙 اختاپوس‌ها ۳ تا قلب دارن!",
    "🦒 زرافه‌ها ۷ مهره گردن دارن!",
    "🐧 پنگوئن‌ها می‌تونن تا ۱۵ دقیقه زیر آب بمونن!",
]

JOKES = [
    "یه روز یه تخته سیاه به تخته سفید گفت: چرا همیشه سیاهی؟ تخته سفید گفت: تو که جای منو گرفتی! 😂",
    "یه برنامه‌نویس به برنامه‌نویس دیگه گفت: زندگی‌ام پر از خطاست! گفت: دیباگ کن! 😅",
    "چرا کامپیوترها عاشق برفن؟ چون وقتی برف میاد، همه چیز white میشه! ❄️",
]

KEYWORD_RESPONSES = {
    "سلام": ["😊 سلام {name} جان! چه خبر؟", "👋 سلام! حالت چطوره؟"],
    "خداحافظ": ["👋 {name}، زود برگرد!", "😢 {name} رفت... خب!"],
    "ممنون": ["❤️ خواهش میکنم {name} جان!", "🌟 خوشحالم که راضی هستی!"],
}

MOOD_RESPONSES = {
    "happy": ["😊 امروز روز خوبیه {name}!", "🌟 {name} جان! انرژی مثبت!"],
    "roast": ["😂 {name}! آخه چرا اینقدر بامزه‌ای؟", "🔥 {name}، استعداد خرابکاری داری!"],
    "evil": ["😈 {name}... امروز حالم خوب نیست!", "💀 {name}، اگه پیام بفرسی جواب نمیدم!"],
    "neutral": ["🤖 {name}، پیامت رو خوندم!", "👍 {name}، اوکی!"],
}

# ==================== دیتابیس ====================
class Database:
    def __init__(self):
        self.init_db()
    
    def get_conn(self):
        return sqlite3.connect(DATABASE_PATH)
    
    def init_db(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                group_id INTEGER,
                username TEXT,
                first_name TEXT,
                join_date TEXT,
                message_count INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0,
                is_muted INTEGER DEFAULT 0,
                mute_until TEXT,
                current_title TEXT,
                UNIQUE(user_id, group_id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER UNIQUE,
                group_name TEXT,
                join_date TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username, first_name, group_id):
        conn = self.get_conn()
        c = conn.cursor()
        now = datetime.now().isoformat()
        
        c.execute("SELECT * FROM users WHERE user_id=? AND group_id=?", (user_id, group_id))
        user = c.fetchone()
        
        if user:
            c.execute('''UPDATE users SET username=?, first_name=?, last_active=?, 
                      message_count=message_count+1 WHERE user_id=? AND group_id=?''',
                      (username, first_name, now, user_id, group_id))
        else:
            c.execute('''INSERT INTO users (user_id, group_id, username, first_name, 
                      join_date, current_title) VALUES (?,?,?,?,?,?)''',
                      (user_id, group_id, username, first_name, now, "تازه وارد"))
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id, group_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id=? AND group_id=?", (user_id, group_id))
        user = c.fetchone()
        conn.close()
        if user:
            return {
                'user_id': user[1],
                'group_id': user[2],
                'username': user[3],
                'first_name': user[4],
                'message_count': user[7],
                'warning_count': user[8],
                'is_muted': bool(user[9]),
                'mute_until': user[10],
                'current_title': user[11]
            }
        return None
    
    def add_warning(self, user_id, group_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''UPDATE users SET warning_count = warning_count + 1 
                  WHERE user_id=? AND group_id=?''', (user_id, group_id))
        conn.commit()
        conn.close()
    
    def clear_warnings(self, user_id, group_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''UPDATE users SET warning_count = 0 
                  WHERE user_id=? AND group_id=?''', (user_id, group_id))
        conn.commit()
        conn.close()
    
    def mute_user(self, user_id, group_id, minutes=60):
        conn = self.get_conn()
        c = conn.cursor()
        mute_until = (datetime.now() + timedelta(minutes=minutes)).isoformat()
        c.execute('''UPDATE users SET is_muted=1, mute_until=? 
                  WHERE user_id=? AND group_id=?''', (mute_until, user_id, group_id))
        conn.commit()
        conn.close()
    
    def unmute_user(self, user_id, group_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''UPDATE users SET is_muted=0, mute_until=NULL 
                  WHERE user_id=? AND group_id=?''', (user_id, group_id))
        conn.commit()
        conn.close()
    
    def get_top_users(self, group_id, limit=10):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''SELECT first_name, message_count FROM users 
                  WHERE group_id=? ORDER BY message_count DESC LIMIT ?''', 
                  (group_id, limit))
        users = c.fetchall()
        conn.close()
        return [{'name': u[0], 'messages': u[1]} for u in users]
    
    def add_group(self, group_id, group_name):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM groups WHERE group_id=?", (group_id,))
        if not c.fetchone():
            c.execute("INSERT INTO groups (group_id, group_name, join_date) VALUES (?,?,?)",
                     (group_id, group_name, datetime.now().isoformat()))
        conn.commit()
        conn.close()

# ==================== مدیریت روحیه ====================
class MoodManager:
    def __init__(self):
        self.current_mood = "happy"
        self.last_change = datetime.now()
        self.moods = ["happy", "roast", "evil", "neutral"]
    
    def get_mood(self):
        if (datetime.now() - self.last_change).seconds > 1800:  # 30 دقیقه
            self.current_mood = random.choice(self.moods)
            self.last_change = datetime.now()
        return self.current_mood
    
    def set_mood(self, mood):
        if mood in self.moods:
            self.current_mood = mood
            self.last_change = datetime.now()
            return True
        return False

# ==================== مدیریت لقب ====================
class TitleManager:
    def __init__(self):
        self.titles = {
            0: "🍼 تازه وارد",
            5: "🌱 تازه نفس",
            20: "💪 فعال گروه",
            50: "👴 قدیمی‌تر از خودم!",
            100: "🏆 افسانه گروه",
            500: "⭐ هم‌رتبه من!",
        }
        self.special_titles = ["سلطان گروه 👑", "شوخی‌بردار 🤡", "استاد تیکه پرانی 🔥", 
                              "نابغه‌ی گروه 🧠", "افسانه‌ی زنده 🦄"]
    
    def get_title(self, count):
        title = "🍼 تازه وارد"
        for c, t in sorted(self.titles.items()):
            if count >= c:
                title = t
        return title
    
    def get_special(self):
        return random.choice(self.special_titles)

# ==================== مقداردهی ====================
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()
mood = MoodManager()
title_mgr = TitleManager()
game_sessions = {}

# ==================== دستورات ====================

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        f"🎉 سلام {update.effective_user.first_name} عزیز!\n\n"
        f"من ربات گروه هستم!\n"
        f"📋 دستورات: /help\n"
        f"🎮 بازی: /game\n"
        f"🏅 لقب: /mytitle"
    )

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(HELP_TEXT)

async def mood_command(update: Update, context: CallbackContext):
    m = mood.get_mood()
    emojis = {"happy": "😊", "roast": "😂", "evil": "😈", "neutral": "🤖"}
    await update.message.reply_text(f"{emojis.get(m, '🤖')} حالت فعلی: **{m}**", parse_mode='Markdown')

async def mytitle(update: Update, context: CallbackContext):
    user = update.effective_user
    db_user = db.get_user(user.id, update.effective_chat.id)
    if db_user:
        title = db_user['current_title'] or title_mgr.get_title(db_user['message_count'])
        await update.message.reply_text(f"🏷️ لقب شما: **{title}**\n📊 پیام‌ها: {db_user['message_count']}", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ هنوز ثبت نام نکردی! یه پیام بفرست.")

async def titles_list(update: Update, context: CallbackContext):
    text = "🏅 **لقب‌ها:**\n\n"
    for count, title in title_mgr.titles.items():
        text += f"• {title} - {count} پیام\n"
    text += f"\n✨ لقب‌های ویژه:\n• {title_mgr.get_special()}"
    await update.message.reply_text(text, parse_mode='Markdown')

async def special_title(update: Update, context: CallbackContext):
    user = update.effective_user
    today = datetime.now().date()
    
    if user.id in user_states and user_states[user.id].get('last_special') == today:
        await update.message.reply_text("❌ امروز قبلاً لقب ویژه گرفتی! فردا بیا.")
        return
    
    special = title_mgr.get_special()
    db_user = db.get_user(user.id, update.effective_chat.id)
    if db_user:
        conn = db.get_conn()
        c = conn.cursor()
        c.execute("UPDATE users SET current_title=? WHERE user_id=? AND group_id=?", 
                 (special, user.id, update.effective_chat.id))
        conn.commit()
        conn.close()
    
    user_states[user.id] = {'last_special': today}
    await update.message.reply_text(f"🎉 لقب ویژه‌ی شما: **{special}**", parse_mode='Markdown')

async def roast(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("🤔 به کی تیکه بندازم؟ مثال: /roast @username")
        return
    
    name = ' '.join(context.args).replace('@', '')
    m = mood.get_mood()
    
    if m == "roast":
        roast_text = random.choice(PRO_ROASTS + CLASSIC_ROASTS).format(name=name)
    elif m == "happy":
        roast_text = random.choice(FRIENDLY_ROASTS).format(name=name)
    else:
        roast_text = random.choice(CLASSIC_ROASTS).format(name=name)
    
    await update.message.reply_text(roast_text)

async def stats(update: Update, context: CallbackContext):
    user = update.effective_user
    db_user = db.get_user(user.id, update.effective_chat.id)
    if not db_user:
        await update.message.reply_text("❌ آماری ثبت نشده!")
        return
    
    await update.message.reply_text(
        f"📊 **آمار {db_user['first_name']}**\n"
        f"• پیام‌ها: {db_user['message_count']}\n"
        f"• اخطارها: {db_user['warning_count']}\n"
        f"• وضعیت: {'🔇 میوت' if db_user['is_muted'] else '✅ فعال'}\n"
        f"• لقب: {db_user['current_title']}",
        parse_mode='Markdown'
    )

async def top(update: Update, context: CallbackContext):
    users = db.get_top_users(update.effective_chat.id)
    if not users:
        await update.message.reply_text("❌ هنوز کاربری ثبت نشده!")
        return
    
    text = "🏆 **کاربران برتر:**\n\n"
    for i, u in enumerate(users[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        text += f"{medal} {u['name']} - {u['messages']} پیام\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def game(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🔢 حدس عدد", callback_data="game_number")],
        [InlineKeyboardButton("🧩 معما", callback_data="game_riddle")],
        [InlineKeyboardButton("💡 حقیقت", callback_data="game_fact")],
        [InlineKeyboardButton("😄 جوک", callback_data="game_joke")],
    ]
    await update.message.reply_text(GAME_MENU, reply_markup=InlineKeyboardMarkup(keyboard))

async def game_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data
    
    if data == "game_number":
        number = random.randint(1, 100)
        game_sessions[user.id] = {'type': 'number', 'number': number}
        await query.edit_message_text(f"🔢 یه عدد بین ۱ تا ۱۰۰ حدس بزن!")
    
    elif data == "game_riddle":
        riddle = random.choice(RIDDLES)
        game_sessions[user.id] = {'type': 'riddle', 'answer': riddle['answer']}
        await query.edit_message_text(f"🧩 معما:\n{riddle['question']}\n\nجواب رو بفرست!")
    
    elif data == "game_fact":
        await query.edit_message_text(f"💡 {random.choice(FACTS)}\n\nبرای حقیقت دیگه: /fact")
    
    elif data == "game_joke":
        await query.edit_message_text(f"😄 {random.choice(JOKES)}\n\nبرای جوک دیگه: /joke")

async def fact(update: Update, context: CallbackContext):
    await update.message.reply_text(f"💡 {random.choice(FACTS)}")

async def joke(update: Update, context: CallbackContext):
    await update.message.reply_text(f"😄 {random.choice(JOKES)}")

async def riddle(update: Update, context: CallbackContext):
    riddle = random.choice(RIDDLES)
    game_sessions[update.effective_user.id] = {'type': 'riddle', 'answer': riddle['answer']}
    await update.message.reply_text(f"🧩 معما:\n{riddle['question']}\n\nجواب رو بفرست!")

async def number_game(update: Update, context: CallbackContext):
    number = random.randint(1, 100)
    game_sessions[update.effective_user.id] = {'type': 'number', 'number': number}
    await update.message.reply_text(f"🔢 یه عدد بین ۱ تا ۱۰۰ حدس بزن!")

# ==================== دستورات ادمین ====================

async def warn(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ فقط ادمین!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ مثال: /warn @username")
        return
    
    username = context.args[0].replace('@', '')
    # اینجا باید کاربر رو پیدا کنی - ساده شده
    db.add_warning(123, update.effective_chat.id)  # نمونه
    await update.message.reply_text(f"⚠️ به {username} اخطار داده شد!")

async def mute(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ فقط ادمین!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ مثال: /mute @username 60")
        return
    
    username = context.args[0].replace('@', '')
    minutes = int(context.args[1]) if len(context.args) > 1 else 60
    
    db.mute_user(123, update.effective_chat.id, minutes)  # نمونه
    await update.message.reply_text(f"🔇 {username} به مدت {minutes} دقیقه میوت شد!")

async def unmute(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ فقط ادمین!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ مثال: /unmute @username")
        return
    
    username = context.args[0].replace('@', '')
    db.unmute_user(123, update.effective_chat.id)  # نمونه
    await update.message.reply_text(f"🔊 میوت {username} برداشته شد!")

async def set_mood(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ فقط ادمین!")
        return
    
    if not context.args or context.args[0] not in ["happy", "roast", "evil", "neutral"]:
        await update.message.reply_text("❌ حالت‌ها: happy, roast, evil, neutral")
        return
    
    mood.set_mood(context.args[0])
    await update.message.reply_text(f"✅ روحیه به {context.args[0]} تغییر کرد!")

# ==================== رویدادهای گروه ====================

async def group_join(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text(random.choice(BOT_JOIN_MESSAGES))
            db.add_group(update.effective_chat.id, update.effective_chat.title)
            return
        
        await update.message.reply_text(random.choice(WELCOME_MESSAGES).format(name=member.first_name))
        db.add_user(member.id, member.username or "unknown", member.first_name, update.effective_chat.id)

async def group_leave(update: Update, context: CallbackContext):
    if update.message.left_chat_member:
        user = update.message.left_chat_member
        await update.message.reply_text(random.choice(GOODBYE_MESSAGES).format(name=user.first_name))

# ==================== مدیریت پیام‌ها ====================

async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    text = update.message.text
    chat_id = update.effective_chat.id
    
    if not text or not user:
        return
    
    # ثبت کاربر
    db.add_user(user.id, user.username or "unknown", user.first_name, chat_id)
    db_user = db.get_user(user.id, chat_id)
    
    # بررسی میوت
    if db_user and db_user['is_muted']:
        if db_user['mute_until'] and datetime.now() < datetime.fromisoformat(db_user['mute_until']):
            await update.message.delete()
            await update.message.reply_text(f"🔇 {user.first_name} میوت هستی!")
            return
        else:
            db.unmute_user(user.id, chat_id)
    
    # بازی‌ها
    if user.id in game_sessions:
        game = game_sessions[user.id]
        
        if game['type'] == 'number':
            try:
                guess = int(text)
                if guess < game['number']:
                    await update.message.reply_text("🔽 برو بالا!")
                elif guess > game['number']:
                    await update.message.reply_text("🔼 برو پایین!")
                else:
                    await update.message.reply_text(f"🎉 آفرین! عدد {game['number']} بود!")
                    del game_sessions[user.id]
            except:
                await update.message.reply_text("❌ عدد بفرست!")
            return
        
        elif game['type'] == 'riddle':
            if text.lower() == game['answer'].lower():
                await update.message.reply_text(f"🎉 درست! جواب: {game['answer']}")
                del game_sessions[user.id]
            else:
                await update.message.reply_text("❌ نه! دوباره امتحان کن!")
            return
    
    # پاسخ به کلمات کلیدی
    for keyword, responses in KEYWORD_RESPONSES.items():
        if keyword in text:
            await update.message.reply_text(random.choice(responses).format(name=user.first_name))
            break
    
    # پاسخ بر اساس روحیه
    if random.random() < 0.1:  # ۱۰٪ شانس
        m = mood.get_mood()
        await update.message.reply_text(random.choice(MOOD_RESPONSES.get(m, MOOD_RESPONSES["neutral"])).format(name=user.first_name))
    
    # به‌روزرسانی لقب
    db_user = db.get_user(user.id, chat_id)
    if db_user:
        new_title = title_mgr.get_title(db_user['message_count'])
        if new_title != db_user['current_title']:
            conn = db.get_conn()
            c = conn.cursor()
            c.execute("UPDATE users SET current_title=? WHERE user_id=? AND group_id=?", 
                     (new_title, user.id, chat_id))
            conn.commit()
            conn.close()
            if db_user['message_count'] % 5 == 0:
                await update.message.reply_text(f"🎉 لقب شما به **{new_title}** تغییر کرد!", parse_mode='Markdown')

# ==================== توابع کمکی ====================

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ==================== اجرا ====================

def main():
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ توکن ربات رو در متغیر TOKEN قرار بدید!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("mood", mood_command))
    app.add_handler(CommandHandler("mytitle", mytitle))
    app.add_handler(CommandHandler("titles", titles_list))
    app.add_handler(CommandHandler("special", special_title))
    app.add_handler(CommandHandler("roast", roast))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("game", game))
    app.add_handler(CommandHandler("fact", fact))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("riddle", riddle))
    app.add_handler(CommandHandler("number", number_game))
    
    # دستورات ادمین
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("set_mood", set_mood))
    
    # کالبک
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^game_"))
    
    # رویدادها
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_join))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, group_leave))
    
    # پیام‌ها
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 ربات روشن شد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
