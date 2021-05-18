import uwuify
from discord.ext import commands


class Uwuifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uwu(self, ctx: commands.Context, *, msg):
        await ctx.send(uwuify.uwu(msg))


def setup(bot):
    bot.add_cog(Uwuifier(bot))
