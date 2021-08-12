import os

import discord
from discord.ext import commands
import pymongo
from pymongo import errors

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
try:
    db = pymongo.MongoClient(secret.DB_REMOTE_URL)["botdb"]
except pymongo.errors.ConfigurationError:
    print("Connecting to the database took too long! Are you connected to the internet?")
    exit(100)

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
    await bot.process_commands(message)


# TODO: REMOVE THESE ON RELEASE
@bot.command(hidden=True)
async def load_cog(ctx: commands.Context, cog: str):
    bot.load_extension(f"cogs.{cog}")
    await ctx.send(f"loaded {cog}")


@bot.command(hidden=True)
async def unload_cog(ctx: commands.Context, cog: str):
    bot.unload_extension(f"cogs.{cog}")
    await ctx.send(f"unloaded {cog}")


if __name__ == "__main__":
    bot.run(secret.TOKEN)
