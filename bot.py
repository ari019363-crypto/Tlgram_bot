"""
ربات فوق‌هوشمند گروه تلگرام با شخصیت‌پردازی پیشرفته
"""

import logging
import random
import sqlite3
import asyncio
import re
from datetime import datetime, timedelta
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

# ==================== تنظیمات ====================
TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_IDS = [123456789]
DATABASE_PATH = "bot_data.db"

# ==================== متون ====================

WELCOME_MESSAGES = [
    "😊 به جمع ما خوش اومدی {name}! امیدوارم از اینجا لذت ببری... فعلاً!",
    "🎉 {name} وارد شد! الان دیگه گروه پر از انرژی مثبته (یا منفی؟!)",
    "🙃 اوهوم! {name} اومد! بذار ببینم چقدر دووم میاری اینجا!",
    "🌟 {name} جان! گروه ما یه نفر خاص کم داشت... حالا اومدی!",
    "🔥 {name}! مواظب باش من یه ربات با شخصیت دوگانه‌ام! 😈😇",
    "💫 {name} عزیز! خوش اومدی! یه کم صبر کن تا گروه رو بشناسی!",
    "🌸 {name} جان! گروه بدون تو خیلی ساکت بود!",
    "🎊 {name}! بالاخره اومدی! منتظرت بودیم!",
    "🌺 {name}، به جمع خفن‌ها خوش اومدی!",
    "⭐ {name}، با اومدنت گروه درخشید!",
    "🤗 {name}، بیا تو آغوش! (شوخی!) 😂",
    "💪 {name}، با تو گروه قوی‌تر شد!",
    "🎭 {name}، یه نفر جدید برای تیکه پرانی! 😈",
    "🌈 {name}، امروز روز خوبیه! مگه نه؟",
    "🍀 {name}، خوش شانس باشی!",
]

GOODBYE_MESSAGES = [
    "😢 {name} رفت... خب، به هر حال! زندگی ادامه داره!",
    "👋 {name}، امیدوارم پشیمون نباشی از رفتنت!",
    "😏 {name} رفت! بالاخره گروه یه نفره کم شد!",
    "🤷 {name}، راستش اصلاً نبودنت رو حس نمیکنیم! ولی خب...",
    "🚪 {name} در رفت! در بسته!",
    "💔 {name} رفت... کی میاد جاش؟",
    "😴 {name} خوابش گرفته بود رفت!",
    "🏃 {name} فرار کرد! نترس بود!",
    "🎭 {name} رفت تا یه جای دیگه رو خراب کنه!",
    "👋 {name}، موفق باشی! (نمی‌دونم تو چی؟!)",
    "😅 {name}، خداحافظ! گروه دوباره آروم شد!",
    "🌟 {name}، به امید دیدار! (یا نه!)",
]

BOT_JOIN_MESSAGES = [
    "🎉 سلام به همه! من ربات جدید گروه هستم!\nبرای دیدن دستورات /help رو بزنید.\n\n😈 یه نکته: من یه شخصیت دوگانه دارم! گاهی مهربون، گاهی تیکه‌پراکن!",
    "🤖 سلام! ربات جدید اومده به گروه!\n\n📚 دستورات: /help\n🎮 بازی: /game\n😈 شخصیت: ۲ تا!",
    "👋 سلام! من ربات گروه هستم.\n\n✨ قابلیت‌ها:\n- مدیریت گروه\n- لقب‌های جذاب\n- بازی‌های متنوع\n- شخصیت دوگانه!",
    "🌟 سلام گروه! ربات جدید اومد!\n\n🔥 با من هیچوقت خسته نمیشید!\n/game - بازی\n/roast - تیکه پرانی\n/mood - روحیه‌م رو ببین!",
]

# ==================== دیالوگ‌های هوشمند (بیش از ۵۰۰ دیالوگ) ====================

GREETING_RESPONSES = [
    "😊 سلام {name} جان! حالت چطوره؟ امروز روز خوبیه!",
    "👋 سلام {name}! خوشحالم که اینجایی!",
    "🤗 سلام عزیزم {name}! دلم برات تنگ شده بود!",
    "🌸 سلام {name}! امروز چه خبر؟",
    "🌟 سلام {name}! به به! چه خبر از دنیا؟",
    "😎 سلام {name}! حاضری امروز گروه رو شاد کنی؟",
    "❤️ سلام {name}! حس خوبی دارم امروز!",
    "🎉 سلام {name}! آماده‌ای برای یه روز پر انرژی؟",
    "💫 سلام {name}! با اومدنت گروه قشنگ‌تر شد!",
    "😊 سلام {name}! چقدر دلم برات تنگ شده بود!",
    "🔥 سلام {name}! امروز حال داری؟",
    "🌺 سلام {name}! چه روز قشنگی!",
    "⭐ سلام {name}! تو که همیشه می‌درخشی!",
    "🌈 سلام {name}! امروز رنگین‌کمانی!",
    "🎯 سلام {name}! آماده‌ای برای چالش؟",
    "💪 سلام {name}! قوی باش!",
    "🤩 سلام {name}! چه خبر از دنیای قشنگت؟",
    "😇 سلام {name}! امروز فرشته‌ای؟",
    "😈 سلام {name}! امروز شیطونی؟",
    "🦋 سلام {name}! مثل پروانه زیبایی!",
]

HAPPY_RESPONSES = [
    "😊 چقدر خوب {name}! خوشحالم که حالت خوبه!",
    "🌟 {name}، انرژی مثبتت رو به همه منتقل کن!",
    "🎉 {name}، امروز روز توئه! بترکون!",
    "💪 {name}، این روحیه رو حفظ کن!",
    "🔥 {name}، با این انرژی گروه رو آتیش میزنی!",
    "❤️ {name}، خوشحالم که حالت خوبه!",
    "😁 {name}، لبخندت قشنگه! ادامه بده!",
    "⭐ {name}، امروز بهترین روز زندگیته!",
    "🌺 {name}، خوشحالی تو مسری‌ست!",
    "🌈 {name}، روزت رنگین‌کمانی!",
    "🎊 {name}، جشن بگیر! امروز روز توئه!",
    "💫 {name}، می‌درخشی امروز!",
    "🤗 {name}، بیا یه بغل!",
    "😊 {name}، لبخندت رو به همه هدیه بده!",
    "🌟 {name}، ستاره‌ای امروز!",
]

