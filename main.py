import os

import discord
from discord.ext import commands
import pymongo

import secret  # super duper secret .py file used to store the bot token

bot_description = f"This is a bot made by the nerds over in the GMU Computer Science discord server!\n" \
                  f"This specific bot was developed by Sumo Akula on the notsumo_Dev branch"

intents = discord.Intents.all()
activity = discord.Game(name=f"discord.py {discord.__version__}")
bot = commands.Bot(command_prefix=commands.when_mentioned_or(":V "),
                   description=bot_description,
                   strip_after_prefix=True,
                   case_insensitive=True,
                   intents=intents,
                   activity=activity)

# connect to database
db = pymongo.MongoClient(secret.DB_LOCAL_URL)["botdb"]

# load all cogs in the ./cogs folder (that's pretty much every file that ends in .py in that folder)
for f in os.listdir("./cogs"):
    if f.endswith(".py"):
        bot.load_extension(f"cogs.{f[:-3]}")


@bot.event
async def on_ready():
    print("bot started!")


if __name__ == "__main__":
    bot.run(secret.TOKEN)
