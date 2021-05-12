import discord
from discord.ext import commands

import main


class Warnings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="warn")
    async def __add_warning(self, ctx: commands.Context, member: discord.Member, *, reason: str = "They were being "
                                                                                                  "a silly baka"):
        guild_collection = main.db[f"GUILD_{ctx.guild.id}"]
        query = {
            "guild_id": ctx.guild.id
        }
        value = {
            "$push": {
                "warnings": {
                    "$each" [
                        {
                            "user_id": member.id,
                            "reason": reason
                        }
                    ]
                }
            }
        }
        guild_collection.update_one(query, value)

    @commands.command(name="removewarning", aliases=["rmw"])
    async def __remove_warning(self, ctx: commands.Context, member: discord.Member):
        # TODO
        pass

    @commands.command(name="warncount", aliases=["wc"])
    async def __get_warning_count(self, ctx: commands.Context, member: discord.Member):
        # TODO
        pass


def setup(bot):
    bot.add_cog(Warnings(bot))