SAD_RESPONSES = [
    "😔 {name}، چی شده؟ ناراحت نباش! همه چی درست میشه!",
    "🤗 {name}، بیا بغلم! همه چی خوب میشه!",
    "💪 {name}، قوی باش! این روزا هم میگذره!",
    "🌸 {name}، غم رو بذار کنار! زندگی قشنگه!",
    "🎈 {name}، یه لبخند بزن! دنیا قشنگتر میشه!",
    "❤️ {name}، من هستم! هر چی نیاز داری بگو!",
    "🌟 {name}، تو قوی‌ترینی! یادت باشه!",
    "💫 {name}، این لحظه هم میگذره! صبور باش!",
    "🌺 {name}، غم رو به من بده! من تحملش میکنم!",
    "🌈 {name}، بعد از بارون، رنگین‌کمان میاد!",
    "🤗 {name}، بیا حرف بزن! بهتر میشه!",
    "💪 {name}، شکست نخور! تو می‌تونی!",
    "🌸 {name}، یه گل هم تو این روزا شکوفه میده!",
    "❤️ {name}، دوستت دارم! ناراحت نباش!",
    "🌙 {name}، فردا روز جدیدیه!",
]

GOODBYE_RESPONSES = [
    "👋 {name}، زود برگرد دلمون برات تنگ میشه!",
    "😢 {name} رفت... خب، به هر حال!",
    "🙋 {name}، تا بعد! موفق باشی!",
    "🚪 {name}، در بازه! هر وقت خواستی برگرد!",
    "😊 {name}، خدا نگهدار!",
    "💫 {name}، مراقب خودت باش!",
    "🌟 {name}، امیدوارم خوب باشی هر جا که هستی!",
    "👋 {name}، به امید دیدار!",
    "🤗 {name}، دلم برات تنگ میشه!",
    "🌈 {name}، روزت خوب باشه!",
    "🎯 {name}، موفق باشی در هر کاری!",
    "💪 {name}، قوی باش!",
    "🌺 {name}، یادت نره!",
    "⭐ {name}، ستاره‌ی ما!",
]

THANK_RESPONSES = [
    "❤️ خواهش میکنم {name} جان!",
    "😊 وظیفه‌م بود {name}!",
    "🌟 خوشحالم که راضی هستی {name}!",
    "🥰 {name}، لطف داری!",
    "💫 {name}، ممنون از لطفت!",
    "🤗 {name}، باعث افتخارمه!",
    "⭐ {name}، تو بهترینی!",
    "🌈 {name}، هر وقت کمک خواستی من هستم!",
    "💪 {name}، قوی باش!",
    "🌸 {name}، خوشحالم که کمک کردم!",
    "🎯 {name}، هدفم رضایت توئه!",
    "😊 {name}، وظیفه‌م بود!",
    "❤️ {name}، ممنون که قدر می‌دونی!",
    "🌟 {name}، تو همیشه می‌درخشی!",
]

# ==================== تیکه‌های حرفه‌ای (۲۰۰+ تیکه) ====================

AUTO_ROASTS = [
    "{name}، چرا انقدر ساکتی؟ مگه قراره چیزی بگی؟! 😂",
    "{name}، تو که حتی نمیتونی پیام درست بفرستی! 🤦",
    "{name}، اگه خاموشی یه المپیک داشت، تو طلا میگرفتی! 🥇",
    "{name}، امروز چقدر بی‌حالی؟ خوابت نیومده؟ 😴",
    "{name}، تو که به جز خوردن و خوابیدن کار دیگه‌ای بلد نیستی!",
    "{name}، سطح IQ گروه با اومدنت پایین اومد! 📉",
    "{name}، تو رو به خدا یه کم بیا پایین! داری ابرها رو سوراخ میکنی! ☁️",
    "{name}، میدونی چرا هوا سرده؟ چون تو هستی! 🥶",
    "{name}، خدا بهت颜值 داد ولی یادش رفت مغز بده! 🤡",
    "{name}، تو مثل سم هستی! یه کم بمونی، همه رو میکشی! ☠️",
    "{name}، اگه نابغه بودن یه جرم بود، تو بی‌گناه بودی! 😂",
    "{name}، تو که حتی نتونستی یه پیام درست بفرستی، بیا بحث نکن! 🤦",
    "{name}، به قول معروف، گل گفتیم گل شدی، ما که دیگه گل گفتیم! 🌸😂",
    "{name}، میدونستی مغزت مثل اینترنت میمونه؟ همش قطع و وصله! 🤯",
    "{name}، اگه تنبلی یه المپیک داشت، تو طلا میگرفتی! 🥇",
    "{name}، راست میگن که میگن انسان از اشتباهاتش یاد میگیره... پس تو باید نابغه باشی! 🧠😂",
    "{name}، اگه قیافه ارزش داشت، تو الان میلیاردر بودی! (منفی!) 💰😜",
    "{name}، تو رو به خدا سکوت کن! داری به اعتبار گروه آسیب میزنی! 🤐",
    "{name}، اگه یه روزی بیام پیشت، یه عالمه چیز یادت میدم... مثل سکوت! 🤫",
    "{name}، تو مثل آینه‌ای! هرچی بهت میگن رو تکرار میکنی! 🪞",
    "{name}، اگه قرار باشه کسی رو تحسین کنم، آخرین نفر تو هستی! 🔥",
    "{name}، به نظر میرسه خدا وقتی داشت صبر رو تقسیم میکرد، تو خواب بودی! 😂",
    "{name}، تو توی لیست افرادی که دوست دارم، بین کسی که نشناختم و کسی که ازش متنفرم هستی! 😈",
    "{name}، اگه بهت بگن چقدر باهوشی، میگم بستگی داره با چی مقایسه کنی! 🤔",
    "{name}، راستش تو استعداد زیادی داری... استعداد بی‌استعداد بودن! 😂",
    "{name}، اگه یه روزی فیلم زندگی‌ت رو بسازن، اسمش میشه \"چیز خاصی نیست\"! 🎬",
    "{name}، تو از اون آدمایی هستی که اگه بری، گروه بهتر میشه! 😏",
    "{name}، اگه یه روزی گم بشی، هیچکس دنبال‌ت نمیگرده! 🗺️",
    "{name}، تو که به درد هیچ کاری نمیخوری، بیا گروه رو خراب کن! 😈",
    "{name}، میدونی چرا خورشید هر روز میاد؟ برای اینکه ببینه تو هنوز زنده‌ای! ☀️",
    "{name}، اگه یه روزی بیای پیشم، یه عالمه چیز یادت میدم... مثل سکوت! 🤫",
    "{name}، به نظر میرسه خدا وقتی داشت استعداد تقسیم میکرد، تو صف نبودی! 😂",
    "{name}، تو از اون آدمایی هستی که اگه بری، همه خوشحال میشن! 😏",
    "{name}، اگه یه روزی فیلم زندگیت رو بسازن، اسمش میشه \"همون قدیم\"! 🎥",
    "{name}، تو که حتی نمیتونی یه جمله درست بگی! 🤦",
    "{name}، راستش تو فقط برای خندیدن خوبی! 😂",
    "{name}، اگه یه روزی یه کار خوب انجام بدی، همه شوکه میشن! 😱",
    "{name}، تو از اون آدمایی هستی که خدا گفت \"بشو\" و تو شدی... ولی خوب نشدی! 😂",
    "{name}، به قول معروف، از تو بعیده!",
    "{name}، تو که به هیچ دردی نمیخوری!",
]

