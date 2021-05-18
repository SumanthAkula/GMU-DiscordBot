import time
import uuid

import discord
import pymongo.results
from discord.ext import commands

import main
from cogs.punisher import Punisher


class Warnings(commands.Cog):
    """
    Commands for giving and removing warnings to/from members.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="warn")
    @commands.guild_only()
    async def __add_warning_cmd(self, ctx: commands.Context, member: discord.Member, points: int,
                                *, reason: str = "They were being a silly baka"):
        """
        Gives a member in the server a warning.  If enough warnings are given, a punishment will be automatically
        enforced on the member.  The bot will generate a random ID that can be used to remove the warning later.

        Arguments:
            member: the member you want to warn
            points: the number of points the warning is worth
            reason (optional): the reason for the warning. if no reason is given, the default one is "They were being a
            silly baka"
        """
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
    @commands.guild_only()
    async def __remove_warning(self, ctx: commands.Context, warning_id: str):
        """
        Removes a warning from the member that is passed in.

        Arguments:
            warning_id: the ID of the warning you are trying to remove
        """
        result: pymongo.results.DeleteResult = main.db.warnings.delete_one(
            {
                "guild_id": ctx.guild.id,
                "warning_id": f"{warning_id}"
            }
        )
        await ctx.reply(":white_check_mark: Warning removed" if result.deleted_count != 0 else ":x: No warning with "
                                                                                               "that ID exists!")

    @commands.command(name="warncount", aliases=["wc"])
    @commands.guild_only()
    async def __get_warning_count(self, ctx: commands.Context, member: discord.Member):
        """
        Prints out how many warnings a member has and how many total warning points they have.

        Arguments:
            member: the member you want to check the warning count for
        """
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

    async def add_warning(self, guild_id, member_id, points: int, reason: str) -> str:
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
        warnings = await Warnings.get_warnings_for_user(guild_id, member_id)
        guild: discord.Guild = await self.bot.fetch_guild(guild_id)
        member: discord.Member = await guild.fetch_member(member_id)
        await Punisher.assign_punishment(guild, member, warnings)
        return warning_id


def setup(bot):
    bot.add_cog(Warnings(bot))
