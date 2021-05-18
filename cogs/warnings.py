import time
import uuid

import discord
import pymongo.results
from discord.ext import commands

import main


class Warnings(commands.Cog):
    """
    How the Warnings commands work:
        warn:
            adds a warning to whatever user is passed in.  whoever runs the command must also pass in the amount of
            points the warning is worth.  If no reason is given, a default reason is given.  the bot will add the
            warning to the database and each warning will record the guild the warning was issued in, the user the
            warning is for, the points, the reason, a warning ID, and the time that the warning was given at in epoch.
            The warning ID is a randomly generated UUID string that is used to identify any individual warning so it can
            be removed or referenced later.
        removewarning:
            removes a warning from the database.  whoever runs this command must also pass in the warning ID of the
            warning they want to remove.  the bot will query the warnings collection in the database and delete it.
        warncount:
            the bot will send the number of warning points and warnings a member has for that guild.  whoever runs
            this command must also pass in the member they want to see the warning count for, even if that member
            is themselves.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="warn")
    async def __add_warning_cmd(self, ctx: commands.Context, member: discord.Member, points: int,
                                *, reason: str = "They were being a silly baka"):
        if points <= 0:
            await ctx.reply("The number of points has to be greater than or equal to 1!")
            return
        if points > 2 ** (63 - 1):
            await ctx.reply("Bro if you gotta warn someone for that many points just ban them at that point lmao")
            return
        warn_id = await self.add_warning(ctx.guild.id, member.id, points, reason)
        await ctx.reply(f":warning: [`{warn_id}`] {member.mention}, you have been given a {points} point warning with "
                        f"the reason \"{reason}\"\n"
                        f"Fuck up one more time and I send the secret girls to break your knee caps")

    @commands.command(name="removewarning", aliases=["unwarn", "rmw"])
    async def __remove_warning(self, ctx: commands.Context, warn_id: str):
        result: pymongo.results.DeleteResult = main.db.warnings.delete_one(
            {
                "guild_id": ctx.guild.id,
                "warning_id": f"{warn_id}"
            }
        )
        await ctx.reply(":white_check_mark: Warning removed" if result.deleted_count != 0 else ":x: No warning with "
                                                                                               "that ID exists!")

    @commands.command(name="warncount", aliases=["wc"])
    async def __get_warning_count(self, ctx: commands.Context, member: discord.Member):
        warnings = await self.get_warnings_for_user(ctx.guild.id, member.id)
        warn_count = len(warnings)
        warn_points = 0
        if warn_count != 0:
            for warning in warnings:
                warn_points += warning["points"]
        await ctx.reply(f"{member.display_name} has {warn_count} warning(s) and {warn_points} warning point(s)")

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
        if not warnings:
            return None
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
