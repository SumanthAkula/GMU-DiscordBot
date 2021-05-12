import os

import discord
from discord.ext import commands
import pymongo

import secret  # super duper secret .py file used to store the bot token

activity = discord.Activity(type=discord.ActivityType.listening, name="Suge")
bot = commands.Bot(command_prefix=">", activity=activity)

# connect to database
db = pymongo.MongoClient(secret.DB_URL)["botdb"]

for f in os.listdir("./cogs"):
    if f.endswith(".py"):
        bot.load_extension(f"cogs.{f[:-3]}")


@bot.event
async def on_ready():
    print("bot started!")


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    if message.content.find("ayy") != -1:
        await message.channel.send("lmao")

bot.run(secret.TOKEN)
