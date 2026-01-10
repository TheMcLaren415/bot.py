import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import re
import os

# TOKEN берём из переменной окружения
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise RuntimeError("❌ Переменная окружения TOKEN не найдена")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==================== ПАРСЕР ВРЕМЕНИ ====================
def parse_time(time_str: str):
    time_str = time_str.replace(" ", "").lower()
    match = re.fullmatch(r"(\d+)([smhdсмчд])", time_str)
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    mapping = {
        "s": timedelta(seconds=value),
        "m": timedelta(minutes=value),
        "h": timedelta(hours=value),
        "d": timedelta(days=value),
        "с": timedelta(seconds=value),
        "м": timedelta(minutes=value),
        "ч": timedelta(hours=value),
        "д": timedelta(days=value)
    }
    return mapping[unit]

# ==================== ПРАВА ====================
def has_access(ctx):
    return ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.moderate_members

# ==================== EMBED ====================
def build_mute_embed(member, time, reason, author):
    embed = discord.Embed(color=0x9b59b6)
    embed.description = (
        "<a:7870redflyingheart:1459453296422027469> **Squad 875 Team** <a:7870redflyingheart:1459453296422027469>\n\n"
        f"1. Вы были наказаны Персоналом <:378490ban:1459454963334910148>\n"
        f"2. Тип наказания **Тайм-Аут** <a:88094loading:1459453760190550058>\n"
        f"3. Длительность **{time}** <a:689495aec:1459453590333558848>\n"
        f"4. Причина **{reason}** <a:655233greensparklies:1459449234955964499>\n"
        f"5. Кто выдал **{author}** <:378490ban:1459454963334910148>"
    )
    return embed

def build_unmute_embed(member, reason, author):
    if not reason:
        reason = "Без причины"
    embed = discord.Embed(color=0x1abc9c)
    embed.description = (
        "<a:7870redflyingheart:1459453296422027469> **Squad 875 Team** <a:7870redflyingheart:1459453296422027469>\n\n"
        f"1. Вы были размьючены Персоналом <:378490ban:1459454963334910148>\n"
        f"2. Тип наказания **Тайм-Аут был снят** <a:88094loading:1459453760190550058>\n"
        f"3. Длительность **Снят** <a:689495aec:1459453590333558848>\n"
        f"4. Причина **{reason}** <a:655233greensparklies:1459449234955964499>\n"
        f"5. Кто снял **{author}** <:378490ban:1459454963334910148>"
    )
    return embed

# ==================== КОМАНДА МЬЮТ ====================
@bot.command(name="мьют")
async def mute(ctx, *args):
    if not has_access(ctx):
        await ctx.reply("❌ У тебя нет прав для выдачи тайм-аута")
        return

    member = None
    time_str = None
    reason = "Не указана"

    content = ctx.message.content[len(ctx.prefix + ctx.command.name):].strip()

    # Пинг
    if ctx.message.mentions:
        member = ctx.message.mentions[0]
        # удаляем упоминание из текста
        content = content.replace(f"<@!{member.id}>", "").strip()
        parts = content.split()
        if len(parts) >= 1:
            time_str = parts[0]
            if len(parts) > 1:
                reason = " ".join(parts[1:])
    # Ответ на сообщение
    elif ctx.message.reference:
        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = msg.author
        parts = content.split()
        if len(parts) >= 1:
            time_str = parts[0]
            if len(parts) > 1:
                reason = " ".join(parts[1:])

    if not member or not time_str:
        await ctx.reply("❌ Использование: `!мьют @пинг 10s/10с причина` или ответом `!мьют 10s/10с причина`")
        return

    if member == ctx.author or member == ctx.guild.me or (member.top_role >= ctx.author.top_role and not ctx.author.guild_permissions.administrator):
        await ctx.reply("❌ Нельзя замьютить этого пользователя")
        return

    duration = parse_time(time_str)
    if not duration:
        await ctx.reply("❌ Неверный формат времени (`s/m/h/d` или `с/м/ч/д`)")
        return

    try:
        await member.timeout(duration, reason=reason)
    except discord.Forbidden:
        await ctx.reply("❌ Недостаточно прав")
        return

    embed = build_mute_embed(member, time_str, reason, ctx.author)
    try:
        await member.send(embed=embed)
    except:
        pass

    await ctx.reply(f"✅ {member.mention} получил тайм-аут на **{time_str}**")

