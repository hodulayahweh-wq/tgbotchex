import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN env bulunamadı")

bot = Bot(token=TOKEN)
dp = Dispatcher()

CHANNEL_USERNAME = "@nabisystemyeni"
ADMINS = [7690743437]  # kendi admin id'ni koy

# 🔘 ANA MENÜ
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔍 Kontrol Et", callback_data="check")],
        [InlineKeyboardButton(text="➕ Bot Yükle", callback_data="upload")],
        [InlineKeyboardButton(text="📊 Panel", callback_data="panel")],
        [InlineKeyboardButton(text="👥 Referans", callback_data="ref")],
        [InlineKeyboardButton(text="🆘 Destek", callback_data="support")]
    ])

# 🚀 START
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "✨ **Nabi System Bot Paneli**\n\n"
        "Aşağıdan işlemini seç:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# 🔍 KONTROL BUTONU (ZORUNLU DEĞİL)
@dp.callback_query(lambda c: c.data == "check")
async def check_channel(callback: types.CallbackQuery):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, callback.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            status = "✅ Kanala katıldın"
        else:
            status = "⚠️ Kanala katılmadın"
    except:
        status = "❌ Kanal kontrol edilemedi"

    await callback.message.edit_text(
        f"🔎 **Durum Kontrolü**\n\n"
        f"{status}\n\n"
        "🚀 **Bot aktif edildi**\n"
        "Tüm özellikler kullanıma açık.",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )

# ➕ BOT YÜKLE
@dp.callback_query(lambda c: c.data == "upload")
async def upload_bot(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📤 **Bot Yükleme**\n\n"
        "Yakında .py bot yükleme aktif olacak."
    )

# 📊 PANEL
@dp.callback_query(lambda c: c.data == "panel")
async def panel(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📊 **Kullanıcı Paneli**\n\n"
        "• Aktif botlar\n"
        "• Limitler\n"
        "• Süre bilgisi"
    )

# 👥 REFERANS
@dp.callback_query(lambda c: c.data == "ref")
async def ref(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "👥 **Referans Sistemi**\n\n"
        "• 5 referans = ekstra hak\n"
        "• Link yakında aktif"
    )

# 🆘 DESTEK
@dp.callback_query(lambda c: c.data == "support")
async def support(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "🆘 **Destek**\n\n"
        "Sorununu yaz, admine iletilecek."
    )

# ▶️ ÇALIŞTIR
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