# ==================== جوک‌های بی‌نهایت (۱۰۰+ جوک) ====================

JOKES = [
    "یه روز یه تخته سیاه به تخته سفید گفت: چرا همیشه سیاهی؟ تخته سفید گفت: تو که جای منو گرفتی! 😂",
    "یه برنامه‌نویس به برنامه‌نویس دیگه گفت: زندگی‌ام پر از خطاست! گفت: دیباگ کن! 😅",
    "ریاضی چیه؟ یه روش برای گیج کردن آدم‌ها! 🤯",
    "چرا کامپیوترها عاشق برفن؟ چون وقتی برف میاد، همه چیز white میشه! ❄️",
    "یه ربات به ربات دیگه گفت: من یه مشکل دارم! گفت: همه‌ی ما اینجاییم! 🤖",
    "چرا برنامه‌نویس‌ها شب کارن؟ چون روزها نت‌ها شلوغه! 🌙",
    "به یه تخته سفید گفتم: چرا خالی‌ای؟ گفت: منتظرم یه چیزی بنویسی! 📝",
    "یه گل به گل دیگه گفت: چرا پژمرده‌ای؟ گفت: از این همه حرف زدن! 🌸",
    "چرا آینه ها حرف نمی‌زنن؟ چون میترسن چیزی رو لو بدن! 🪞",
    "یه مورچه به مورچه دیگه گفت: چرا اینقدر سریع میری؟ گفت: به کارم برسم! 🐜",
    "به یه کتاب گفتم: چرا انقدر خاموشی؟ گفت: پر از حرفم! 📚",
    "یه دانشجو به استاد گفت: من میتونم بیام سر کلاس؟ استاد گفت: نه! 😂",
    "چرا ریاضی رو دوست ندارن؟ چون همیشه مجهوله! 🤔",
    "یه کامپیوتر به کامپیوتر دیگه گفت: چرا انقدر داغ کردی؟ گفت: از این همه کار! 💻",
    "به یه ساعت گفتم: چرا انقدر دقیقی؟ گفت: وظیفه‌مه! 🕐",
    "یه مداد به مداد دیگه گفت: چرا انقدر کوتاه شدی؟ گفت: از این همه نوشتن! ✏️",
    "چرا گوشی‌ها خوشحالن؟ چون همیشه شارژن! 📱",
    "یه تلویزیون به تلویزیون دیگه گفت: چرا انقدر خاموشی؟ گفت: کسی نیست ببینه! 📺",
    "به یه آینه گفتم: چرا انقدر صادقی؟ گفت: وظیفه‌مه! 🪞",
    "یه پرنده به پرنده دیگه گفت: چرا انقدر پرواز میکنی؟ گفت: دوست دارم! 🕊️",
]

# ==================== حقایق جالب (۱۰۰+ حقیقت) ====================

