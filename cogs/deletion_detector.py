import os
from datetime import timedelta
from typing import Union

import discord
from discord.ext import commands

import main

from utils.log_channel_types import LogChannelType


class DeletionDetector(commands.Cog, name="Deletion Detector"):
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

    async def get_logging_channel(self, guild_id: int) -> Union[None, discord.TextChannel]:
        data = main.db.log_channels.find_one(
            {
                "guild_id": guild_id,
                "log_type": LogChannelType.MessageDeletion.value
            }
        )
        if data is None:
            return None
        else:
            return await self.bot.fetch_channel(data["channel_id"])

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.channel.type == discord.ChannelType.group or message.channel.type == discord.ChannelType.private:
            return  # do not log deleted messages in DMs
        channel = await self.get_logging_channel(message.guild.id)
        if channel is None:
            await message.channel.send("No message deletion logging channel was found in this guild!")
            return

        est_time = message.created_at - timedelta(hours=4)
        embed = discord.Embed(title="Deleted Message", color=0xff9838)
        embed.set_author(name=f"{message.author.name}#{message.author.discriminator}",
                         icon_url=message.author.avatar_url)
        embed.add_field(name="time sent", value=est_time.strftime('%m/%d/%Y - %I:%M %p ET'), inline=False)
        embed.add_field(name="channel", value=message.channel.mention, inline=False)
        if message.content:
            embed.add_field(name="content", value=message.content, inline=False)
        attachments = []
        if message.attachments:
            for attachment in message.attachments:
                orig = await attachment.to_file()
                # get the file size
                orig.fp.seek(0, os.SEEK_END)
                if orig.fp.tell() > message.guild.filesize_limit:
                    attachments.append(discord.File("assets/file_too_big.jpg"))
                else:
                    attachments.append(discord.File(fp=orig.fp, filename=attachment.filename))
        await channel.send(embed=embed, files=None if not attachments else attachments)

    async def on_bulk_message_delete(self, messages: list[discord.Message]):
        channel = await self.get_logging_channel(messages[0].guild.id)
        if channel is None:
            await messages[0].channel.send("No message deletion logging channel was found in this guild!")
            return
        for message in messages:
            await self.on_message_delete(message)


def setup(bot):
    bot.add_cog(DeletionDetector(bot))
