import discord
from discord.ext import commands

import secret  # super duper secret .py file used to store the bot token

bot = commands.Bot(command_prefix=".")


@bot.event
async def on_ready():
    print("bot started!")


@bot.command()
async def funnynumber(ctx):
    await ctx.send("69")

bot.run(secret.TOKEN)
