import asyncio
import sys

# Event loop fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client, filters, idle
from pytgcalls import PyTgCalls
from pytgcalls.types import InputAudioStream  # v1.2.9 ka import
import yt_dlp
import config

app = Client(
    "MusicBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

assistant = Client(
    "Assistant",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.STRING_SESSION
)

call_py = PyTgCalls(assistant)

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text("👋 Hello! Main music bot hoon. Kisi bhi group me mujhe aur mere assistant ko add karein aur /play [song name] likhein.")

@app.on_message(filters.command("play"))
async def play_music(client, message):
    if len(message.command) < 2:
        await message.reply_text("❌ Kripya gaane ka naam likhein. Jaise: /play Faded")
        return

    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    
    m = await message.reply_text("🔍 Gaana khoja ja raha hai...")

    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True,
        'quiet': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch:{query}", download=False)
            if 'entries' in search_results and search_results['entries']:
                song_info = search_results['entries'][0]
            else:
                song_info = search_results
            
            stream_url = song_info['url']
            song_title = song_info['title']
    except Exception as e:
        await m.edit(f"❌ Error: {str(e)}")
        return

    try:
        await m.edit("🎵 Voice Chat me connect kiya ja raha hai...")
        
        # v1.2.9 syntax
        await call_py.join_group_call(
            chat_id,
            InputAudioStream(stream_url)
        )
        await m.edit(f"▶️ Abhi Play ho raha hai: {song_title}")
    except Exception as e:
        await m.edit(f"⚠️ Error: {str(e)}")

async def main():
    await app.start()
    await assistant.start()
    await call_py.start()
    print("🤖 Bot Successfully Start Ho Gaya!")
    await idle()

if __name__ == "__main__":
    loop.run_until_complete(main())