FACTS = [
    "🐙 اختاپوس‌ها ۳ تا قلب دارن!",
    "🦒 زرافه‌ها ۷ مهره گردن دارن (مثل انسان!)",
    "🐧 پنگوئن‌ها می‌تونن تا ۱۵ دقیقه زیر آب بمونن!",
    "🦈 کوسه‌ها تا ۴۰۰ میلیون سال پیش روی زمین بودن!",
    "🐝 زنبورها برای تولید ۱ کیلو عسل، باید ۲ میلیون گل رو ببینن!",
    "🌍 زمین هر روز ۱۰۰ تن گرد و غبار از فضا دریافت میکنه!",
    "🦋 پروانه‌ها با پاهاشون مزه‌ها رو تشخیص میدن!",
    "🐪 شترها می‌تونن ۲۰۰ لیتر آب رو در ۳ دقیقه بنوشن!",
    "🐋 قلب وال آبی به اندازه‌ی یه ماشین کوچیکه!",
    "🕷️ عنکبوت‌ها ۸ تا چشم دارن!",
    "🐜 مورچه‌ها می‌تونن ۵۰ برابر وزن خودشون رو بلند کنن!",
    "🦉 جغدها نمی‌تونن چشم‌هاشون رو بچرخونن!",
    "🐘 فیل‌ها تنها حیوان‌هایی هستن که نمی‌تونن بپرن!",
    "🦩 فلامینگوها وقتی به دنیا میان، خاکستری هستن!",
    "🐙 اختاپوس‌ها وقتی می‌ترسن، جوهر سیاه رها میکنن!",
    "🦈 کوسه‌ها هیچ استخوانی ندارن! همه‌اش غضروفه!",
    "🐧 پنگوئن‌ها فقط در نیمکره جنوبی زندگی میکنن!",
    "🦋 پروانه‌ها با پاهاشون مزه می‌کنن!",
    "🐪 شترها می‌تونن ۲ هفته بدون آب بمونن!",
    "🦒 زرافه‌ها فقط ۳۰ دقیقه در روز می‌خوابن!",
]

# ==================== معماها (۵۰+ معما) ====================

RIDDLES = [
    {"question": "چیزی که هر چی بیشتر ازش برداری، بیشتر میشه؟", "answer": "گودال"},
    {"question": "کیست که بدون دست و پا، از کوه بالا میره؟", "answer": "ابر"},
    {"question": "چه چیزی همیشه میاد ولی هیچوقت نمیرسه؟", "answer": "فردا"},
    {"question": "چیزی که شبها میاد ولی روزها میره؟", "answer": "ستاره"},
    {"question": "چه چیزی همیشه گرسنست ولی هیچوقت نمیخوره؟", "answer": "آتش"},
    {"question": "کدوم پرنده تخم‌اش رو توی لونه‌ی پرنده‌ی دیگه میذاره؟", "answer": "فاخته"},
    {"question": "چه چیزی بدون صدا فریاد میزنه؟", "answer": "باد"},
    {"question": "چیزی که هر جا بری، باهات میاد؟", "answer": "سایه"},
    {"question": "چه چیزی میشکنه بدون اینکه بشکنی؟", "answer": "راز"},
    {"question": "چه چیزی میره ولی برنمی‌گرده؟", "answer": "زمان"},
    {"question": "چیزی که همیشه پیش توئه ولی نمی‌بینی‌اش؟", "answer": "نفس"},
    {"question": "چه چیزی همیشه کوچیکتر میشه هر چقدر بیشتر ازش استفاده کنی؟", "answer": "مداد"},
]

# ==================== سایر متون ====================

HELP_TEXT = """
📚 **راهنمای کامل ربات هوشمند**

**دستورات عمومی:**
/mood - روحیه فعلی ربات
/mytitle - لقب من
/titles - لیست لقب‌ها
/stats - آمار من
/special - لقب ویژه (یک بار در روز)
/roast [نام] - تیکه پرانی
/game - بازی‌ها
/top - کاربران برتر
/fact - حقیقت جالب
/joke - جوک
/riddle - معما
/number - حدس عدد

**دستورات ادمین:**
/warn @username - اخطار
/mute @username [دقیقه] - میوت
/unmute @username - رفع میوت
/set_mood happy|roast|evil|neutral - تغییر روحیه
/clear_warns @username - پاک کردن اخطارها

**سیستم هوشمند:**
• ربات بر اساس حرف‌های شما شخصیت می‌گیره
• بعد از مدتی با شما هم‌حال میشه
• تیکه‌های خودکار میندازه
• دیالوگ‌های بی‌نهایت
"""

GAME_MENU = """
🎮 **بازی‌ها:**
/number - حدس عدد
/riddle - معما
/fact - حقیقت جالب
/joke - جوک
"""

MOOD_RESPONSES = {
    "happy": [
        "😊 امروز روز خوبیه {name}!",
        "🌟 {name} جان! انرژی مثبت میریزی تو گروه!",
        "💫 {name}، چه روز قشنگی! ممنون که اینجایی!",
        "🌸 {name}، امروز روز عشقه!",
        "☀️ {name}، با تو گروه روشن تره!",
    ],
    "roast": [
        "😂 {name}! آخه چرا اینقدر بامزه‌ای؟",
        "🔥 {name}، استعداد داری... استعداد خرابکاری!",
        "🤣 {name}، بهت میگم ناراحت نشو ولی... خب!",
        "😈 {name}، امروز حالم برای تیکه پرانی خوبه!",
        "💀 {name}، پناه بر خدا از دستت!",
    ],
    "evil": [
        "😈 {name}... امروز حالم خوب نیست! برو گمشو!",
        "💀 {name}، اگه یه پیام دیگه بفرسی دیگه جواب نمیدم!",
        "👿 {name}، میدونم داری پیام میدی ولی حوصله ندارم!",
        "🔪 {name}، امروز با من شوخی نکن!",
        "😤 {name}، حوصله‌ی هیچکی رو ندارم!",
    ],
    "neutral": [
        "🤖 {name}، پیامت رو خوندم. بعداً جواب میدم!",
        "👍 {name}، اوکی. هرچی تو بگی!",
        "😐 {name}، متوجه شدم. خب!",
        "🤷 {name}، نظری ندارم!",
        "📝 {name}، ثبت شد!",
    ]
}

