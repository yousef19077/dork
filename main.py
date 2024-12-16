import telebot
import requests
import time  # لإضافة التأخير بين الرسائل
from random import choice  # لاختيار صورة عشوائية
import json  # للعمل مع ملفات JSON

# ضع توكن البوت الخاص بك هنا
BOT_TOKEN = "7983611945:AAH8BA42GyvwQ__9ePR8v6T-KXlKRm6Dofg"
CHANNEL_ID = -1002380061998  # ضع هنا معرف القناة بصيغة ID (مع الرقم السالب)
SENT_CARDS_FILE = "sent_cards.json"  # اسم ملف الفيز المنشورة

bot = telebot.TeleBot(BOT_TOKEN)

# قائمة روابط الصور (20 صورة)
images = [
    "https://t.me/reeetere/37",
    "https://t.me/reeetere/38",
    "https://t.me/reeetere/39",
    "https://t.me/reeetere/40",
    "https://t.me/reeetere/41",
    "https://t.me/reeetere/42",
    "https://t.me/reeetere/43",
    "https://t.me/reeetere/44",
    "https://t.me/reeetere/45",
    "https://t.me/reeetere/46",
    "https://t.me/reeetere/47",
    "https://t.me/reeetere/48",
    "https://t.me/reeetere/49",
    "https://t.me/reeetere/50",
    "https://t.me/reeetere/51",
    "https://t.me/reeetere/52",
    "https://t.me/reeetere/53",
    "https://t.me/reeetere/54",
    "https://t.me/reeetere/55",
    "https://t.me/reeetere/56",
]

# قائمة لتتبع الفيز المرسلة
def load_sent_cards():
    try:
        with open(SENT_CARDS_FILE, "r") as file:
            data = file.read().strip()
            return set(json.loads(data)) if data else set()  # التحقق إذا كان الملف فارغًا
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_sent_cards(cards):
    with open(SENT_CARDS_FILE, "w") as file:
        json.dump(list(cards), file)

# API لمعالجة معلومات البطاقات
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

# قراءة ومعالجة ملف الفيز
def process_file(file_name):
    sent_cards = load_sent_cards()  # تحميل الفيز المنشورة من الملف
    try:
        with open(file_name, "r") as file:
            lines = file.readlines()
            for line in lines:
                if "|" in line:  # يفترض أن الفيز تكون على هذا الشكل
                    card = line.strip()
                    
                    # تحقق إذا كانت البطاقة قد أُرسلت من قبل
                    if card in sent_cards:
                        continue
                    
                    # الحصول على معلومات البطاقة
                    brand, card_type, level, bank, country, flag = info(card)
                    
                    # صياغة الرسالة
                    msg = f"""
ᴄᴄ⇾{card}
• sᴛᴀᴛᴜs⇾APPROVED ✅
━━━━━━• ɪɴꜰᴏ •━━━━━━
• ʙɪɴ⇾{card[:6]} | {brand} | {card_type}
• ᴄᴏᴜɴᴛʀʏ⇾{country}{flag}
• ʙᴀɴᴋ⇾{bank}
"""

                    # اختيار صورة عشوائية
                    image_url = choice(images)

                    # إعداد الزرَّين
                    markup = telebot.types.InlineKeyboardMarkup()
                    button1 = telebot.types.InlineKeyboardButton("Admin", url="https://t.me/wwpww6")
                    button2 = telebot.types.InlineKeyboardButton("Hello World ", url="https://t.me/c/2380061998/513")
                    markup.add(button1, button2)
                           # إرسال الرسالة إلى القناة
                    bot.send_photo(CHANNEL_ID, image_url, caption=msg, reply_markup=markup)
                    
                    # إضافة البطاقة إلى القائمة المرسلة
                    sent_cards.add(card)
                    save_sent_cards(sent_cards)  # حفظ الفيز المرسلة
                    
                    # تأخير لتجنب الحظر
                    time.sleep(5)
                    
            print("تمت معالجة الملف وإرسال المعلومات إلى القناة.")
    except FileNotFoundError:
        print(f"الملف {file_name} غير موجود في المجلد.")
    except Exception as e:
        print(f"حدث خطأ أثناء معالجة الملف: {e}")

# أمر البوت لبدء المعالجة
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, "مرحبًا! يتم الآن معالجة الملف...")
    process_file("cards.txt")  # استبدل "cards.txt" باسم ملفك

# تشغيل البوت
bot.polling()
