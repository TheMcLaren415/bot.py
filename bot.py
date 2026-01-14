import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.clear_commands()
    await bot.tree.sync()
    print("Slash-команды удалены")

bot.run(TOKEN)
