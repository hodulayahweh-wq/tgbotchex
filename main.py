import os
import json
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN env bulunamadı")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

BASE_DIR = "user_bots"
os.makedirs(BASE_DIR, exist_ok=True)

running = {}  # user_id: process

# ================== START ==================

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("➕ Bot Yükle (.py)", callback_data="upload"),
        InlineKeyboardButton("🛑 Bot Durdur", callback_data="stop"),
        InlineKeyboardButton("📊 Durum", callback_data="status"),
    )
    await message.answer(
        "🤖 *Render Bot Çalıştırıcı*\n\n"
        "• .py dosyanı gönder\n"
        "• Bot çalışsın\n\n"
        "⚠️ Render restart olursa bot kapanır",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ================== UPLOAD ==================

@dp.callback_query_handler(lambda c: c.data == "upload")
async def upload(callback: types.CallbackQuery):
    await callback.message.answer("📤 Çalıştırmak istediğin **.py** dosyasını gönder")

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def handle_py(message: types.Message):
    if not message.document.file_name.endswith(".py"):
        await message.reply("❌ Sadece .py dosyası")
        return

    uid = str(message.from_user.id)
    user_dir = os.path.join(BASE_DIR, uid)
    os.makedirs(user_dir, exist_ok=True)

    file_info = await bot.get_file(message.document.file_id)
    file_path = os.path.join(user_dir, "bot.py")

    await bot.download_file(file_info.file_path, file_path)

    # Çalıştır
    process = subprocess.Popen(
        ["python", "bot.py"],
        cwd=user_dir
    )

    running[uid] = process

    await message.reply("✅ Bot çalıştırıldı")

# ================== DURUM ==================

@dp.callback_query_handler(lambda c: c.data == "status")
async def status(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    if uid in running and running[uid].poll() is None:
        await callback.message.answer("🟢 Bot çalışıyor")
    else:
        await callback.message.answer("🔴 Bot kapalı")

# ================== STOP ==================

@dp.callback_query_handler(lambda c: c.data == "stop")
async def stop(callback: types.CallbackQuery):
    uid = str(callback.from_user.id)
    proc = running.get(uid)

    if proc and proc.poll() is None:
        proc.terminate()
        del running[uid]
        await callback.message.answer("🛑 Bot durduruldu")
    else:
        await callback.message.answer("❌ Çalışan bot yok")

# ================== RUN ==================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
