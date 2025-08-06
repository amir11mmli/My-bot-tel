import telebot
from telebot import types
from flask import Flask
import threading

API_TOKEN = '8134019036:AAF03l5fvkXot7T_HiDClneKkgTGNi8YCrQ'
CHANNELS = ['@sakvny']  # کانال عمومی شما

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# اجرای سرور Flask در پس‌زمینه برای زنده نگه‌داشتن ربات
def run():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run).start()

@app.route('/')
def home():
    return 'ربات آنلاین است!'

# بارگذاری پست‌ها از فایل
def load_posts():
    try:
        with open("posts.txt", "r", encoding="utf-8") as f:
            lines = f.read().strip().split("\n")
            return [(lines[i], lines[i + 1]) for i in range(0, len(lines), 2)]
    except:
        return []

# بررسی عضویت کاربر در کانال
def is_member(user_id):
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            print(f"[ERROR] بررسی عضویت در {ch}: {e}")
            return False
    return True

# وضعیت پست فعلی هر کاربر
user_states = {}

# هندلر start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_member(user_id):
        user_states[user_id] = 0
        send_post(user_id)
    else:
        markup = types.InlineKeyboardMarkup()
        for ch in CHANNELS:
            markup.add(types.InlineKeyboardButton("📢 عضویت در کانال", url=f"https://t.me/{ch[1:]}"))
        markup.add(types.InlineKeyboardButton("✅ عضو شدم", callback_data="check_join"))
        bot.send_message(user_id, "⛔️ اول باید عضو این کانال بشی:", reply_markup=markup)

# ارسال پست
def send_post(user_id):
    posts = load_posts()
    index = user_states.get(user_id, 0)
    if index < len(posts):
        title, content = posts[index]
        markup = types.InlineKeyboardMarkup()
        if index + 1 < len(posts):
            markup.add(types.InlineKeyboardButton("▶️ پست بعدی", callback_data="next_post"))
        bot.send_message(user_id, f"📄 {title}\n\n{content}", reply_markup=markup)
    else:
        bot.send_message(user_id, "https://t.me/+o7GOFYDDTmplMmI8")

# بررسی عضویت پس از کلیک "عضو شدم"
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    user_id = call.from_user.id
    if is_member(user_id):
        user_states[user_id] = 0
        bot.answer_callback_query(call.id, "✅ عضویت تأیید شد!")
        send_post(user_id)
    else:
        bot.answer_callback_query(call.id, "⛔️ هنوز عضو نیستی!", show_alert=True)

# پست بعدی
@bot.callback_query_handler(func=lambda call: call.data == "next_post")
def next_post(call):
    user_id = call.from_user.id
    user_states[user_id] = user_states.get(user_id, 0) + 1
    send_post(user_id)

# اجرا
bot.infinity_polling()
