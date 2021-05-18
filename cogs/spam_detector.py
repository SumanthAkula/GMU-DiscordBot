import time

import discord
from discord.ext import commands
from cogs.warnings import Warnings


class SpamDetector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return  # message was sent in DM, and we dont need to check for spam in DMs
        member_messages = []
        for m in await message.channel.history(limit=10, before=message, oldest_first=False).flatten():
            if m.author.id == message.author.id and m.guild.id == message.guild.id:
                member_messages.append(m)
        if not member_messages:
            return
        if message.created_at.timestamp() - member_messages[-1].created_at.timestamp() < 10:
            await self.warn(message)

    async def warn(self, message: discord.Message):
        recent = await Warnings.get_most_recent_warning(message.guild.id, message.author.id)
        if recent is None or time.time() - recent["time"] > 10:
            # user has either never been warned before or hasn't been warned in the last 10 seconds, so add a warning
            warn_id = await Warnings(self.bot).add_warning(message.guild.id, message.author.id, 1, "[AUTO] spamming")
            await message.channel.send(
                f":warning: [`{warn_id}`] {message.author.mention}, you have been given a 1 point warning for spamming"
                f"\nIf you keep spamming, you will get another warning!")


def setup(bot):
    bot.add_cog(SpamDetector(bot))
