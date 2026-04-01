import asyncio
from pyrogram import Client, filters
import yt_dlp
import os
import uuid
from gtts import gTTS
from flask import Flask
import threading

# 🔑 CONFIG
API_ID = 
API_HASH = ""
BOT_TOKEN = ""
ADMIN_ID =   # TU ID

app = Client("yt-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 🌐 WEB (Render)
web = Flask(__name__)

@web.route('/')
def home():
    return "🔥 Bot activo"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web.run(host="0.0.0.0", port=port)

# 🧠 LISTA BAN
usuarios_ban = set()

# 🔒 FILTRO BAN
async def check_ban(user_id):
    return user_id in usuarios_ban

# 🔥 START + BOTÓN
@app.on_message(filters.command("start"))
async def start(client, message):
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    botones = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Donar estrellas", url="https://www.paypal.com/paypalme/cris1470")]
    ])

    await message.reply(
        "🔥 YOUTUBE BOT PRO 🔥\n\n"
        "🎬 /mp4 link\n"
        "🎵 /mp3 link\n"
        "🔊 /voz texto\n",
        reply_markup=botones
    )

# 🔊 VOZ
@app.on_message(filters.command("voz"))
async def voz(client, message):
    if await check_ban(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply("❌ Usa: /voz hola mundo")

    texto = " ".join(message.command[1:])
    file = f"{uuid.uuid4()}.mp3"

    tts = gTTS(text=texto, lang="es")
    tts.save(file)

    await message.reply_audio(file)
    os.remove(file)

# 🎵 MP3
@app.on_message(filters.command("mp3"))
async def mp3(client, message):
    if await check_ban(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply("❌ Usa: /mp3 link")

    url = message.command[1]
    msg = await message.reply("⏳ Descargando audio...")

    file_id = str(uuid.uuid4())

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{file_id}.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3'
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file = f"{file_id}.mp3"
        await msg.delete()
        await message.reply_audio(file)
        os.remove(file)

    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

# 🎬 MP4
@app.on_message(filters.command("mp4"))
async def mp4(client, message):
    if await check_ban(message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply("❌ Usa: /mp4 link")

    url = message.command[1]
    msg = await message.reply("⏳ Descargando video...")

    file_id = str(uuid.uuid4())

    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{file_id}.%(ext)s',
        'quiet': True,
        'merge_output_format': 'mp4'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file = f"{file_id}.mp4"
        await msg.delete()
        await message.reply_video(file)
        os.remove(file)

    except Exception as e:
        await msg.edit(f"❌ Error: {e}")

# 🔨 BAN
@app.on_message(filters.command("ban") & filters.user(ADMIN_ID))
async def ban(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usa: /ban ID")

    user_id = int(message.command[1])
    usuarios_ban.add(user_id)

    await message.reply(f"🔨 Usuario {user_id} baneado")

# 🔓 UNBAN
@app.on_message(filters.command("unban") & filters.user(ADMIN_ID))
async def unban(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ Usa: /unban ID")

    user_id = int(message.command[1])
    usuarios_ban.discard(user_id)

    await message.reply(f"🔓 Usuario {user_id} desbaneado")

# 🚀 RUN
if __name__ == "__main__":
    print("🔥 Bot iniciado")

    threading.Thread(target=run_web, daemon=True).start()

    app.start()
    asyncio.get_event_loop().run_forever()
