import telebot
import requests
import time
from random import choice
import json

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
    sent_cards = load_sent_cards()
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

# الانضمام إلى قناة خاصة والحصول على ID
@bot.message_handler(commands=['join_private'])
def join_private(message):
    try:
        link = message.text.split()[1]
        bot.join_chat(link)  # البوت ينضم باستخدام الرابط
        chat_info = bot.get_chat(link)
        bot.reply_to(message, f"✅ تم الاشتراك بنجاح.\nID المجموعة/القناة: `{chat_info.id}`")
    except IndexError:
        bot.reply_to(message, "❌ يجب إدخال رابط الدعوة بعد الأمر.\nمثال: `/join_private https://t.me/yourchannel`")
    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")

# استيراد الفيز
def import_from_source(source_id):
    try:
        updates = bot.get_chat_history(source_id, limit=50)
        for message in updates.messages:
            if message.text and "|" in message.text:
                cards = [line.strip() for line in message.text.splitlines() if "|" in line]
                for card in cards:
                    send_card(card)
        print("تم استيراد الفيز بنجاح.")
    except Exception as e:
        print(f"خطأ أثناء الاستيراد: {e}")

# أوامر البوت
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "مرحبًا! استخدم الأوامر للاستيراد:\n/import_from_id [ID]\n/import_from_link [رابط]\n/join_private [رابط دعوة]")

@bot.message_handler(commands=['import_from_id'])
def import_from_id(message):
    try:
        source_id = int(message.text.split()[1])
        bot.reply_to(message, f"جارٍ الاستيراد من المصدر ID: {source_id}")
        import_from_source(source_id)
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ يجب إدخال معرف ID صحيح بعد الأمر.")

@bot.message_handler(commands=['import_from_link'])
def import_from_link(message):
    try:
        link = message.text.split()[1]
        source_id = bot.get_chat(link).id
        bot.reply_to(message, f"جارٍ الاستيراد من الرابط: {link}")
        import_from_source(source_id)
    except (IndexError, Exception) as e:
        bot.reply_to(message, f"❌ حدث خطأ: {e}")

# تشغيل البوت
bot.polling()
