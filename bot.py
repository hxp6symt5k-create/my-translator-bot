import os
import sqlite3
import threading
from flask import Flask, request
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from deep_translator import GoogleTranslator
import pytesseract
from PIL import Image

# 1. إعداد قاعدة البيانات لحفظ المستخدمين
db = sqlite3.connect('users.db', check_same_thread=False)
db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY)')
db.commit()

# 2. إعداد Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل بكفاءة!"

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    password = os.environ.get('ADMIN_PASSWORD', '123456')
    if request.method == 'POST':
        if request.form.get('password') == password:
            # حساب عدد المستخدمين
            cursor = db.execute('SELECT COUNT(*) FROM users')
            count = cursor.fetchone()[0]
            return f"مرحباً أدمن. عدد مستخدمي البوت الحالي هو: {count} مستخدم."
        else:
            return "كلمة المرور خاطئة!"
    return '<form method="post"><input type="password" name="password" placeholder="كلمة المرور"><input type="submit" value="عرض الإحصائيات"></form>'

# 3. إعداد البوت
API_ID = int(os.environ.get('API_ID', 24962965))
API_HASH = os.environ.get('API_HASH', 'f502f0bc2963b2d565bb6ad0151c48ee')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage)
async def handler(event):
    # تسجيل المستخدم في قاعدة البيانات
    if event.sender_id:
        db.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (event.sender_id,))
        db.commit()

    if event.raw_text and event.raw_text != '/start':
        try:
            translated = GoogleTranslator(source='auto', target='om').translate(event.raw_text)
            await event.reply(f"Hiikkaan:\n{translated}")
        except:
            await event.reply("عذراً، حدث خطأ في الترجمة.")

    elif event.photo:
        path = await event.download_media()
        try:
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

# 4. تشغيل الخادم والبوت
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    client.run_until_disconnected()
