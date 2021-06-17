import os

import discord
from discord.ext import commands
import pymongo

import secret  # super duper secret .py file used to store the bot token

bot_description = "This is a bot made by the nerds over in the GMU Computer Science discord server!"

intents = discord.Intents.default()
intents.members = True
activity = discord.Game(name="with ur mom")
bot = commands.Bot(command_prefix=":V ",
                   description=bot_description,
                   strip_after_prefix=True,
                   case_insensitive=False,
                   intents=intents,
                   activity=activity)

# connect to database
db = pymongo.MongoClient(secret.DB_REMOTE_URL)["botdb"]

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
@bot.command()
async def load_cog(ctx: commands.Context, cog: str):
    """
    DEVELOPER ONLY DONT FUCK WITH THIS PLS
    """
    bot.load_extension(f"cogs.{cog}")
    await ctx.send(f"loaded {cog}")


@bot.command()
async def unload_cog(ctx: commands.Context, cog: str):
    """
    DEVELOPER ONLY DONT FUCK WITH THIS PLS
    """
    bot.unload_extension(f"cogs.{cog}")
    await ctx.send(f"unloaded {cog}")


if __name__ == "__main__":
    bot.run(secret.TOKEN)
