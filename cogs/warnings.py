import uuid

import discord
from discord.ext import commands

import main


class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="warn")
    async def __add_warning(self, ctx: commands.Context, member: discord.Member, points: int = 1
                            , *, reason: str = "They were being a silly baka"):
        guild_collection = main.db[f"GUILD_{ctx.guild.id}"]
        warn_id = str(uuid.uuid1())
        value = {
            "$push": {
                "warnings": {
                    "$each": [
                        {
                            "warn_id": warn_id,
                            "user_id": member.id,
                            "reason": reason,
                            "points": points
                        }
                    ]
                }
            }
        }
        guild_collection.update_one({}, value)
        warn_count = await self.__get_warnings_for_user(ctx.guild.id, member.id)
        await ctx.send(f":warning: [`{warn_id}`] {member.mention}, you have been given a warning with "
                       f"the reason \"{reason}\"! You now have {warn_count} warning(s)")

    @commands.command(name="removewarning", aliases=["unwarn", "rmw"])
    async def __remove_warning(self, ctx: commands.Context, warn_id: str):
        guild_collection = main.db[f"GUILD_{ctx.guild.id}"]
        value = {
            "$pull": {
                "warnings": {
                    "warn_id": warn_id
                }
            }
        }
        guild_collection.update_one({}, value)
        await ctx.send(":white_check_mark:")

    @staticmethod
    async def __get_warnings_for_user(guild_id: int, member_id: int) -> int:
        guild_collection = main.db[f"GUILD_{guild_id}"]
        warnings = dict(guild_collection.find_one({}))["warnings"]
        warn_count = 0
        for warning in warnings:
            if warning["user_id"] == member_id:  # loop through all the warnings and see which ones belong to the user
                warn_count += 1
        return warn_count

    @commands.command(name="warncount", aliases=["wc"])
    async def __get_warning_count(self, ctx: commands.Context, member: discord.Member):
        warn_count = await self.__get_warnings_for_user(ctx.guild.id, member.id)
        await ctx.send(f"{member.display_name} has {warn_count} warning(s)")


def setup(bot):
    bot.add_cog(Warnings(bot))