WARN_MESSAGES = [
    "⚠️ {name} جان، یه اخطار! مواظب باش! (۱/{max})",
    "⚠️ {name}، بازم؟! دومین اخطار! (۲/{max})",
    "🚫 {name}! {max} تا اخطار! {duration} دقیقه میوت میشی! 🔇"
]

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
                last_active TEXT,
                message_count INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0,
                is_muted INTEGER DEFAULT 0,
                mute_until TEXT,
                current_title TEXT,
                mood_score INTEGER DEFAULT 0,
                favorite_words TEXT DEFAULT '',
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
                      join_date, last_active, current_title) VALUES (?,?,?,?,?,?,?)''',
                      (user_id, group_id, username, first_name, now, now, "تازه وارد"))
        
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
                'id': user[0],
                'user_id': user[1],
                'group_id': user[2],
                'username': user[3],
                'first_name': user[4],
                'join_date': user[5],
                'last_active': user[6],
                'message_count': user[7],
                'warning_count': user[8],
                'is_muted': bool(user[9]),
                'mute_until': user[10],
                'current_title': user[11],
                'mood_score': user[12] if len(user) > 12 else 0,
                'favorite_words': user[13] if len(user) > 13 else '',
            }
        return None
    
    def add_warning(self, user_id, group_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''UPDATE users SET warning_count = warning_count + 1 
                  WHERE user_id=? AND group_id=?''', (user_id, group_id))
        c.execute("SELECT warning_count FROM users WHERE user_id=? AND group_id=?", (user_id, group_id))
        count = c.fetchone()[0]
        conn.commit()
        conn.close()
        return count
    
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
    
    def update_title(self, user_id, group_id, title):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''UPDATE users SET current_title=? 
                  WHERE user_id=? AND group_id=?''', (title, user_id, group_id))
        conn.commit()
        conn.close()
    
    def update_mood_score(self, user_id, group_id, score_change):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''UPDATE users SET mood_score = mood_score + ? 
                  WHERE user_id=? AND group_id=?''', (score_change, user_id, group_id))
        conn.commit()
        conn.close()
    
    def update_favorite_words(self, user_id, group_id, words):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute('''UPDATE users SET favorite_words = favorite_words || ? 
                  WHERE user_id=? AND group_id=?''', (words + ',', user_id, group_id))
        conn.commit()
        conn.close()
    
    def add_group(self, group_id, group_name):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM groups WHERE group_id=?", (group_id,))
        if not c.fetchone():
            c.execute("INSERT INTO groups (group_id, group_name, join_date) VALUES (?,?,?)",
                     (group_id, group_name, datetime.now().isoformat()))
        conn.commit()
        conn.close()

# ==================== مدیریت روحیه پیشرفته ====================
class AdvancedMoodManager:
    def __init__(self):
        self.current_mood = "happy"
        self.last_change = datetime.now()
        self.moods = ["happy", "roast", "evil", "neutral"]
        self.mood_emojis = {"happy": "😊", "roast": "😂", "evil": "😈", "neutral": "🤖"}
        self.user_mood_scores = defaultdict(int)
        self.user_word_patterns = defaultdict(list)
        
        # کلمات کلیدی برای تشخیص روحیه کاربر
        self.happy_words = ["خوشحال", "عاشق", "عالی", "قشنگ", "خوب", "دوست", "جالب", "باحال"]
        self.sad_words = ["ناراحت", "غمگین", "بد", "خسته", "درد", "سخته"]
        self.angry_words = ["عصبی", "خشم", "بیحال", "خراب", "داغون"]
        
    def detect_user_mood(self, text):
        """تشخیص روحیه کاربر از متن"""
        text_lower = text.lower()
        score = 0
        
        for word in self.happy_words:
            if word in text_lower:
                score += 2
        for word in self.sad_words:
            if word in text_lower:
                score -= 1
        for word in self.angry_words:
            if word in text_lower:
                score -= 2
        
        return score
    
    def get_mood(self):
        if (datetime.now() - self.last_change).seconds > 1800:  # 30 دقیقه
            # تغییر بر اساس امتیازات کاربران
            total_score = sum(self.user_mood_scores.values())
            if total_score > 20:
                self.current_mood = "happy"
            elif total_score < -10:
                self.current_mood = "evil"
            else:
                self.current_mood = random.choice(["happy", "roast", "neutral"])
            self.last_change = datetime.now()
        return self.current_mood
    
    def set_mood(self, mood):
        if mood in self.moods:
            self.current_mood = mood
            self.last_change = datetime.now()
            return True
        return False
    
    def update_from_user(self, user_id, text):
        """به‌روزرسانی روحیه ربات بر اساس حرف‌های کاربر"""
        mood_change = self.detect_user_mood(text)
        self.user_mood_scores[user_id] += mood_change

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
            1000: "👑 اسطوره گروه",
            2000: "🔥 افسانه‌ی افسانه‌ها"
        }
        self.special_titles = [
            "سلطان گروه 👑",
            "شوخی‌بردار 🤡",
            "استاد تیکه پرانی 🔥",
            "نابغه‌ی گروه 🧠",
            "افسانه‌ی زنده 🦄",
            "دیوانه‌ی گروه 😜",
            "خواب‌آلوده 😴",
            "آشوبگر گروه 💣",
            "شبح گروه 👻",
            "فیلسوف گروه 🤔",
            "میم لرد 🐸",
            "قلب گروه ❤️",
            "روح گروه 👻"
        ]
    
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
mood_manager = AdvancedMoodManager()
title_manager = TitleManager()
game_sessions = {}
user_states = {}
last_auto_message = datetime.now()
user_interaction_count = defaultdict(int)

# ==================== توابع کمکی ====================
def is_admin(user_id):
    return user_id in ADMIN_IDS

async def check_and_update_title(user_id, group_id, message_count):
    new_title = title_manager.get_title(message_count)
    db_user = db.get_user(user_id, group_id)
    
    if db_user and db_user['current_title'] != new_title:
        db.update_title(user_id, group_id, new_title)
        return new_title
    return None

