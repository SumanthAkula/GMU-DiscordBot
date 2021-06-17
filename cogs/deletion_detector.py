from datetime import timedelta

import discord
from discord.ext import commands

import main

from utils.log_channel_types import LogChannelType


class DeletionDetector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setdeletionlog", aliases=["sdl"])
    @commands.guild_only()
    async def __set_deletion_log_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Set the channel you want deleted messages to be logged to

        Arguments:
            channel: tag the channel you want deleted messages to be logged to
        """
        if ctx.guild.id != channel.guild.id:
            await ctx.reply("The channel must be a channel from this server!")
            return
        main.db.log_channels.replace_one(
            {
                "guild_id": ctx.guild.id,
                "log_type": LogChannelType.MessageDeletion.value
            },
            {
                "guild_id": ctx.guild.id,
                "log_type": LogChannelType.MessageDeletion.value,
                "channel_id": channel.id
            },
            upsert=True
        )

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.channel.type == discord.ChannelType.group or message.channel.type == discord.ChannelType.private:
            return  # do not log deleted messages in DMs
        channel_id = main.db.log_channels.find_one(
            {
                "guild_id": message.guild.id,
                "log_type": LogChannelType.MessageDeletion.value
            }
        )["channel_id"]
        channel = await self.bot.fetch_channel(channel_id)

        attachments = []
        if message.attachments:
            for attachment in message.attachments:
                orig = await attachment.to_file()
                attachments.append(discord.File(fp=orig.fp, filename=attachment.filename))
        est_time = message.created_at - timedelta(hours=4)
        embed = discord.Embed(title="Deleted Message", color=0xff9838)
        embed.set_author(name=f"{message.author.name}#{message.author.discriminator}",
                         icon_url=message.author.avatar_url)
        embed.add_field(name="time sent", value=est_time.strftime('%m/%d/%Y - %I:%M %p ET'), inline=False)
        embed.add_field(name="channel", value=message.channel.mention, inline=False)
        if message.content:
            embed.add_field(name="content", value=message.content, inline=False)
        await channel.send(embed=embed, files=None if not message.attachments else attachments)

    async def on_bulk_message_delete(self, messages: list[discord.Message]):
        pass  # TODO


def setup(bot):
    bot.add_cog(DeletionDetector(bot))
