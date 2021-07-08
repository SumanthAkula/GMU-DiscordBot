import time

import discord
import pymongo.results
from bson.objectid import ObjectId
from discord.ext import commands, tasks

import main
from cogs.punisher import Punisher
from utils.database.collections import WARNINGS


class Warnings(commands.Cog):
    """
    Commands for giving and removing warnings to/from members.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.autoremove_warning.start()

    @tasks.loop(hours=12)
    async def autoremove_warning(self):
        _now = time.time()
        one_week = _now - 604800
        three_weeks = _now - (one_week * 3)
        two_months = _now - (2629743 * 2)
        six_months = _now - 15778463
        main.db[WARNINGS].delete_many(
            {
                "points": 1,
                "time": {
                    "$lte": one_week
                }
            }
        )
        main.db[WARNINGS].delete_many(
            {
                "points": 2,
                "time": {
                    "$lte": three_weeks
                }
            }
        )
        main.db[WARNINGS].delete_many(
            {
                "points": {
                    "$in": [3, 4]
                },
                "time": {
                    "$lte": two_months
                }
            }
        )
        main.db[WARNINGS].delete_many(
            {
                "points": {
                    "$in": list(range(5, 9))    # make the range end at 9 so it includes 8 point warnings
                },
                "time": {
                    "$lte": six_months
                }
            }
        )

    @commands.command(name="warn")
    @commands.guild_only()
    async def __add_warning_cmd(self, ctx: commands.Context, member: discord.Member, points: int,
                                *, reason: str):
        """
        Gives a member in the server a warning.  If enough warnings are given, a punishment will be automatically
        enforced on the member.  The bot will generate a random ID that can be used to remove the warning later.

        Arguments:
            member: the member you want to warn
            points: the number of points the warning is worth
            reason: the reason for the warning
        """
        if points <= 0:
            await ctx.reply("The number of points has to be greater than or equal to 1!")
            return
        if points > 2 ** (63 - 1):
            await ctx.reply("Bro if you gotta warn someone for that many points just ban them at that point lmao")
            return
        warn_id = await self.add_warning(ctx.guild.id, member.id, points, reason)
        await ctx.reply(f"A warning has been sent to the member\n"
                        f"ID: `{warn_id}`\n"
                        f"Run the `removewarning [warning ID]` command to remove the warning")

    @commands.command(name="removewarning", aliases=["unwarn", "rmw"])
    @commands.guild_only()
    async def __remove_warning(self, ctx: commands.Context, warning_id: str):
        """
        Removes a warning from the member that is passed in.

        Arguments:
            warning_id: the ID of the warning you are trying to remove
        """
        result: pymongo.results.DeleteResult = main.db[WARNINGS].delete_one(
            {
                "_id": ObjectId(warning_id),
                "guild_id": ctx.guild.id
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
        member_warnings = main.db[WARNINGS].find(
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

    async def add_warning(self, guild_id: int, member_id: int, points: int, reason: str) -> ObjectId:
        warning_id = main.db[WARNINGS].insert_one(
            {
                "guild_id": guild_id,
                "user_id": member_id,
                "reason": reason,
                "points": points,
                "time": time.time()
            }
        ).inserted_id
        warnings = await Warnings.get_warnings_for_user(guild_id, member_id)
        guild: discord.Guild = self.bot.get_guild(guild_id)
        member: discord.Member = await guild.fetch_member(member_id)
        message = f"{member.mention}, you have been given a {points} point warning!\n" \
                  f"Fuck up one more time and I send the secret girls to break your nico-nico knee caps"
        embed = discord.Embed(title=":warning: Warning!",
                              color=discord.Color.from_rgb(255, 214, 10),
                              description=message)
        embed.add_field(name="reason", value=reason)
        embed.add_field(name="warning ID", value=f"`{warning_id}`", inline=False)
        embed.add_field(name="think you were warned by mistake?", value="copy that warning ID and contact a moderator "
                                                                        "to see if you can get the warning removed")
        await member.send(embed=embed)
        await Punisher.assign_punishment(guild, member, warnings)

        return warning_id


def setup(bot):
    bot.add_cog(Warnings(bot))
