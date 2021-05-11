import discord
from discord.ext import commands

import secret

bot = commands.Bot(command_prefix=".")


@bot.event
async def on_ready():
    print("bot started!")


bot.run(secret.TOKEN)
