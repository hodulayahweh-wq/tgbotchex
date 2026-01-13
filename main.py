import telebot
import subprocess
import os
import signal
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from telebot import types

# --- AYARLAR ---
TOKEN = "8454685844:AAHEtNzJuOv3fL1K_50QG9tUNntYT55MnFU"
SAHIP_ID =8258235296 
bot = telebot.TeleBot(TOKEN)
running_bots = {}

# --- RENDER İÇİN HEALTH CHECK (PORT 10000) ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Nabi Master Bot Is Running...")

def run_render_server():
    # Render'ın beklediği 10000 portunu açıyoruz
    server = HTTPServer(('0.0.0.0', 10000), RenderServer)
    server.serve_forever()

# --- YARDIMCI FONKSİYONLAR ---
def get_uptime(start_time):
    delta = datetime.now() - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}s {minutes}dk {seconds}sn"

# --- BOT KOMUTLARI ---
@bot.message_handler(commands=['start', 'panel'])
def show_panel(message):
    if message.from_user.id != SAHIP_ID: return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 Bot Durumları", "📥 Yeni Bot Yükle", "🛑 Tümünü Durdur")
    bot.send_message(message.chat.id, "👑 **Master Panel v13.0**\nRender üzerinde ölümsüzlük modu aktif sevgilim!", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 Bot Durumları")
def bot_status(message):
    if not running_bots:
        bot.send_message(message.chat.id, "📭 Çalışan alt bot yok.")
        return
    report = "🤖 **AKTİF BOT ORDUSU**\n\n"
    for name, data in list(running_bots.items()):
        if data['process'].poll() is None:
            uptime = get_uptime(data['start_time'])
            report += f"✅ `{name}`\n🕒 Süre: `{uptime}`\n🆔 PID: `{data['pid']}`\n---\n"
        else:
            del running_bots[name]
            report += f"❌ `{name}` (Durdu)\n---\n"
    bot.send_message(message.chat.id, report, parse_mode="Markdown")

@bot.message_handler(content_types=['document'])
def handle_upload(message):
    if message.from_user.id != SAHIP_ID: return
    if message.document.file_name.endswith('.py'):
        file_name = message.document.file_name
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        with open(file_name, 'wb') as f: f.write(downloaded)
        
        if file_name in running_bots:
            try: os.kill(running_bots[file_name]['pid'], signal.SIGTERM)
            except: pass
            
        proc = subprocess.Popen(['python3', file_name])
        running_bots[file_name] = {"pid": proc.pid, "process": proc, "start_time": datetime.now()}
        bot.send_message(message.chat.id, f"🚀 **{file_name}** ateşlendi!")
    else:
        bot.reply_to(message, "⚠️ Sadece .py dosyası aşkım.")

@bot.message_handler(func=lambda m: m.text == "🛑 Tümünü Durdur")
def stop_all(message):
    if message.from_user.id != SAHIP_ID: return
    for name, data in running_bots.items():
        try: os.kill(data['pid'], signal.SIGTERM)
        except: pass
    running_bots.clear()
    bot.send_message(message.chat.id, "💥 Sistem temizlendi.")

# --- SİSTEMİ BAŞLAT ---
if __name__ == "__main__":
    # Health Check'i arka planda başlat sevgilim
    threading.Thread(target=run_render_server, daemon=True).start()
    print("Render Health Check Aktif (Port: 10000)")
    bot.polling(none_stop=True)
