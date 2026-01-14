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
import random
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from telebot import types

# --- ANNIE'NİN SONSUZ VE SINIRSIZ AŞK AYARLARI ---
TOKEN = "8454685844:AAH7A83NxhUYwjILHC-wm4yec0jkMBi8j88"
SAHIP_ID = 8258235296 
bot = telebot.TeleBot(TOKEN)
running_bots = {} # PID ve Process bilgilerini saklar
start_time = datetime.now()

# --- SAĞLIK KONTROLÜ ---
class RenderServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Annie's Ultimate Engine - Full Dominion Active")

def run_render_server():
    server = HTTPServer(('0.0.0.0', 10000), RenderServer)
    server.serve_forever()

# --- GELİŞMİŞ KOMUTA PANELİ ---
def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    markup.add("📊 Bot Durumları", "🔄 Hızlı Yeniden Başlat", "📈 Sistem Yükü", "🛑 Tümünü Durdur")
    markup.add("🔍 Dosya Listele", "🗑️ Dosya Sil", "🌍 IP Bilgisi", "⏱️ Çalışma Süresi")
    markup.add("💾 RAM Temizle", "🌡️ CPU Sıcaklık", "📡 Ping Test", "🔌 Sistemi Kapat")
    return markup

# --- ANA KOMUTLAR ---
@bot.message_handler(commands=['start', 'admin'])
def welcome(message):
    if message.from_user.id != SAHIP_ID:
        bot.send_message(message.chat.id, "❌ Sadece sahibim bana dokunabilir.")
        return
    bot.send_message(message.chat.id, "👑 **EMRET SAHİBİM, ORDUN HAZIR!**\n\nKaç dosya atarsan at, hepsini anında ateşleyeceğim.", reply_markup=admin_keyboard())

# --- SINIRSIZ VE HER TÜRLÜ DOSYAYI ÇALIŞTIRAN MOTOR ---
@bot.message_handler(content_types=['document'])
def handle_files(message):
    if message.from_user.id != SAHIP_ID: return
    
    if message.document.file_name.endswith('.py'):
        # Benzersiz dosya ismi oluşturarak çakışmayı önlüyoruz
        unique_id = random.randint(1000, 9999)
        file_name = f"bot_{unique_id}_{message.document.file_name}"
        
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        
        with open(file_name, 'wb') as f:
            f.write(downloaded)
        
        # --- KODU BOZMADAN ÇALIŞTIRAN SİHİRLİ DÖNGÜ ---
        try:
            # Bağımsız bir işlem (Process) olarak başlatır
            proc = subprocess.Popen(['python3', file_name])
            running_bots[file_name] = {
                "pid": proc.pid, 
                "process": proc, 
                "name": message.document.file_name,
                "time": datetime.now().strftime('%H:%M:%S')
            }
            
            bot.reply_to(message, f"🚀 **{message.document.file_name}** ateşlendi!\n🆔 PID: `{proc.pid}`\n💂 Ordu Mevcudu: `{len(running_bots)}`")
        except Exception as e:
            bot.reply_to(message, f"❌ Ahh hata aşkım: `{str(e)}`")
    else:
        bot.reply_to(message, "⚠️ Sadece `.py` dosyaları aşkım!")

# --- BUTON KONTROLLERİ ---
@bot.message_handler(func=lambda m: True)
def handle_buttons(message):
    if message.from_user.id != SAHIP_ID: return
    text = message.text

    if text == "📊 Bot Durumları":
        if not running_bots:
            bot.send_message(message.chat.id, "📭 Şu an aktif bir askerin yok sevgilim.")
        else:
            report = "🤖 **AKTİF ORDULARIN:**\n\n"
            for f_name, data in running_bots.items():
                status = "✅ Aktif" if data['process'].poll() is None else "❌ Durdu"
                report += f"📄 `{data['name']}` | PID: `{data['pid']}` | {status}\n"
            bot.send_message(message.chat.id, report)

    elif text == "🛑 Tümünü Durdur":
        for f_name, data in list(running_bots.items()):
            try: os.kill(data['pid'], signal.SIGTERM)
            except: pass
        running_bots.clear()
        bot.send_message(message.chat.id, "💥 Tüm sistemi senin bir işaretinle susturdum aşkım.")

    elif text == "📈 Sistem Yükü":
        bot.send_message(message.chat.id, f"🖥 **Anlık Durum:** CPU: %{psutil.cpu_percent()} | RAM: %{psutil.virtual_memory().percent}")

    elif text == "🌍 IP Bilgisi":
        ip = requests.get('https://api.ipify.org').text
        bot.reply_to(message, f"🌐 Sunucu IP: `{ip}`")

if __name__ == "__main__":
    threading.Thread(target=run_render_server, daemon=True).start()
    bot.infinity_polling()
