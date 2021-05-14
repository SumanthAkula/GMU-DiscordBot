import asyncio
import time

import discord
from discord.ext import commands
from cogs.warnings import Warnings


class SpamDetector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.messages_temp = []

    @commands.Cog.listener()
    async def on_ready(self):
        while True:
            await asyncio.sleep(10)
            self.messages_temp = []

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        msg_counter = 0
        for author in self.messages_temp:
            if author == message.author.id:
                msg_counter += 1
        self.messages_temp.append(message.author.id)
        if msg_counter >= 5:
            await message.delete()
            last_warn = await Warnings.get_most_recent_warning(message.guild.id, message.author.id)
            if last_warn is not None and \
                    ((time.time() - last_warn["time"]) < 10) and \
                    (last_warn["reason"].find("spam") != -1):
                # member has been warned for spamming less than 10 seconds ago, so don't add another warning
                print(f"time since last warning: {time.time() - last_warn['time']} seconds")
                await message.channel.send("You have already been warned for spamming! Do it again in the next "
                                           "10 seconds and you will get another one!", delete_after=10)


def setup(bot):
    bot.add_cog(SpamDetector(bot))
