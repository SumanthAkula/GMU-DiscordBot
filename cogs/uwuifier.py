from typing import Optional

import discord
import uwuify
from discord.ext import commands


class Uwuifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def uwu(self, ctx: commands.Context, *, msg: Optional[str]):
        if ctx.message.reference is None and msg is None:
            await ctx.reply("You have to either reply to a message with this command OR provide some text to uwuify as "
                            "an argument")
            return
        if ctx.message.reference:
            original: discord.Message = await ctx.message.channel.fetch_message(ctx.message.reference.message_id)
            msg = original.content
        flags = uwuify.SMILEY | uwuify.YU
        await ctx.send(uwuify.uwu(msg, flags=uwuify.UwuifyFlag(flags)))


def setup(bot):
    bot.add_cog(Uwuifier(bot))
