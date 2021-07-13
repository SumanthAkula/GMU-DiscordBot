import time

import discord
from discord.ext import commands, tasks


class SpamDetector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache: [discord.Message] = []

    @commands.Cog.listener()
    async def on_ready(self):
        self.clear_cache.start()

    @tasks.loop(seconds=10)
    async def clear_cache(self):
        self.message_cache = []

    async def on_tenth_message(self, messages: [discord.Message]):
        # check if the last 10 messages were all sent within 5 seconds of each other
        if messages[-1].created_at.timestamp() - messages[0].created_at.timestamp() > 5:
            return
        await self.warn(messages[0])

        # clear author from cache after warning has been given
        for message in self.message_cache:
            if message.author.id == messages[0].author.id and message.guild.id == messages[0].guild.id:
                self.message_cache.remove(message)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        if message.guild is None:
            return  # message was sent in DM, and we dont need to check for spam in DMs

        self.message_cache.append(message)  # add message to cache

        # get all messages in the cache sent by the user that sent the message passed in
        messages = \
            [m for m in self.message_cache if m.author.id ==
                message.author.id and m.guild.id == message.guild.id]
        if len(messages) >= 10:     # if they sent 10 messages, check if they're spam
            await self.on_tenth_message(messages)

    async def warn(self, message: discord.Message):
        recent = await self.bot.get_cog("Warnings").get_most_recent_warning(message.guild.id, message.author.id)
        if recent is None or time.time() - recent["time"] > 10:
            # user has either never been warned before or hasn't been warned in the last 10 seconds, so add a warning
            warn_id = await self.bot.get_cog("Warnings").add_warning(message.guild.id, message.author.id, 1,
                                                                     "[AUTO] spamming")
            await message.channel.send(
                f":warning: [`{str(warn_id)}`] {message.author.mention}, you have been given a 1 point warning for "
                f"spamming\nIf you keep spamming, you will get another warning!")


def setup(bot):
    """
    disabled this shit so it wont auto ban people for no reason
    """
    bot.add_cog(SpamDetector(bot))
