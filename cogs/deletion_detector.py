import base64
import os
import time
from pathlib import Path

import discord
from discord.ext import commands, tasks

import main

DELETED_ATTACHMENTS_PATH = path = "tmp/deleted_attachments/"


class DeletionDetector(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cache = []
        self.clear_cache.start()
        Path(DELETED_ATTACHMENTS_PATH).mkdir(parents=True, exist_ok=True)

    @tasks.loop(seconds=30)
    async def clear_cache(self):
        self.cache = []

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
        for message in messages:
            if message["content"]:
                await ctx.send(message["content"])
            if message["attachments"]:
                for a in message["attachments"]:
                    file_name = f"G{ctx.guild.id}_{a['filename']}"
                    with open(f"{DELETED_ATTACHMENTS_PATH}{file_name}", "wb") as fp:
                        fp.write(base64.decodebytes(a["base64"]))
                    await ctx.send(file=discord.File(DELETED_ATTACHMENTS_PATH + file_name))
                    os.remove(DELETED_ATTACHMENTS_PATH + file_name)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        attachments = []
        for a in message.attachments:
            file = await a.to_file()
            file = file.fp
            b64 = base64.b64encode(file.read())
            attachments.append(
                {
                    "attachment_id": a.id,
                    "filename": a.filename,
                    "type": a.content_type,
                    "base64": b64
                }
            )
        main.db.deleted_messages.insert_one(
            {
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
