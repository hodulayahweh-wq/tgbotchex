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
TOKEN = "8454685844:AAH7A83NxhUYwjILHC-wm4yec0jkMBi8j88"
SAHIP_ID = 8258235296 
bot = telebot.TeleBot(TOKEN)
running_bots = {}
BOT_LIMIT = 5 

# --- RENDER HEALTH CHECK ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Nabi Master OS - Toplu Yukleme Aktif")

def run_render_server():
    server = HTTPServer(('0.0.0.0', 10000), RenderServer)
    server.serve_forever()

# --- BAŞLANGIÇ ---
@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_msg = (
        "👋 **Nabi Bot Servisine Hoş Geldiniz!**\n\n"
        "Kendi botlarınızı çalıştırmak için `.py` dosyalarınızı gönderin.\n"
        "🔹 **Toplu İşlem:** Birden fazla dosyayı aynı anda seçip gönderebilirsiniz!\n"
        f"🔹 **Sistem Limiti:** Toplam `{BOT_LIMIT}` bot."
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown")

# --- GİZLİ ADMİN PANELİ ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != SAHIP_ID:
        bot.reply_to(message, "❌ Yetkisiz erişim.")
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📊 Bot Durumları", "🛑 Tümünü Durdur")
    bot.send_message(message.chat.id, "👑 **Admin Paneli Açıldı**", reply_markup=markup)

# --- TOPLU BOT YÜKLEME MANTIĞI ---
@bot.message_handler(content_types=['document'])
def handle_files(message):
    # Toplam Limit Kontrolü
    if len(running_bots) >= BOT_LIMIT:
        bot.send_message(message.chat.id, f"⚠️ Üzgünüm, sistem kapasitesi dolu ({len(running_bots)}/{BOT_LIMIT}).")
        return

    if message.document.file_name.endswith('.py'):
        # Kullanıcının ID'si ve dosya adını birleştirerek çakışmayı önle
        original_name = message.document.file_name
        safe_name = f"u{message.from_user.id}_{original_name}"
        
        # Dosyayı İndir
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            with open(safe_name, 'wb') as f:
                f.write(downloaded)
            
            # Alt Botu Başlat
            proc = subprocess.Popen(['python3', safe_name])
            running_bots[safe_name] = {
                "pid": proc.pid,
                "process": proc,
                "user": message.from_user.first_name,
                "start_time": datetime.now()
            }
            
            bot.send_message(message.chat.id, f"🚀 **{original_name}** başarıyla kuyruğa alındı ve başlatıldı!")
            
            # Yöneticiye (Sana) bilgi ver
            if message.from_user.id != SAHIP_ID:
                bot.send_message(SAHIP_ID, f"🔔 **Yeni Bot:** {message.from_user.first_name} -> `{original_name}`")
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ `{original_name}` başlatılırken hata: {str(e)}")
    else:
        bot.send_message(message.chat.id, f"⚠️ `{message.document.file_name}` Python dosyası değil.")

# --- DURUM LİSTESİ ---
@bot.message_handler(func=lambda m: m.text == "📊 Bot Durumları")
def check_status(message):
    if message.from_user.id != SAHIP_ID: return
    if not running_bots:
        bot.send_message(message.chat.id, "📭 Şu an aktif bot yok.")
        return
    
    report = "🤖 **AKTİF ORDULAR**\n\n"
    for name, data in list(running_bots.items()):
        if data['process'].poll() is None:
            report += f"👤 {data['user']} | 📄 `{name}` | 🆔 `{data['pid']}`\n"
        else:
            del running_bots[name]
    bot.send_message(message.chat.id, report)

@bot.message_handler(func=lambda m: m.text == "🛑 Tümünü Durdur")
def stop_all(message):
    if message.from_user.id != SAHIP_ID: return
    for name, data in running_bots.items():
        try: os.kill(data['pid'], signal.SIGTERM)
        except: pass
    running_bots.clear()
    bot.send_message(message.chat.id, "💥 Tüm botlar durduruldu.")

if __name__ == "__main__":
    threading.Thread(target=run_render_server, daemon=True).start()
    bot.infinity_polling()
umları
