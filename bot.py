import discord
from discord.ext import commands
from datetime import timedelta
import re
import os

# Берём токен из переменных окружения
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("❌ Переменная окружения TOKEN не найдена")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Парсер времени: s / m / h / d
def parse_time(time_str: str):
    match = re.fullmatch(r"(\d+)(s|m|h|d)", time_str.lower())
    if not match:
        return None

    value, unit = match.groups()
    value = int(value)

    return {
        "s": timedelta(seconds=value),
        "m": timedelta(minutes=value),
        "h": timedelta(hours=value),
        "d": timedelta(days=value),
    }[unit]

@bot.event
async def on_ready():
    print(f"✅ Бот запущен: {bot.user}")

@bot.command(name="мьют")
@commands.has_permissions(moderate_members=True)
@commands.bot_has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member = None, time: str = None, *, reason: str = "Не указана"):

    # Если команда ответом
    if ctx.message.reference and not member:
        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = msg.author

    if not member or not time:
        await ctx.reply("❌ Использование: `!мьют @пользователь 10s причина`")
        return

    # Проверки
    if member == ctx.author:
        await ctx.reply("❌ Нельзя выдать тайм-аут самому себе")
        return

    if member == ctx.guild.me:
        await ctx.reply("❌ Я не могу выдать тайм-аут себе")
        return

    if member.top_role >= ctx.author.top_role:
        await ctx.reply("❌ У пользователя роль выше или равна вашей")
        return

    duration = parse_time(time)
    if not duration:
        await ctx.reply("❌ Неверный формат времени (`s/m/h/d`)")
        return

    try:
        await member.timeout(duration, reason=reason)
    except discord.Forbidden:
        await ctx.reply("❌ Недостаточно прав")
        return

    # RU + EN embed в ЛС
    embed = discord.Embed(color=0x9b59b6)
    embed.description = (
        "<a:stars:1404966549932216340>  **Squad 875 Team** <a:stars:1404966549932216340>\n\n"

        "<:white_one:1227916018182131745> **Вы были наказаны Персоналом**\n"
        "**You have been punished by the staff**\n\n"

        "<:number_two:1227916035785621596> **Тип наказания:** Тайм-Аут\n"
        "**Punishment type:** Timeout\n\n"

        f"<:number_three:1227916051015274587> **Длительность:** {time}\n"
        f"**Duration:** {time}\n\n"

        f"<:4_:1140242031080378508> **Причина:** {reason}\n"
        f"**Reason:** {reason}\n\n"

        f"<:5_:1140242066920718377> **Кто выдал:** {ctx.author}\n"
        f"**Issued by:** {ctx.author}"
    )

    try:
        await member.send(embed=embed)
    except:
        pass

    await ctx.reply(f"✅ {member.mention} получил тайм-аут на **{time}**")

@mute.error
async def mute_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ У тебя нет права **Moderate Members**")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.reply("❌ У бота нет права **Moderate Members**")

bot.run(TOKEN)