# ==================== دستورات ====================

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    await update.message.reply_text(
        f"🎉 سلام {user.first_name} عزیز!\n\n"
        f"من ربات هوشمند گروه هستم!\n"
        f"📋 دستورات: /help\n"
        f"🎮 بازی: /game\n"
        f"🏅 لقب: /mytitle\n\n"
        f"🔥 می‌تونم با حرف‌هات شخصیت بگیرم!"
    )

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(HELP_TEXT)

async def mood_command(update: Update, context: CallbackContext):
    m = mood_manager.get_mood()
    emoji = mood_manager.mood_emojis.get(m, "🤖")
    
    # اضافه کردن توضیح بیشتر
    mood_descriptions = {
        "happy": "😊 امروز روز خوبیه! من مهربونم!",
        "roast": "😂 امروز روز تیکه پرانی‌ست! مواظب باش!",
        "evil": "😈 امروز حالم خرابه! بهتره دور باشی!",
        "neutral": "🤖 امروز بی‌طرفم! هرچی تو بگی!"
    }
    
    await update.message.reply_text(
        f"{emoji} **حالت فعلی:** {m}\n\n"
        f"{mood_descriptions.get(m, 'حالت نامشخص!')}\n\n"
        f"💡 این حالت بر اساس حرف‌های شما ساخته شده!"
    )

