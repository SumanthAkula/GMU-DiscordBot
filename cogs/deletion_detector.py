import os
import time
import uuid
from pathlib import Path

import discord
from discord.ext import commands, tasks

import main

# constant path for the temporary files needed for recreating the attachments
DELETED_ATTACHMENTS_PATH = path = "tmp/deleted_attachments/"


class DeletionDetector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = []
        self.clear_cache.start()
        self.clear_old_deletes.start()
        Path(DELETED_ATTACHMENTS_PATH).mkdir(parents=True, exist_ok=True)  # create folders for the temp files

    @tasks.loop(seconds=30)
    async def clear_cache(self):
        self.cache = []

    @tasks.loop(minutes=1)
    async def clear_old_deletes(self):
        """
        deletes deleted messages from the database if they were deleted 14 or more days ago.
        """
        threshold = time.time() - 604800 * 2
        main.db.deleted_messages.delete_many(
            {
                "time_deleted": {
                    "$lte": threshold
                }
            }
        )

    @commands.command(name="snipe")
    async def __snipe_cmd(self, ctx: commands.Context):
        if not self.cache:
            await ctx.reply("Nothing to snipe!")
            return
        await ctx.send(self.cache[0])

    @commands.command(name="getdeleted", aliases=["gd"])
    async def __get_deleted_cmd(self, ctx: commands.Context, member: discord.Member, amount: int = 1):
        messages = main.db.deleted_messages.find(
            {
                "guild_id": ctx.guild.id,
                "author_id": member.id
            }, limit=amount
        ).sort("time_sent", -1)
        messages = list(messages)
        if not messages:
            await ctx.send("There are no recently deleted messages from this user!")
        for message in messages:
            if message["content"]:
                await ctx.send(message["content"])
            if message["attachments"]:  # check if the message has attachments
                for a in message["attachments"]:  # if so, load each one and send to discord
                    file_name = f"G{ctx.guild.id}_{a['filename']}"
                    with open(f"{DELETED_ATTACHMENTS_PATH}{file_name}", "wb") as fp:  # create a temporary file
                        # decode the base64 string and write it back to the file
                        fp.write(a["data"])
                    await ctx.send(file=discord.File(DELETED_ATTACHMENTS_PATH + file_name))
                    os.remove(DELETED_ATTACHMENTS_PATH + file_name)  # delete the temp file after sending it to discord

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        attachments = []
        for a in message.attachments:
            """
            encode attachments as base64 strings to store them in the database easily
            """
            file = await a.to_file()
            attachments.append(
                {
                    "attachment_id": a.id,
                    "filename": a.filename,
                    "type": a.content_type,
                    "data": file.fp.read()
                }
            )
        main.db.deleted_messages.insert_one(
            {
                "_id": str(uuid.uuid1()),
                "guild_id": message.guild.id,
                "author_id": message.author.id,
                "content": message.content,
                "attachments": attachments,
                "time_sent": message.created_at.timestamp(),
                "time_deleted": time.time()
            }
        )

    async def on_bulk_message_delete(self, messages: list[discord.Message]):
        pass  # TODO


def setup(bot):
    bot.add_cog(DeletionDetector(bot))
