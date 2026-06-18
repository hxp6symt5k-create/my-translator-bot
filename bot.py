import os
import threading
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from deep_translator import GoogleTranslator
import pytesseract
from PIL import Image

# إعداد خادم Flask للبقاء نشطاً
app = Flask(__name__)
@app.route('/')
def home(): return "البوت يعمل!"

# إعداد مسار Tesseract (على سيرفرات لينكس لا نحتاج مساراً كاملاً غالباً)
# إذا واجهت خطأ في السيرفر، قد نحتاج لضبط المسار هنا
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract' 

# جلب البيانات من متغيرات البيئة (التي ستضعها في موقع Render)
API_ID = int(os.environ.get('API_ID', 24962965))
API_HASH = os.environ.get('API_HASH', 'f502f0bc2963b2d565bb6ad0151c48ee')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

# إعداد البوت
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage)
async def handler(event):
    # التعامل مع النصوص
    if event.raw_text and event.raw_text != '/start':
        try:
            translated = GoogleTranslator(source='auto', target='om').translate(event.raw_text)
            await event.reply(f"Hiikkaan:\n{translated}")
        except:
            await event.reply("عذراً، حدث خطأ في الترجمة.")

    # التعامل مع الصور
    elif event.photo:
        path = await event.download_media()
        try:
            text = pytesseract.image_to_string(Image.open(path), lang='eng+amh+ara')
            if text.strip():
                translated = GoogleTranslator(source='auto', target='om').translate(text)
                await event.reply(f"نص الصورة المترجم:\n{translated}")
            else:
                await event.reply("لم أجد نصاً في الصورة.")
        except:
            await event.reply("فشل قراءة الصورة.")
        finally:
            if os.path.exists(path): os.remove(path)

# تشغيل البوت والخادم
if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))).start()
    client.run_until_disconnected()