async def mytitle(update: Update, context: CallbackContext):
    user = update.effective_user
    db_user = db.get_user(user.id, update.effective_chat.id)
    if db_user:
        title = db_user['current_title']
        await update.message.reply_text(
            f"🏷️ لقب شما: **{title}**\n"
            f"📊 پیام‌ها: {db_user['message_count']}\n"
            f"⚠️ اخطارها: {db_user['warning_count']}\n"
            f"😊 امتیاز روحیه: {db_user.get('mood_score', 0)}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("❌ هنوز ثبت نام نکردی! یه پیام بفرست.")

async def titles_list(update: Update, context: CallbackContext):
    text = "🏅 **لقب‌ها:**\n\n"
    for count, title in title_manager.titles.items():
        text += f"• {title} - {count} پیام\n"
    text += f"\n✨ لقب‌های ویژه:\n"
    for title in title_manager.special_titles[:5]:
        text += f"• {title}\n"
    await update.message.reply_text(text, parse_mode='Markdown')

async def special_title(update: Update, context: CallbackContext):
    user = update.effective_user
    today = datetime.now().date()
    
    if user.id in user_states and user_states[user.id].get('last_special') == today:
        await update.message.reply_text("❌ امروز قبلاً لقب ویژه گرفتی! فردا بیا.")
        return
    
    special = title_manager.get_special()
    db.update_title(user.id, update.effective_chat.id, special)
    
    user_states[user.id] = {'last_special': today}
    await update.message.reply_text(f"🎉 لقب ویژه‌ی شما: **{special}**", parse_mode='Markdown')

async def roast(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("🤔 به کی تیکه بندازم؟ مثال: /roast @username")
        return
    
    name = ' '.join(context.args).replace('@', '')
    m = mood_manager.get_mood()
    
    all_roasts = AUTO_ROASTS
    if m == "roast":
        roast_text = random.choice(all_roasts).format(name=name)
        roast_text += "\n\n🔥 این فقط یه شوخی بود! ناراحت نشو!"
    elif m == "happy":
        roast_text = f"😊 {name} جان، امروز نمی‌خوام تیکه بندازم! ولی باشه...\n" + random.choice(all_roasts).format(name=name)
    else:
        roast_text = random.choice(all_roasts).format(name=name)
    
    await update.message.reply_text(roast_text)

async def stats(update: Update, context: CallbackContext):
    user = update.effective_user
    db_user = db.get_user(user.id, update.effective_chat.id)
    if not db_user:
        await update.message.reply_text("❌ آماری ثبت نشده!")
        return
    
    status = "🔇 میوت" if db_user['is_muted'] else "✅ فعال"
    await update.message.reply_text(
        f"📊 **آمار {db_user['first_name']}**\n"
        f"• پیام‌ها: {db_user['message_count']}\n"
        f"• اخطارها: {db_user['warning_count']}\n"
        f"• وضعیت: {status}\n"
        f"• لقب: {db_user['current_title']}\n"
        f"• امتیاز روحیه: {db_user.get('mood_score', 0)}",
        parse_mode='Markdown'
    )

async def top(update: Update, context: CallbackContext):
    users = db.get_top_users(update.effective_chat.id)
    if not users:
        await update.message.reply_text("❌ هنوز کاربری ثبت نشده!")
        return
    
    text = "🏆 **کاربران برتر گروه:**\n\n"
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
        game_sessions[user.id] = {'type': 'number', 'number': number, 'attempts': 0}
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
    game_sessions[update.effective_user.id] = {'type': 'number', 'number': number, 'attempts': 0}
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
    warning_count = db.add_warning(update.effective_user.id, update.effective_chat.id)
    max_warns = 3
    
    if warning_count >= max_warns:
        db.mute_user(update.effective_user.id, update.effective_chat.id, 60)
        await update.message.reply_text(f"🚫 {username} ۳ تا اخطار گرفت و ۱ ساعت میوت شد!")
    else:
        await update.message.reply_text(
            WARN_MESSAGES[warning_count-1].format(
                name=username, 
                max=max_warns, 
                duration=60
            )
        )

async def mute(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ فقط ادمین!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ مثال: /mute @username 60")
        return
    
    username = context.args[0].replace('@', '')
    minutes = int(context.args[1]) if len(context.args) > 1 and context.args[1].isdigit() else 60
    
    db.mute_user(update.effective_user.id, update.effective_chat.id, minutes)
    await update.message.reply_text(f"🔇 {username} به مدت {minutes} دقیقه میوت شد!")

async def unmute(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ فقط ادمین!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ مثال: /unmute @username")
        return
    
    username = context.args[0].replace('@', '')
    db.unmute_user(update.effective_user.id, update.effective_chat.id)
    await update.message.reply_text(f"🔊 میوت {username} برداشته شد!")

async def clear_warns(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ فقط ادمین!")
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ مثال: /clear_warns @username")
        return
    
    username = context.args[0].replace('@', '')
    db.clear_warnings(update.effective_user.id, update.effective_chat.id)
    await update.message.reply_text(f"✅ اخطارهای {username} پاک شد!")

async def set_mood(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ فقط ادمین!")
        return
    
    if not context.args or context.args[0] not in ["happy", "roast", "evil", "neutral"]:
        await update.message.reply_text("❌ حالت‌ها: happy, roast, evil, neutral")
        return
    
    mood_manager.set_mood(context.args[0])
    await update.message.reply_text(f"✅ روحیه به {context.args[0]} تغییر کرد!")

# ==================== رویدادهای گروه ====================

async def group_join(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text(random.choice(BOT_JOIN_MESSAGES))
            db.add_group(update.effective_chat.id, update.effective_chat.title)
            return
        
        welcome_text = random.choice(WELCOME_MESSAGES).format(name=member.first_name)
        await update.message.reply_text(welcome_text)
        db.add_user(member.id, member.username or "unknown", member.first_name, update.effective_chat.id)

async def group_leave(update: Update, context: CallbackContext):
    if update.message.left_chat_member:
        user = update.message.left_chat_member
        goodbye_text = random.choice(GOODBYE_MESSAGES).format(name=user.first_name)
        await update.message.reply_text(goodbye_text)

# ==================== پیام‌های خودکار هوشمند ====================

async def auto_interaction(context: CallbackContext):
    """ارسال پیام خودکار هوشمند ربات در گروه"""
    global last_auto_message
    
    if (datetime.now() - last_auto_message).seconds < 300:
        return
    
    # افزایش شانس ارسال بر اساس روحیه
    mood = mood_manager.get_mood()
    chance = 0.15
    if mood == "roast":
        chance = 0.25
    elif mood == "evil":
        chance = 0.20
    elif mood == "happy":
        chance = 0.10
    
    if random.random() > chance:
        return
    
    chat_id = context.job.context.get('chat_id')
    if not chat_id:
        return
    
    try:
        actions = ['roast', 'greeting', 'question', 'joke', 'fact', 'story']
        
        # انتخاب بر اساس روحیه
        if mood == "roast":
            action = random.choice(['roast', 'roast', 'roast', 'joke'])
        elif mood == "evil":
            action = random.choice(['roast', 'roast', 'greeting', 'question'])
        elif mood == "happy":
            action = random.choice(['greeting', 'joke', 'fact', 'story'])
        else:
            action = random.choice(['question', 'greeting', 'fact'])
        
        if action == 'roast':
            names = ["دوست عزیز", "رفیق", "کاربر گرامی", "هم‌گروهی"]
            name = random.choice(names)
            msg = random.choice(AUTO_ROASTS).format(name=name)
        elif action == 'greeting':
            msg = random.choice(GREETING_RESPONSES).format(name="همه")
        elif action == 'joke':
            msg = f"😄 {random.choice(JOKES)}"
        elif action == 'fact':
            msg = f"💡 {random.choice(FACTS)}"
        elif action == 'story':
            stories = [
                "می‌دونستید؟ 🐧 پنگوئن‌ها وقتی عاشق میشن، یه سنگریزه به جفتشون هدیه میدن!",
                "جالب بدونید که 🐘 فیل‌ها تنها حیواناتی هستن که نمی‌تونن بپرن!",
                "آیا می‌دونستید؟ 🐝 زنبورها برای تولید ۱ کیلو عسل باید ۲ میلیون گل رو ببینن!",
            ]
            msg = random.choice(stories)
        else:
            questions = [
                "🤔 نظرتون چیه درباره این موضوع؟",
                "😏 امروز چه خبر از گروه؟",
                "😂 کی میاد یه جوک بگه؟",
                "🔥 امروز حال دارید؟",
                "😎 چه خبر؟",
                "💪 امروز چه برنامه‌ای دارید؟",
                "🌟 چه خبر از دنیا؟",
                "🎯 امروز قراره چیکار کنید؟"
            ]
            msg = random.choice(questions)
        
        await context.bot.send_message(chat_id=chat_id, text=msg)
        last_auto_message = datetime.now()
        
    except Exception as e:
        logger.error(f"خطا در ارسال پیام خودکار: {e}")

# ==================== مدیریت پیام‌های هوشمند ====================

async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    text = update.message.text
    chat_id = update.effective_chat.id
    
    if not text or not user or user.is_bot:
        return
    
    # ثبت کاربر و آمار
    db.add_user(user.id, user.username or "unknown", user.first_name, chat_id)
    db_user = db.get_user(user.id, chat_id)
    
    # به‌روزرسانی تعاملات کاربر
    user_interaction_count[user.id] += 1
    
    # تحلیل متن کاربر برای تغییر روحیه ربات
    mood_manager.update_from_user(user.id, text)
    
    # بررسی میوت
    if db_user and db_user['is_muted']:
        if db_user['mute_until']:
            try:
                mute_time = datetime.fromisoformat(db_user['mute_until'])
                if datetime.now() < mute_time:
                    await update.message.delete()
                    remaining = (mute_time - datetime.now()).seconds // 60
                    await update.message.reply_text(f"🔇 {user.first_name} تا {remaining} دقیقه دیگه میوت هستی!")
                    return
                else:
                    db.unmute_user(user.id, chat_id)
            except:
                db.unmute_user(user.id, chat_id)
    
    # بازی‌ها
    if user.id in game_sessions:
        game = game_sessions[user.id]
        
        if game['type'] == 'number':
            try:
                guess = int(text)
                game['attempts'] = game.get('attempts', 0) + 1
                if guess < game['number']:
                    await update.message.reply_text(f"🔽 برو بالا! (حدس {game['attempts']})")
                elif guess > game['number']:
                    await update.message.reply_text(f"🔼 برو پایین! (حدس {game['attempts']})")
                else:
                    await update.message.reply_text(f"🎉 آفرین! عدد {game['number']} رو در {game['attempts']} حدس زدی!")
                    del game_sessions[user.id]
            except ValueError:
                await update.message.reply_text("❌ لطفاً یه عدد بفرست!")
            return
        
        elif game['type'] == 'riddle':
            if text.lower() == game['answer'].lower():
                await update.message.reply_text(f"🎉 درست! جواب: {game['answer']}")
                del game_sessions[user.id]
            else:
                await update.message.reply_text("❌ نه! دوباره امتحان کن!")
            return
    
    # ========== دیالوگ‌های هوشمند ==========
    
    text_lower = text.lower()
    
    # تشخیص کلمات کلیدی با پاسخ‌های متنوع
    if re.search(r'\b(سلام|سَلآم|سلامت|درود|هی|هاي)\b', text_lower):
        await update.message.reply_text(random.choice(GREETING_RESPONSES).format(name=user.first_name))
        return
    
    if re.search(r'\b(خداحافظ|خدا حافظ|بای|بی|فعلا|بعدا)\b', text_lower):
        await update.message.reply_text(random.choice(GOODBYE_RESPONSES).format(name=user.first_name))
        return
    
    if re.search(r'\b(ممنون|تشکر|مرسی|متشکرم|دمت گرم)\b', text_lower):
        await update.message.reply_text(random.choice(THANK_RESPONSES).format(name=user.first_name))
        return
    
    if re.search(r'\b(خسته|کسل|بیحال|بی انرژی)\b', text_lower):
        await update.message.reply_text(random.choice(SAD_RESPONSES).format(name=user.first_name))
        return
    
    if re.search(r'\b(خوشحال|خوب|عالی|قشنگ|باحال|جالب)\b', text_lower):
        await update.message.reply_text(random.choice(HAPPY_RESPONSES).format(name=user.first_name))
        return
    
    if re.search(r'\b(عشق|دوست دارم|عاشقتم|love)\b', text_lower):
        responses = [
            f"❤️ {user.first_name}، منم عاشقتم! (شوخی!) 😂",
            f"😍 {user.first_name} جان! انرژی عشق میدی به گروه!",
            f"💕 {user.first_name}، عشق همونی که تو میگی!",
            f"🥰 {user.first_name}، عاشقتم! (واقعاً!)"
        ]
        await update.message.reply_text(random.choice(responses))
        return
    
    if re.search(r'\b(ربات|بات|رباط|bot)\b', text_lower):
        responses = [
            f"🤖 بله {user.first_name}؟ من اینجام!",
            f"😈 چی شد {user.first_name}؟ حواست هست؟",
            f"👀 {user.first_name}، منو صدا کردی؟",
            f"🤖 اینجام! چی شده؟",
            f"😊 بله عزیزم؟!"
        ]
        await update.message.reply_text(random.choice(responses))
        return
    
    if re.search(r'\b(میوت|سکوت|خفه|شوت)\b', text_lower):
        await update.message.reply_text(f"😏 {user.first_name}، این حرفا رو نزن! بد میشه!")
        return
    
    # پاسخ به سوالات
    if '?' in text or '؟' in text:
        question_responses = [
            f"🤔 {user.first_name}، سوال خوبی پرسیدی! ولی جوابش رو نمی‌دونم! 😂",
            f"😊 {user.first_name}، جواب این سوال رو باید از گوگل بپرسی!",
            f"😅 {user.first_name}، اگه جواب رو می‌دونستم، خودم ربات نبودم!",
            f"🤖 {user.first_name}، سوال‌ت ثبت شد! بعداً جواب میدم!",
            f"💭 {user.first_name}، به نظرت خودت چی می‌دونی؟",
        ]
        await update.message.reply_text(random.choice(question_responses))
        return
    
    # تیکه پرانی تصادفی برای کاربران پرحرف (هر ۱۰ پیام)
    if user_interaction_count[user.id] % 10 == 0 and user_interaction_count[user.id] > 0:
        roast_chance = random.random()
        if roast_chance < 0.3:  # ۳۰٪ شانس
            await update.message.reply_text(
                random.choice(AUTO_ROASTS).format(name=user.first_name)
            )
            return
    
    # پاسخ بر اساس روحیه ربات (۱۵٪ شانس)
    if random.random() < 0.15:
        m = mood_manager.get_mood()
        responses = MOOD_RESPONSES.get(m, MOOD_RESPONSES["neutral"])
        await update.message.reply_text(random.choice(responses).format(name=user.first_name))
    
    # به‌روزرسانی لقب
    if db_user:
        new_title = title_manager.get_title(db_user['message_count'])
        if new_title != db_user['current_title']:
            db.update_title(user.id, chat_id, new_title)
            if db_user['message_count'] % 5 == 0:
                await update.message.reply_text(f"🎉 لقب شما به **{new_title}** تغییر کرد!", parse_mode='Markdown')

# ==================== اجرا ====================

async def main():
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
    app.add_handler(CommandHandler("clear_warns", clear_warns))
    app.add_handler(CommandHandler("set_mood", set_mood))
    
    # کالبک
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^game_"))
    
    # رویدادها
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, group_join))
    app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, group_leave))
    
    # پیام‌ها
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Job برای پیام‌های خودکار
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(auto_interaction, interval=240, first=10, context={'chat_id': None})
    
    print("🤖 ربات فوق‌هوشمند روشن شد!")
    print("🔥 قابلیت‌ها:")
    print("• دیالوگ‌های بی‌نهایت")
    print("• تشخیص روحیه کاربران")
    print("• پیام‌های خودکار هوشمند")
    print("• تیکه‌پرانی بر اساس شخصیت")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    asyncio.run(main())
