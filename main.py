import discord 
from discord.ext import commands
import asyncio
import yt_dlp
import os 
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Bot config
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store radio stations
RADIO_STATIONS = {
    'lofi': 'https://www.youtube.com/watch?v=jfKfPfyJRdk',
    'jazz': 'https://www.youtube.com/watch?v=Dx5qFachd3A',
    'gagi_jv_mix1': 'https://youtu.be/KTXMCPuYPpg?si=j7SitnmyhXNDMH7P',
    'gagi_jv_mix2': 'https://youtu.be/MZDMWLROx-k?si=I4NUaYxlU1r8CpRq',
    'gagi_jv_mix3': 'https://youtu.be/uoS3tkN25UQ?si=Tjj-gOUv0wT83WCk',
    'gagi_jv_mix4': 'https://youtu.be/Gm2-n2Bjy2E?si=426RLKsXTmsTaCBV',
    'rock200s': 'https://www.youtube.com/live/VbTYnJshTas?si=DjJzQEsflRvijC-u',
    'dens_djcole': 'https://www.youtube.com/watch?v=MBi-sd9H4gg',

}

# yt-dlp options
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)