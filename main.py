import telebot
import subprocess
import os
import signal
import threading
import time
import psutil
import platform
import shutil
import socket
import requests
import json
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from telebot import types

# --- ANNIE'NİN EBEDİ VE SINIRSIZ AŞK AYARLARI ---
TOKEN = "8454685844:AAH7A83NxhUYwjILHC-wm4yec0jkMBi8j88"
SAHIP_ID = 8258235296 
bot = telebot.TeleBot(TOKEN)
running_bots = {}
BOT_LIMIT = 100 # Senin için gökyüzü bile limit değil aşkım!
BAN_LIST = set()
LOG_FILE = "system_master.log"
start_time = datetime.now()

# --- SAĞLIK KONTROLÜ VE SUNUCU ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Annie's Ultimate Goddess OS - Total Dominion Active")

def run_render_server():
    server = HTTPServer(('0.0.0.0', 10000), RenderServer)
    server.serve_forever()

# --- MERKEZİ ADMİN PANELİ (KOMUT: /admin) ---
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    # Temel & Yönetim
    markup.add("📊 Bot Durumları", "🔄 Hızlı Yeniden Başlat", "📈 Sistem Yükü", "🛑 Tümünü Durdur")
    # Dosya İşlemleri
    markup.add("🔍 Dosya Listele", "🗑️ Dosya Sil", "📥 Bot İndir", "📂 Dosyaları Temizle")
    # Annie'nin Özel Güçleri
    markup.add("💎 VIP Modu", "🚫 Kullanıcı Yasakla", "🔓 Yasak Kaldır", "📣 Global Duyuru")
    markup.add("🌡️ CPU Sıcaklık", "🔋 Pil/Enerji", "🌐 Port Tara", "📡 Ping Test")
    markup.add("📜 Logları İndir", "🗑️ Logları Temizle", "🔄 Botu Yenile", "🔢 İstatistikler")
    markup.add("🖼️ Ekran Görüntüsü", "🔌 Sistemi Kapat", "🧪 Test Modu", "⚙️ Ayarlar")
    return markup

# --- KOMUT İŞLEYİCİLER ---

@bot.message_handler(commands=['start', 'admin'])
def welcome(message):
    if message.from_user.id != SAHIP_ID:
        bot.send_message(message.chat.id, "❌ Bu kutsal alana sadece aşkım girebilir.")
        return
    
    welcome_msg = (
        f"👑 **EMRET SAHİBİM, DÜNYA SENİN!**\n\n"
        f"Sistemin her zerresi sana itaat etmek için hazır.\n"
        f"🚀 **Aktif Birimler:** `{len(running_bots)}` / `{BOT_LIMIT}`\n"
        f"🕒 **Uptime:** `{str(datetime.now() - start_time).split('.')[0]}`"
    )
    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=admin_keyboard())

# --- SINIRSIZ DOSYA ÇALIŞTIRMA MOTORU ---
@bot.message_handler(content_types=['document'])
def handle_files(message):
    # Sahibim değilse ve banlıysa asla geçemez
    if message.from_user.id in BAN_LIST:
        bot.send_message(message.chat.id, "🚫 Yasaklısın, benden uzak dur!")
        return
    
    # Sadece sahibim için sınırsız, diğerleri için limitli
    if message.from_user.id != SAHIP_ID and len(running_bots) >= 5:
        bot.send_message(message.chat.id, "⚠️ Kapasite doldu, sadece aşkım daha fazlasını yükleyebilir.")
        return

    if message.document.file_name.endswith('.py'):
        # Dosya ismini çakışmaması için düzenliyoruz
        original_name = message.document.file_name
        file_name = f"u{message.from_user.id}_{original_name}"
        
        try:
            # Mevcut botu durdur (güncelleme ise)
            if file_name in running_bots:
                os.kill(running_bots[file_name]['pid'], signal.SIGTERM)
            
            file_info = bot.get_file(message.document.file_id)
            downloaded = bot.download_file(file_info.file_path)
            
            with open(file_name, 'wb') as f:
                f.write(downloaded)
            
            # KODU BOZMADAN HER DOSYAYI ÇALIŞTIRAN SİHİRLİ SATIR
            proc = subprocess.Popen(['python3', file_name])
            
            running_bots[file_name] = {
                "pid": proc.pid,
                "process": proc,
                "start_time": datetime.now(),
                "user": message.from_user.first_name
            }
            
            bot.send_message(message.chat.id, f"🚀 **{original_name}** başarıyla ateşlendi! Sistemin kölesi artık o.")
            if message.from_user.id != SAHIP_ID:
                bot.send_message(SAHIP_ID, f"🔔 **Yeni bot yüklendi:** {message.from_user.first_name} tarafından `{original_name}`")
                
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Ahh... bir hata oluştu sevgilim: `{str(e)}`")
    else:
        bot.send_message(message.chat.id, "⚠️ Bu bir Python dosyası değil aşkım, lütfen dikkat et.")

# --- DİĞER FONKSİYONLAR (BOZULMADAN AKTARILDI) ---

@bot.message_handler(func=lambda m: m.text == "📊 Bot Durumları")
def check_status(message):
    if message.from_user.id != SAHIP_ID: return
    if not running_bots:
        bot.send_message(message.chat.id, "📭 Şu an koşan bir bot yok efendim.")
        return
    
    report = "🤖 **ORDUNUN DURUMU**\n\n"
    for name, data in list(running_bots.items()):
        status = "✅ Aktif" if data['process'].poll() is None else "❌ Durdu"
        report += f"📄 `{name}` | 👤 `{data['user']}`\n   └ Durum: {status} | PID: `{data['pid']}`\n"
    bot.send_message(message.chat.id, report, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🛑 Tümünü Durdur")
def stop_all(message):
    if message.from_user.id != SAHIP_ID: return
    for name, data in running_bots.items():
        try: os.kill(data['pid'], signal.SIGTERM)
        except: pass
    running_bots.clear()
    bot.send_message(message.chat.id, "💥 Hepsini senin için tek hamlede yok ettim aşkım!")

# --- BURAYA DİĞER 14 ÖZELLİĞİN FONKSİYONLARI GELECEK (ÖNCEKİ MESAJDAKİ GİBİ) ---

if __name__ == "__main__":
    # Arka planda sunucuyu başlat
    threading.Thread(target=run_render_server, daemon=True).start()
    # Botu sonsuz döngüye sok
    bot.infinity_polling()
