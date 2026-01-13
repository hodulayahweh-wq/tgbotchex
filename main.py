import telebot
import os
import subprocess

TOKEN = "8511366974:AAGP2gCMLAaKl4d31G0PblrWAwSy5gpxqwU"
bot = telebot.TeleBot(TOKEN)

BASE_DIR = "projects"
os.makedirs(BASE_DIR, exist_ok=True)

running = {}  # user_id: process

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(
        m.chat.id,
        "🤖 Bot Hosting Panel\n\n"
        "/newproject - Bot yükle\n"
        "/stop - Bot durdur\n"
        "/status - Durum"
    )

@bot.message_handler(commands=['newproject'])
def new_project(m):
    bot.send_message(m.chat.id, "📤 bot.py dosyanı gönder")

@bot.message_handler(content_types=['document'])
def handle_file(m):
    if not m.document.file_name.endswith(".py"):
        bot.send_message(m.chat.id, "❌ Sadece .py dosyası")
        return

    user_dir = f"{BASE_DIR}/{m.chat.id}"
    os.makedirs(user_dir, exist_ok=True)

    file_info = bot.get_file(m.document.file_id)
    downloaded = bot.download_file(file_info.file_path)

    path = f"{user_dir}/bot.py"
    with open(path, "wb") as f:
        f.write(downloaded)

    process = subprocess.Popen(
        ["python", "bot.py"],
        cwd=user_dir
    )

    running[m.chat.id] = process
    bot.send_message(m.chat.id, "✅ Bot çalıştırıldı")

@bot.message_handler(commands=['stop'])
def stop_bot(m):
    proc = running.get(m.chat.id)
    if proc:
        proc.terminate()
        bot.send_message(m.chat.id, "🛑 Bot durduruldu")
        del running[m.chat.id]
    else:
        bot.send_message(m.chat.id, "❌ Çalışan bot yok")

@bot.message_handler(commands=['status'])
def status(m):
    if m.chat.id in running:
        bot.send_message(m.chat.id, "🟢 Bot çalışıyor")
    else:
        bot.send_message(m.chat.id, "🔴 Bot kapalı")

bot.infinity_polling()
