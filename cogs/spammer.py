import asyncio

from discord.ext import commands


class Spammer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="spam", alieses=["sp"])
    async def __spam_cmd(self, ctx: commands.Context, amount: int = 10):
        for n in range(amount):
            await ctx.send(f"message {n + 1}")
            await asyncio.sleep(0.25)


def setup(bot):
    bot.add_cog(Spammer(bot))
