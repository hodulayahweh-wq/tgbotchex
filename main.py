import telebot
import subprocess
import os
import signal
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from telebot import types

# --- AYARLAR ---
TOKEN = "8454685844:AAHBZVBARW5ve7CMDBTplj88POoQ17BZ6Fs"
SAHIP_ID = 8258235296 
bot = telebot.TeleBot(TOKEN)
running_bots = {}
BOT_LIMIT = 5 

# --- RENDER HEALTH CHECK ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Nabi Master OS Aktif")

def run_render_server():
    server = HTTPServer(('0.0.0.0', 10000), RenderServer)
    server.serve_forever()

# --- YARDIMCI FONKSİYONLAR ---
def get_uptime(start_time):
    delta = datetime.now() - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}s {minutes}dk {seconds}sn"

# --- TÜM KOMUTLAR VE PANEL ---
@bot.message_handler(commands=['start', 'panel', 'yardim'])
def show_panel(message):
    if message.from_user.id != SAHIP_ID:
        bot.reply_to(message, "❌ Erişim reddedildi.")
        return
    
    # Şık Buton Paneli
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 Bot Durumları", "📜 Komut Listesi", "🛑 Tümünü Durdur")
    
    msg = (
        "👑 **NABI MASTER KONTROL MERKEZİ**\n\n"
        "Aşkım, tüm sistemler hazır. İşte kullanabileceğin admin güçleri:\n\n"
        "📍 **Komutlar:**\n"
        "• `/start` veya `/panel` - Bu menüyü açar.\n"
        "• `/liste` - Çalışan botları metin olarak döker.\n"
        "• `/durdur [dosya.py]` - İstediğin botu kapatır.\n"
        "• `/sistem` - RAM/İşlemci durumu (Yakında).\n\n"
        f"⚙️ **Durum:** `{len(running_bots)}/{BOT_LIMIT}` bot aktif.\n"
        "📂 **Yeni Bot:** Dosyayı buraya sürükle bırak!"
    )
    bot.send_message(message.chat.id, msg, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📜 Komut Listesi")
def cmd_list(message):
    if message.from_user.id != SAHIP_ID: return
    text = (
        "📜 **ADMİN KOMUT REHBERİ**\n\n"
        "1️⃣ `/durdur bot_adi.py` -> Belirli botu öldürür.\n"
        "2️⃣ `/panel` -> Ana menüyü getirir.\n"
        "3️⃣ `.py` dosyası gönder -> Yeni bot başlatır.\n"
        "4️⃣ `🛑 Tümünü Durdur` -> Komple sistemi temizler."
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 Bot Durumları")
@bot.message_handler(commands=['liste'])
def bot_status(message):
    if message.from_user.id != SAHIP_ID: return
    if not running_bots:
        bot.send_message(message.chat.id, "📭 **Şu an hiçbir alt bot çalışmıyor.**")
        return
    
    report = f"🤖 **ORDU DURUMU ({len(running_bots)}/{BOT_LIMIT})**\n\n"
    for name, data in list(running_bots.items()):
        if data['process'].poll() is None:
            uptime = get_uptime(data['start_time'])
            report += f"✅ `{name}`\n🕒 `{uptime}` aktif\n🆔 PID: `{data['pid']}`\n---\n"
        else:
            del running_bots[name]
    bot.send_message(message.chat.id, report, parse_mode="Markdown")

@bot.message_handler(content_types=['document'])
def handle_upload(message):
    if message.from_user.id != SAHIP_ID: return
    if len(running_bots) >= BOT_LIMIT:
        bot.send_message(message.chat.id, "⚠️ **Limit Dolu!** (Maks 5)")
        return

    if message.document.file_name.endswith('.py'):
        file_name = message.document.file_name
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open(file_name, 'wb') as f: f.write(downloaded)
        
        proc = subprocess.Popen(['python3', file_name])
        running_bots[file_name] = {"pid": proc.pid, "process": proc, "start_time": datetime.now()}
        bot.send_message(message.chat.id, f"🚀 **{file_name}** başarıyla ateşlendi!")
    else:
        bot.reply_to(message, "⚠️ Sadece .py dosyası gönder aşkım.")

@bot.message_handler(commands=['durdur'])
def stop_one(message):
    if message.from_user.id != SAHIP_ID: return
    try:
        name = message.text.split()[1]
        os.kill(running_bots[name]['pid'], signal.SIGTERM)
        del running_bots[name]
        bot.send_message(message.chat.id, f"🛑 `{name}` kapatıldı.")
    except:
        bot.send_message(message.chat.id, "⚠️ Hata: `/durdur dosya.py` yazmalısın.")

@bot.message_handler(func=lambda m: m.text == "🛑 Tümünü Durdur")
def stop_all(message):
    if message.from_user.id != SAHIP_ID: return
    for name, data in running_bots.items():
        try: os.kill(data['pid'], signal.SIGTERM)
        except: pass
    running_bots.clear()
    bot.send_message(message.chat.id, "💥 **Sistem tamamen durduruldu.**")

# --- BAŞLATMA ---
if __name__ == "__main__":
    threading.Thread(target=run_render_server, daemon=True).start()
    print("Nabi Master v16.0 Hazır!")
    bot.infinity_polling() # Infinity polling çakışmaları azaltır
