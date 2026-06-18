import os
import threading
from flask import Flask, request
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from deep_translator import GoogleTranslator
import pytesseract
from PIL import Image

# 1. إعداد Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    password = os.environ.get('ADMIN_PASSWORD', '123456')
    if request.method == 'POST':
        if request.form.get('password') == password:
            return "مرحباً بك في لوحة تحكم الأدمن. البوت يعمل حالياً."
        else:
            return "كلمة المرور خاطئة!"
    return '<form method="post"><input type="password" name="password" placeholder="كلمة المرور"><input type="submit" value="دخول"></form>'

# 2. إعداد المتغيرات
API_ID = int(os.environ.get('API_ID', 24962965))
API_HASH = os.environ.get('API_HASH', 'f502f0bc2963b2d565bb6ad0151c48ee')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

# 3. تشغيل البوت
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage)
async def handler(event):
    if event.raw_text and event.raw_text != '/start':
        try:
            translated = GoogleTranslator(source='auto', target='om').translate(event.raw_text)
            await event.reply(f"Hiikkaan:\n{translated}")
        except:
            await event.reply("عذراً، حدث خطأ في الترجمة.")

    elif event.photo:
        path = await event.download_media()
        try:
            # ملاحظة: إذا واجهت خطأ في السيرفر، قد تحتاج لحذف سطر pytesseract التالي
            text = pytesseract.image_to_string(Image.open(path)) 
            if text.strip():
                translated = GoogleTranslator(source='auto', target='om').translate(text)
                await event.reply(f"نص الصورة المترجم:\n{translated}")
            else:
                await event.reply("لم أجد نصاً في الصورة.")
        except:
            await event.reply("فشل قراءة الصورة.")
        finally:
            if os.path.exists(path): os.remove(path)

# 4. تشغيل الخادم والبوت معاً
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    client.run_until_disconnected()
