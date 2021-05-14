import time
import uuid

import discord
from discord.ext import commands

import main


class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="warn")
    async def __add_warning_cmd(self, ctx: commands.Context, member: discord.Member, points: int,
                                *, reason: str = "They were being a silly baka"):
        warn_id = await self.add_warning(ctx.guild.id, member.id, points, reason)
        await ctx.send(f":warning: [`{warn_id}`] {member.mention}, you have been given a {points} point warning with "
                       f"the reason \"{reason}\"\n"
                       f"Fuck up one more time and I send the secret girls to break your knee caps")

    @commands.command(name="removewarning", aliases=["unwarn", "rmw"])
    async def __remove_warning(self, ctx: commands.Context, warn_id: str):
        main.db.warnings.delete_one(
            {
                "guild_id": ctx.guild.id,
                "warning_id": f"{warn_id}"
            }
        )
        await ctx.send(":white_check_mark:")

    @commands.command(name="warncount", aliases=["wc"])
    async def __get_warning_count(self, ctx: commands.Context, member: discord.Member):
        warnings = await self.get_warnings_for_user(ctx.guild.id, member.id)
        warn_count = len(warnings)
        await ctx.send(f"{member.display_name} has {warn_count} warning(s)")

    @staticmethod
    async def get_warnings_for_user(guild_id: int, member_id: int) -> list:
        member_warnings = main.db.warnings.find(
            {
                "guild_id": guild_id,
                "user_id": member_id
            }
        )
        return list(member_warnings)

    @staticmethod
    async def get_most_recent_warning(guild_id: int, member_id: int):
        warnings = await Warnings.get_warnings_for_user(guild_id, member_id)
        return warnings[-1]

    @staticmethod
    async def add_warning(guild_id, member_id, points: int, reason: str) -> str:
        warning_id = str(uuid.uuid1())
        main.db.warnings.insert_one(
            {
                "guild_id": guild_id,
                "warning_id": warning_id,
                "user_id": member_id,
                "reason": reason,
                "points": points,
                "time": time.time()
            }
        )
        return warning_id


def setup(bot):
    bot.add_cog(Warnings(bot))
