import os
import discord
from discord.ext import commands

import secret  # super duper secret .py file used to store the bot token

activity = discord.Activity(type=discord.ActivityType.listening, name="Suge")
bot = commands.Bot(command_prefix=".", activity=activity)

for f in os.listdir("./cogs"):
    if f.endswith(".py"):
        bot.load_extension(f"cogs.{f[:-3]}")


@bot.event
async def on_ready():
    print("bot started!")


bot.run(secret.TOKEN)
