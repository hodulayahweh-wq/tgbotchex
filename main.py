import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN bulunamadı")

ADMINS = [7690743437]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ================= MENU =================

def main_menu():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("➕ .py Yükle", callback_data="upload"),
    )

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "✅ Ana bot çalışıyor\n\n.py dosya yükleyebilirsin",
        reply_markup=main_menu()
    )

# ================= DOSYA YÜKLE =================

@dp.callback_query_handler(lambda c: c.data == "upload")
async def upload(callback: types.CallbackQuery):
    await callback.message.answer("📂 .py dosyasını gönder")

@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def load_py(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    doc = message.document
    if not doc.file_name.endswith(".py"):
        await message.reply("❌ Sadece .py dosya")
        return

    file = await bot.download_file_by_id(doc.file_id)

    os.makedirs("plugins", exist_ok=True)
    path = f"plugins/{doc.file_name}"

    with open(path, "wb") as f:
        f.write(file.read())

    namespace = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
            exec(code, namespace)

        if "register" not in namespace:
            await message.reply("❌ register(dp) yok")
            return

        namespace["register"](dp)
        await message.reply("✅ Bot yüklendi ve ÇALIŞIYOR")

    except Exception as e:
        await message.reply(f"❌ Hata:\n{e}")

# ================= RUN =================

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)True
