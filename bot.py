import discord
from discord.ext import commands
import aiohttp
import re
import json
import os
import asyncio

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def get_session():
    return aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10),
        headers={"User-Agent": "BypassBot/1.0"}
    )

async def bypass_linkvertise(url):
    try:
        async with await get_session() as s:
            async with s.get(url) as r:
                html = await r.text()
        m = re.search(r'linkvertise\.linkData = ({.+?});', html)
        if m:
            data = json.loads(m.group(1))
            return data.get("target")
    except:
        pass
    return None

async def auto_bypass(url):
    if "linkvertise.com" in url or "work.ink" in url:
        return await bypass_linkvertise(url)
    return None

@bot.event
async def on_ready():
    print(f"{bot.user} (Bypass) is online!")

@bot.command()
async def bypass(ctx, url: str):
    if not url.startswith("http"):
        await ctx.send("Send a full link: `http://...`")
        return
    await ctx.send("🔄 Bypassing...")
    direct = await auto_bypass(url)
    if direct:
        await ctx.send(f"✅ **Bypassed!** \n{direct}")
    else:
        await ctx.send("❌ Could not bypass. Try again later.")

@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    urls = re.findall(r"https?://[^\s]+", msg.content)
    for url in urls:
        if "linkvertise" in url or "work.ink" in url:
            direct = await auto_bypass(url)
            if direct:
                await msg.reply(f"🔗 Bypassed: {direct}")
                break
    await bot.process_commands(msg)

bot.run(os.getenv("DISCORD_TOKEN"))
