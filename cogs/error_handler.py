import traceback
from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        try:
            raise error
        except commands.CommandError:
            message = """```python\n"""
            message += traceback.format_exc()
            message += "\n```"
            await ctx.send(message)
        raise error


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
