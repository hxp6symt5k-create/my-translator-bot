import threading
from flask import Flask
from telethon import TelegramClient, events
from deep_translator import GoogleTranslator
import os

# --- إعداد Flask (للحفاظ على البوت نشطاً) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "البوت يعمل الآن!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

# --- إعداد البوت ---
BOT_TOKEN = '8834802083:AAEFIafy5AMyvXY16FTsU_SP47lOerEAfwY'
client = TelegramClient('bot_session', api_id='24962965', api_hash='f502f0bc2963b2d565bb6ad0151c48ee').start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage)
async def handler(event):
    if event.raw_text and event.raw_text != '/start':
        try:
            translated = GoogleTranslator(source='auto', target='om').translate(event.raw_text)
            await event.reply(f"Hiikkaan:\n{translated}")
        except Exception as e:
            await event.reply("حدث خطأ في الترجمة.")

# --- تشغيل الخادم والبوت معاً ---
if __name__ == '__main__':
    # تشغيل Flask في مسار منفصل (Thread)
    threading.Thread(target=run_flask).start()
    print("البوت والخادم يعملان!")
    client.run_until_disconnected()