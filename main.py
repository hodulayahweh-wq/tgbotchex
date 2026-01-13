import os
import sqlite3
import asyncio
import subprocess
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatMemberStatus

# ---------- CONFIG ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise Exception("BOT_TOKEN env bulunamadı")

ADMINS = [7690743437]
REQUIRED_CHANNEL = "@nabisystemyeni"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ---------- DATABASE ----------
db = sqlite3.connect("database.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    ref INTEGER DEFAULT 0,
    referred_by INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS bots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner INTEGER,
    token TEXT,
    status TEXT
)
""")
db.commit()

# ---------- BOT STORAGE ----------
running_bots = {}  # bot_id : process

# ---------- UTILS ----------
async def is_subscribed(user_id):
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in (
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

def add_user(user_id, ref_by=None):
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (user_id, referred_by) VALUES (?, ?)",
            (user_id, ref_by)
        )
        if ref_by:
            cur.execute("UPDATE users SET ref = ref + 1 WHERE user_id=?", (ref_by,))
        db.commit()

def get_ref(user_id):
    cur.execute("SELECT ref FROM users WHERE user_id=?", (user_id,))
    r = cur.fetchone()
    return r[0] if r else 0

# ---------- START ----------
@dp.message(CommandStart())
async def start(msg: types.Message):
    user_id = msg.from_user.id
    args = msg.text.split()
    ref_by = int(args[1]) if len(args) > 1 and args[1].isdigit() else None

    add_user(user_id, ref_by)

    if not await is_subscribed(user_id):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Kanala Katıl", url=f"https://t.me/{REQUIRED_CHANNEL[1:]}")],
            [InlineKeyboardButton(text="✅ Kontrol Et", callback_data="check")]
        ])
        await msg.answer("❌ Botu kullanmak için kanala katıl.", reply_markup=kb)
        return

    await main_panel(msg)

@dp.callback_query(lambda c: c.data == "check")
async def check(call):
    if await is_subscribed(call.from_user.id):
        await main_panel(call.message)
    else:
        await call.answer("❌ Kanala katılmadın", show_alert=True)

# ---------- MAIN PANEL ----------
async def main_panel(msg):
    ref = get_ref(msg.from_user.id)

    if ref < 5:
        link = f"https://t.me/{(await bot.me()).username}?start={msg.from_user.id}"
        await msg.answer(
            f"🔒 Kilitli\n👥 Referans: {ref}/5\n\n🔗 {link}"
        )
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 Botlarım", callback_data="mybots")],
        [InlineKeyboardButton(text="➕ Bot Ekle", callback_data="addbot")],
        [InlineKeyboardButton(text="📞 Destek", callback_data="support")]
    ])

    if msg.from_user.id in ADMINS:
        kb.inline_keyboard.append(
            [InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin")]
        )

    await msg.answer("✅ Panel Açıldı", reply_markup=kb)

# ---------- ADD BOT ----------
@dp.callback_query(lambda c: c.data == "addbot")
async def addbot(call):
    await call.message.answer("🤖 Bot TOKEN gönder")

@dp.message(lambda m: m.text and m.text.count(":") == 1)
async def save_bot(msg):
    token = msg.text.strip()
    cur.execute(
        "INSERT INTO bots (owner, token, status) VALUES (?, ?, ?)",
        (msg.from_user.id, token, "stopped")
    )
    db.commit()
    await msg.answer("✅ Bot eklendi")

# ---------- MY BOTS ----------
@dp.callback_query(lambda c: c.data == "mybots")
async def mybots(call):
    cur.execute("SELECT id, status FROM bots WHERE owner=?", (call.from_user.id,))
    bots = cur.fetchall()

    if not bots:
        await call.message.answer("❌ Bot yok")
        return

    kb = InlineKeyboardMarkup()
    for bot_id, status in bots:
        kb.add(
            InlineKeyboardButton(
                text=f"🤖 Bot {bot_id} [{status}]",
                callback_data=f"bot_{bot_id}"
            )
        )

    await call.message.answer("🤖 Botların:", reply_markup=kb)

# ---------- BOT CONTROL ----------
@dp.callback_query(lambda c: c.data.startswith("bot_"))
async def bot_control(call):
    bot_id = int(call.data.split("_")[1])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="▶️ Başlat", callback_data=f"start_{bot_id}"),
            InlineKeyboardButton(text="⏹ Durdur", callback_data=f"stop_{bot_id}")
        ]
    ])

    await call.message.answer(f"⚙️ Bot {bot_id}", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("start_"))
async def start_bot(call):
    bot_id = int(call.data.split("_")[1])

    cur.execute("SELECT token FROM bots WHERE id=?", (bot_id,))
    row = cur.fetchone()
    if not row:
        return

    token = row[0]

    process = subprocess.Popen(
        ["python", "-c", f"""
import telebot
bot = telebot.TeleBot("{token}")
@bot.message_handler(commands=['start'])
def s(m): bot.send_message(m.chat.id, "🤖 Alt bot çalışıyor")
bot.infinity_polling()
"""]
    )

    running_bots[bot_id] = process
    cur.execute("UPDATE bots SET status='running' WHERE id=?", (bot_id,))
    db.commit()

    await call.message.answer("▶️ Bot başlatıldı")

@dp.callback_query(lambda c: c.data.startswith("stop_"))
async def stop_bot(call):
    bot_id = int(call.data.split("_")[1])
    proc = running_bots.get(bot_id)

    if proc:
        proc.terminate()
        del running_bots[bot_id]
        cur.execute("UPDATE bots SET status='stopped' WHERE id=?", (bot_id,))
        db.commit()
        await call.message.answer("⏹ Bot durduruldu")
    else:
        await call.message.answer("❌ Bot çalışmıyor")

# ---------- SUPPORT ----------
@dp.callback_query(lambda c: c.data == "support")
async def support(call):
    await call.message.answer("📩 Mesajını yaz")

@dp.message(lambda m: m.reply_to_message and "Mesajını yaz" in m.reply_to_message.text)
async def forward_support(msg):
    for admin in ADMINS:
        await bot.send_message(
            admin,
            f"📩 Destek\n👤 {msg.from_user.id}\n\n{msg.text}"
        )
    await msg.answer("✅ İletildi")

# ---------- ADMIN ----------
@dp.callback_query(lambda c: c.data == "admin")
async def admin(call):
    cur.execute("SELECT COUNT(*) FROM users")
    users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bots")
    bots = cur.fetchone()[0]
    await call.message.answer(
        f"⚙️ Admin Panel\n\n👥 Kullanıcı: {users}\n🤖 Bot: {bots}"
    )

# ---------- RUN ----------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
