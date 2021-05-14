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
        member_messages = []
        for m in (await message.channel.history(limit=10).flatten()):
            if m.author.id == message.author.id and m.guild.id == message.guild.id:
                member_messages.append(m)
        if member_messages[0].created_at.timestamp() - member_messages[-1].created_at.timestamp() < 10:
            for m in member_messages:
                await m.delete()
                member_messages.remove(m)
            print("spamming detected!")


def setup(bot):
    bot.add_cog(SpamDetector(bot))
