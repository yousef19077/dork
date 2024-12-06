import requests
from bs4 import BeautifulSoup
import telebot
import random
import json
import time

# إعداد البوت
BOT_TOKEN = "7303620071:AAFI15Tkv-1pWRkPSLo1K_d7BXK2rMXSPwo"  # استبدل بالتوكن الخاص بك
bot = telebot.TeleBot(BOT_TOKEN)

# قائمة User-Agent
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0"
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

# دالة البحث باستخدام Google Dork
def google_dork_search(dork_query, num_results=10, max_pages=3):
    headers = {"User-Agent": random.choice(user_agents)}
    results = set()
    proxies = None  # أضف بروكسي هنا إذا توفر لديك

    for page in range(max_pages):
        start = page * num_results
        search_url = f"https://www.google.com/search?q={dork_query}&num={num_results}&start={start}"

        try:
            response = requests.get(search_url, headers=headers, proxies=proxies, timeout=10)
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
                bot.send_message(chat_id, "تم تجاوز عدد الطلبات المسموح بها. سيتم الانتظار قليلًا...")
                time.sleep(random.uniform(10, 30))  # انتظار عشوائي بين 10-30 ثانية
        except requests.RequestException as e:
            bot.send_message(chat_id, f"خطأ في الاتصال: {e}")
            time.sleep(random.uniform(10, 30))  # انتظار عشوائي

    return list(results)

# أزرار اختيار نوع المنتج
@bot.message_handler(commands=['start', 'product'])
def product_menu(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    products = ["Electronics", "Clothing", "Books", "Toys", "Furniture", "Groceries"]
    for product in products:
        markup.add(telebot.types.InlineKeyboardButton(product, callback_data=f"product:{product}"))
    bot.send_message(message.chat.id, "اختر نوع المنتج:", reply_markup=markup)

# معالجة اختيار المنتج
@bot.callback_query_handler(func=lambda call: call.data.startswith("product:"))
def select_product(call):
    product = call.data.split(":")[1]
    bot.send_message(call.message.chat.id, f"تم اختيار المنتج: {product}\nالرجاء اختيار بوابة الدفع:")
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    gateways = [
        "PayPal", "Stripe", "Braintree", "Square", "Authorize.Net", 
        "2Checkout", "Adyen", "Amazon Pay", "Google Pay", "Apple Pay", 
        "Klarna", "Skrill", "WePay", "Worldpay", "BlueSnap"
    ]
    for gateway in gateways:
        markup.add(telebot.types.InlineKeyboardButton(gateway, callback_data=f"gateway:{product}:{gateway}"))
    bot.send_message(call.message.chat.id, "اختر بوابة الدفع:", reply_markup=markup)

# معالجة اختيار بوابة الدفع
@bot.callback_query_handler(func=lambda call: call.data.startswith("gateway:"))
def select_gateway(call):
    _, product, gateway = call.data.split(":")
    bot.send_message(call.message.chat.id, f"تم اختيار بوابة الدفع: {gateway}\nالرجاء اختيار نوع العملة:")
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    currencies = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CNY", "INR"]
    for currency in currencies:
        markup.add(telebot.types.InlineKeyboardButton(currency, callback_data=f"currency:{product}:{gateway}:{currency}"))
    bot.send_message(call.message.chat.id, "اختر العملة:", reply_markup=markup)

# معالجة اختيار العملة
@bot.callback_query_handler(func=lambda call: call.data.startswith("currency:"))
def select_currency(call):
    _, product, gateway, currency = call.data.split(":")
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
    except ValueError:
        bot.send_message(message.chat.id, "الرجاء إدخال مبلغ صالح. مثال: 100.50")
        bot.register_next_step_handler(message, process_price, product, gateway, currency)

# تشغيل البوت
print("Bot is running...")
bot.polling()
