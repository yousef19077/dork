import requests
from bs4 import BeautifulSoup
import telebot
import random
import json
import time

# إعداد البوت
BOT_TOKEN = "7725003415:AAGrEIEZM10jQ0cLN7-EUptht4u8sEMHnTE"  # استبدل بالتوكن الخاص بك
bot = telebot.TeleBot(BOT_TOKEN)

# قائمة User-Agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0"
]

# قائمة البروكسيات
proxies = [
    "104.167.27.85:3128",
    "156.228.81.35:3128",
    "156.240.99.34:3128",
    "104.207.32.32:3128",
    "156.233.87.19:3128",
    "156.228.174.146:3128",
    "104.207.52.183:3128",
    "104.207.35.176:3128",
    "156.228.105.144:3128",
    "104.207.50.156:3128",
    "156.228.182.209:3128",
    "156.253.176.100:3128",
    "104.207.58.29:3128",
    "154.94.12.229:3128",
    "104.167.31.238:3128",
    "156.228.88.168:3128",
    "104.207.56.158:3128",
    "156.228.102.72:3128",
    "156.228.98.144:3128"
]

# تحميل أو إنشاء القائمة السوداء
BLACKLIST_FILE = "blacklist.json"
try:
    with open(BLACKLIST_FILE, "r") as f:
        blacklist = set(json.load(f))
except (FileNotFoundError, json.JSONDecodeError):
    blacklist = set()

def save_blacklist():
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(list(blacklist), f)

# دالة اختيار بروكسي عشوائي
def get_random_proxy():
    return {"http": random.choice(proxies), "https": random.choice(proxies)}

# دالة البحث باستخدام Google Dork
def google_dork_search(dork_query, num_results=5, max_pages=2):
    headers = {"User-Agent": random.choice(user_agents)}
    results = set()

    for page in range(max_pages):
        start = page * num_results
        search_url = f"https://www.google.com/search?q={dork_query}&num={num_results}&start={start}"
        
        try:
            proxy = get_random_proxy()  # اختيار بروكسي عشوائي
            response = requests.get(search_url, headers=headers, proxies=proxy, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for g in soup.find_all('div', class_='tF2Cxc'):
                    title = g.find('h3').text
                    link = g.find('a')['href']
                    if link not in blacklist:
                        blacklist.add(link)
                        save_blacklist()
                        results.add(f"{title} - {link}")
            elif response.status_code == 429:
                time.sleep(5)  # الانتظار قبل إعادة المحاولة
                continue
            else:
                return [f"فشل في البحث. رمز الحالة: {response.status_code}"]
        except Exception as e:
            return [f"حدث خطأ أثناء البحث: {str(e)}"]

        time.sleep(5)  # الانتظار بين الطلبات

    return list(results)

# رابط الفيديو من قناة التليجرام
VIDEO_URL = "https://t.me/reeetere/15"  # استبدل برابط الفيديو الخاص بك

# أزرار اختيار نوع المنتج
@bot.message_handler(commands=['start', 'product'])
def product_menu(message):
    # إرسال الفيديو أولاً فقط في البداية
    bot.send_video(message.chat.id, VIDEO_URL)
    
    # إرسال الأزرار بعد الفيديو
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    products = [
        "Electronics", "Clothing", "Books", "Toys", "Furniture", 
        "Groceries", "Health", "Beauty", "Sports", "Automotive"
    ]
    buttons = [telebot.types.InlineKeyboardButton(product, callback_data=f"product:{product}") for product in products]
    markup.add(*buttons)
    bot.send_message(message.chat.id, "اختر نوع المنتج:", reply_markup=markup)

# معالجة اختيار المنتج
@bot.callback_query_handler(func=lambda call: call.data.startswith("product:"))
def select_product(call):
    product = call.data.split(":")[1]
    
    # إزالة الأزرار السابقة
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    
    bot.send_message(call.message.chat.id, f"تم اختيار المنتج: {product}\nالرجاء اختيار بوابة الدفع:")
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    gateways = [
        "PayPal", "Stripe", "Braintree", "Square", "Authorize.Net", 
        "2Checkout", "Adyen", "Amazon Pay", "Google Pay", "Apple Pay", 
        "Klarna", "Skrill", "WePay", "Worldpay", "BlueSnap"
    ]
    buttons = [telebot.types.InlineKeyboardButton(gateway, callback_data=f"gateway:{product}:{gateway}") for gateway in gateways]
    markup.add(*buttons)
    bot.send_message(call.message.chat.id, "اختر بوابة الدفع:", reply_markup=markup)

# معالجة اختيار بوابة الدفع
@bot.callback_query_handler(func=lambda call: call.data.startswith("gateway:"))
def select_gateway(call):
    _, product, gateway = call.data.split(":")
    
    # إزالة الأزرار السابقة
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    
    bot.send_message(call.message.chat.id, f"تم اختيار بوابة الدفع: {gateway}\nالرجاء اختيار نوع العملة:")
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    currencies = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CNY", "INR"]
    buttons = [telebot.types.InlineKeyboardButton(currency, callback_data=f"currency:{product}:{gateway}:{currency}") for currency in currencies]
    markup.add(*buttons)
    bot.send_message(call.message.chat.id, "اختر العملة:", reply_markup=markup)

# معالجة اختيار العملة
@bot.callback_query_handler(func=lambda call: call.data.startswith("currency:"))
def select_currency(call):
    _, product, gateway, currency = call.data.split(":")
    
    # إزالة الأزرار السابقة
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    
    bot.send_message(call.message.chat.id, f"تم اختيار العملة: {currency}\nالرجاء إدخال السعر:")
    bot.register_next_step_handler(call.message, process_price, product, gateway, currency)

# معالجة إدخال السعر
def process_price(message, product, gateway, currency):
    try:
        price = float(message.text)
        dork_query = f'"{product}" "{gateway}" "{currency}" "{price}" "add to cart"'
        bot.send_message(message.chat.id, f"جاري البحث باستخدام الدورك:\n{dork_query}")
        # البحث بالدورك
        results = google_dork_search(dork_query)
        if results:
            for result in results:
                bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, "لم يتم العثور على نتائج.")
        bot.send_message(message.chat.id, "تم البحث بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "الرجاء إدخال مبلغ صالح. مثال: 100.50")
        bot.register_next_step_handler(message, process_price, product, gateway, currency)

# تشغيل البوت
print("Bot is running...")
bot.polling()