# ==================== КОМАНДА РАЗМЬЮТ ====================
@bot.command(name="размьют")
async def unmute(ctx, *args):
    if not has_access(ctx):
        await ctx.reply("❌ У тебя нет прав для снятия тайм-аута")
        return

    member = None
    reason = ""

    content = ctx.message.content[len(ctx.prefix + ctx.command.name):].strip()

    # Пинг
    if ctx.message.mentions:
        member = ctx.message.mentions[0]
        content = content.replace(f"<@!{member.id}>", "").strip()
        if content:
            reason = content
    # Ответ
    elif ctx.message.reference:
        msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        member = msg.author
        if content:
            reason = content

    if not member:
        await ctx.reply("❌ Использование: `!размьют @пинг причина (необязательно)` или ответом")
        return

    if member == ctx.guild.me:
        await ctx.reply("❌ Я не могу снять тайм-аута себе")
        return

    try:
        await member.edit(timed_out_until=None)
    except discord.Forbidden:
        await ctx.reply("❌ Недостаточно прав")
        return

    embed = build_unmute_embed(member, reason, ctx.author)
    try:
        await member.send(embed=embed)
    except:
        pass

    await ctx.reply(f"✅ {member.mention} тайм-аут снят")

# ==================== SLASH COMMANDS ====================
class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mute", description="Выдать тайм-аут пользователю")
    @app_commands.describe(member="Пользователь", time="Длительность (10s/5m/2h/1d или 10с/5м/2ч/1д)", reason="Причина")
    async def slash_mute(self, interaction: discord.Interaction, member: discord.Member, time: str, reason: str = "Не указана"):
        if not (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.moderate_members):
            await interaction.response.send_message("❌ У тебя нет прав", ephemeral=True)
            return

        if member == interaction.user or member == interaction.guild.me or (member.top_role >= interaction.user.top_role and not interaction.user.guild_permissions.administrator):
            await interaction.response.send_message("❌ Нельзя замьютить этого пользователя", ephemeral=True)
            return

        duration = parse_time(time)
        if not duration:
            await interaction.response.send_message("❌ Неверный формат времени", ephemeral=True)
            return

        try:
            await member.timeout(duration, reason=reason)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Недостаточно прав", ephemeral=True)
            return

        embed = build_mute_embed(member, time, reason, interaction.user)
        try:
            await member.send(embed=embed)
        except:
            pass

        await interaction.response.send_message(f"✅ {member.mention} получил тайм-аут на **{time}**")

    @app_commands.command(name="unmute", description="Снять тайм-аут пользователя")
    @app_commands.describe(member="Пользователь", reason="Причина (необязательно)")
    async def slash_unmute(self, interaction: discord.Interaction, member: discord.Member, reason: str = ""):
        if not (interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.moderate_members):
            await interaction.response.send_message("❌ У тебя нет прав", ephemeral=True)
            return

        if member == interaction.guild.me:
            await interaction.response.send_message("❌ Я не могу снять тайм-аута себе", ephemeral=True)
            return

        try:
            await member.edit(timed_out_until=None)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Недостаточно прав", ephemeral=True)
            return

        embed = build_unmute_embed(member, reason, interaction.user)
        try:
            await member.send(embed=embed)
        except:
            pass

        await interaction.response.send_message(f"✅ {member.mention} тайм-аут снят")

bot.add_cog(Mute(bot))

bot.run(TOKEN)
