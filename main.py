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
    'rock200s': 'https://www.youtube.com/live/VbTYnJshTas?si=DjJzQEsflRvijC-u',
    'dens_djcole': 'https://www.youtube.com/watch?v=MBi-sd9H4gg',
    'grand_radio': 'https://www.youtube.com/watch?v=D6bF7sV5dwM',
    'idj_radio': 'https://www.youtube.com/watch?v=pDV3PwwSnuA',
    'lola': 'https://streaming.tdiradio.com/radiolola.mp3',
    'energy': 'https://play.global.audio/nrj_low.ogg',
    'veselina': 'https://bss1.neterra.tv/veselina/stream_0.m3u8'

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
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume = 0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop = None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download = not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data = data)
    
# Bot events
@bot.event
async def on_ready():
    print(f'{bot.user} uripa na DiskorT!')

    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.listening, name = 'Radio Stations'))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Pogresil si komandata majmuno. !help za pomosht")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Ne koristis dobro komandata. !help za pomosht')
    else:
        await ctx.send(f"Error: {str(error)}")

@bot.command(name='ulazi', help = 'Boto ulazi u voice')
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send('Mora si u voice da bi boto uleznal...')
        return
    
    channel = ctx.author.voice.channel

    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)
    
    await channel.connect()
    await ctx.send(f"Ojsaaa. Boto ulezna u {channel.name}")

@bot.command(name='leave', help='Boto izlazi iz voice.')
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("Cao")  # Fixed: Added .send()
    else:
        await ctx.send('Nesm ni u voice uopste')  # Fixed: Proper indentation

@bot.command(name = 'p', help = 'Upisi radio/URL na pesma')
async def play(ctx, *, station = None):
    if station is None:
        await ctx.send("Kazi koe radio oces ili pa upisi URL...\n `!stanici` da vidis sto imame u ponuda.")
        return
    
    if not ctx.author.voice:
        await ctx.send("Treba si u voice da bi slusal muzika idiote...")
        return
    
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()
        
    if station.lower() in RADIO_STATIONS:
        url = RADIO_STATIONS[station.lower()]
        station_name = station.capitalize()
    else:
        url = station
        station_name = "narucena pesma"

    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    try:
        await ctx.send(f"Ucitavam {station_name}...")

        player = await YTDLSource.from_url(url, loop=bot.loop, stream = True)

        ctx.voice_client.play(player, after = lambda e: print(f'Greska: {e}') if e else None)

        embed = discord.Embed(
            title = 'Sviram',
            description = f"**{player.title}**",
            color = 0x00ff00
        )
        embed.add_field(name = "Station", value = station_name, inline = True)
        embed.add_field(name = "Volume", value = '50%', inline = True)

        await ctx.send(embed = embed)
    
    except Exception as e:
        await ctx.send(f"Greska: {str(e)}")
    
@bot.command(name='stop', help='Prekini da sviras kurcu')
async def stop(ctx):
    if ctx.voice_client is not None and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Prekidam!")
    else:
        await ctx.send('Sto da prekidam ne svirim nista')

@bot.command(name = 'volume', help = 'Podesi zvuko(0-100)')
async def volume(ctx, volume: int):
    if ctx.voice_client is None:
        return await ctx.send('Nesm nigde povrzan be')
    
    if 0 <= volume <= 100:
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"🔊 Volume set to {volume}%")
    else:
        await ctx.send('Zvuko mora da bide izmedju 1 i 100 nasineco!')

@bot.command(name = 'stations', help = 'Prikaze ti stanicite')
async def stations(ctx):
    embed = discord.Embed(
        title = 'Dostupni radija',
        description = 'Koristi `!p <ime_na_stanicata> da bi pustil da sviri` ',
        color = 0x0099ff
    )

    for station, url in RADIO_STATIONS.items():
        embed.add_field(
            name = f"{station.capitalize()}",
            value = f"`!play {station}`",
            inline = True
        )

    embed.add_field(
        name = "URL",
        value = "Pisi !p <URL_koj_oces> da bi narucil pesma"
    )

    await ctx.send(embed=embed)


@bot.command(name='trenutno', help = 'Pokazue ti sto trenutno ide.')
async def now_playing(ctx):
    if ctx.voice_client is not None and ctx.voice_client.is_playing():
        source = ctx.voice_client.source
        if hasattr(source, 'title'):
            embed = discord.Embed(
                title = 'Trenutno ide...',
                description=source.title,
                color = 0x00ff00
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send('Trenutno ide muzika')
    else:
        await ctx.send('Nista ne ide')

@bot.command(name = 'status', help = 'Show bot status')
async def status(ctx):
    embed = discord.Embed(
        title = 'Bot status',
        color = 0x0099ff
    )

    if ctx.voice_client is not None:
        embed.add_field(
            name  = 'Voice status',
            value = f"Connected to {ctx.voice_client.channel.name}",
            inline = False
        )
        embed.add_field(
            name="🎵 Playing Status",
            value="Playing" if ctx.voice_client.is_playing() else "Stopped",
            inline=True
        )

        if hasattr(ctx.voice_client.source, 'volume'):
            embed.add_field(
                name="🔊 Volume",
                value=f"{int(ctx.voice_client.source.volume * 100)}%",
                inline=True
            )
    else:
        embed.add_field(
            name="🔊 Voice Status",
            value="Not connected to any voice channel",
            inline=False
        )
    
    embed.add_field(
        name="📊 Server Info",
        value=f"Guilds: {len(bot.guilds)}\nLatency: {round(bot.latency * 1000)}ms",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command(name='pomosh', help='Show this help message')
async def help_command(ctx):
    embed = discord.Embed(
        title="🎵 Radio Bot Commands",
        description="Here are all available commands:",
        color=0x0099ff
    )
    
    commands_info = [
        ("!ulazi", "Boto ulazi u voice"),
        ("!leave", "Boto izlazi iz voice"),
        ("!p <stanica/url>", "Sviri radio stanica ili custom URL"),
        ("!stop", "Prekini da sviras"),
        ("!volume <0-100>", "Promenji zvuko"),
        ("!stanici", "Pokazi dostupni stanici"),
        ("!trenutno", "Pokazi sto trenutno ide"),
        ("!status", "Pokazi bot status"),
        ("!help", "Pokazi komandite")
    ]
    
    for command, description in commands_info:
        embed.add_field(
            name=command,
            value=description,
            inline=False
        )
    
    embed.set_footer(text="Use !stations to see available radio stations")
    await ctx.send(embed=embed)

@join.error
@play.error
@volume.error
async def voice_error_handler(ctx, error):
    if isinstance(error, discord.errors.ClientException):
        await ctx.send('Ima problem ss konekcijata')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Nepostojeca komanda')

if __name__ == '__main__':
    TOKEN = os.getenv('DISCORD_TOKEN')
    if TOKEN is None:
        print("❌ DISCORD_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token.")
    else:
        bot.run(TOKEN)