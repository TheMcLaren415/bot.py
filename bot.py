import os
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1395001990542528573  # твой сервер

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    # 🔥 Удаляем GUILD-команды
    bot.tree.clear_commands(guild=guild)
    await bot.tree.sync(guild=guild)

    # 🔥 Удаляем GLOBAL-команды
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()

    print("✅ Guild и Global слеш-команды удалены")
    await bot.close()

bot.run(TOKEN)
