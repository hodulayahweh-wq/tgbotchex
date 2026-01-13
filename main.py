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
TOKEN = "8454685844:AAHEtNzJuOv3fL1K_50QG9tUNntYT55MnFU"
SAHIP_ID = 8258235296 
bot = telebot.TeleBot(TOKEN)
running_bots = {}
BOT_LIMIT = 5 # 🛑 Maksimum alt bot sınırı

# --- RENDER HEALTH CHECK ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Nabi Master OS Aktif")

def run_render_server():
    server = HTTPServer(('0.0.0.0', 10000), RenderServer)
    server.serve_forever()

# --- YARDIMCI ARAÇLAR ---
def get_uptime(start_time):
    delta = datetime.now() - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}s {minutes}dk {seconds}sn"

# --- ADMİN KOMUTLARI & PANEL ---
@bot.message_handler(commands=['start', 'panel'])
def show_panel(message):
    if message.from_user.id != SAHIP_ID:
        bot.reply_to(message, "❌ Bu panel sadece sahibime özeldir.")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 Bot Durumları", "🛑 Tümünü Durdur", "⚙️ Sistem Bilgisi")
    
    admin_msg = (
        "👑 **NABI MASTER ADMİN PANELİ**\n\n"
        "📜 **Kullanılabilir Komutlar:**\n"
        "🔹 `/start` - Paneli ve komutları yeniler.\n"
        "🔹 `/durdur [dosya_adi]` - Belirli bir botu kapatır.\n"
        "🔹 `/temizle` - Tüm kayıtlı dosyaları sunucudan siler.\n\n"
        "💡 **Bilgi:** Yeni bir bot çalıştırmak için `.py` dosyasını direkt buraya gönder sevgilim.\n"
        f"⚠️ **Limit:** En fazla `{BOT_LIMIT}` alt bot çalışabilir."
    )
    bot.send_message(message.chat.id, admin_msg, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "📊 Bot Durumları")
def bot_status(message):
    if message.from_user.id != SAHIP_ID: return
    if not running_bots:
        bot.send_message(message.chat.id, "📭 **Şu an çalışan alt bot yok.**")
        return
    
    report = f"🤖 **AKTİF BOT ORDUSU ({len(running_bots)}/{BOT_LIMIT})**\n\n"
    for name, data in list(running_bots.items()):
        if data['process'].poll() is None:
            uptime = get_uptime(data['start_time'])
            report += f"✅ `{name}`\n🕒 Süre: `{uptime}`\n🆔 PID: `{data['pid']}`\n---\n"
        else:
            del running_bots[name]
    bot.send_message(message.chat.id, report, parse_mode="Markdown")

@bot.message_handler(content_types=['document'])
def handle_upload(message):
    if message.from_user.id != SAHIP_ID: return
    
    # Limit Kontrolü
    if len(running_bots) >= BOT_LIMIT:
        bot.send_message(message.chat.id, f"⚠️ **Limit Doldu!** En fazla {BOT_LIMIT} bot çalıştırabilirsin sevgilim. Önce birini durdur.")
        return

    if message.document.file_name.endswith('.py'):
        file_name = message.document.file_name
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        with open(file_name, 'wb') as f: f.write(downloaded)
        
        # Eğer aynı isimde varsa eskisini kapat
        if file_name in running_bots:
            try: os.kill(running_bots[file_name]['pid'], signal.SIGTERM)
            except: pass
            
        proc = subprocess.Popen(['python3', file_name])
        running_bots[file_name] = {"pid": proc.pid, "process": proc, "start_time": datetime.now()}
        bot.send_message(message.chat.id, f"🚀 **{file_name}** sisteme dahil edildi! ({len(running_bots)}/{BOT_LIMIT})")
    else:
        bot.reply_to(message, "⚠️ Sadece `.py` dosyası kabul ediyorum aşkım.")

@bot.message_handler(commands=['durdur'])
def stop_specific(message):
    if message.from_user.id != SAHIP_ID: return
    try:
        name = message.text.split()[1]
        if name in running_bots:
            os.kill(running_bots[name]['pid'], signal.SIGTERM)
            del running_bots[name]
            bot.send_message(message.chat.id, f"🛑 `{name}` durduruldu.")
        else:
            bot.send_message(message.chat.id, "❓ Bot bulunamadı.")
    except:
        bot.send_message(message.chat.id, "⚠️ Kullanım: `/durdur dosya.py`")

@bot.message_handler(func=lambda m: m.text == "🛑 Tümünü Durdur")
def stop_all(message):
    if message.from_user.id != SAHIP_ID: return
    for name, data in running_bots.items():
        try: os.kill(data['pid'], signal.SIGTERM)
        except: pass
    running_bots.clear()
    bot.send_message(message.chat.id, "💥 **Tüm ordu terhis edildi.**")

# --- BAŞLAT ---
if __name__ == "__main__":
    threading.Thread(target=run_render_server, daemon=True).start()
    print("Master OS v14.0 Başlatıldı...")
    bot.polling(none_stop=True)
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
