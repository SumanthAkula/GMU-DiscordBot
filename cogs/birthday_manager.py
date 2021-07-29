import discord
from discord.ext import commands


class BirthdayManager(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.birthdays = []

    @commands.group("birthday", aliases=["bday"], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def __bday_command(self, ctx: commands.Context):
        """
        Get or set your birthday and the bot can wish you a happy birthday
        """
        await ctx.invoke(self.bot.help_command, f"{ctx.command.name}")

    @__bday_command.command("set", pass_context=True, invoke_without_command=True)
    async def set(self, ctx: commands.Context, birthday: commands.Bot):
        """
        Set your birthday

        Arguments:
            birthday: your birthday in UNIX epoch time :V
        """
        await ctx.send("set bday")

    @commands.command("test")
    async def test(self, ctx: commands.Context, arg):
        """
        a test command

        Arguments:
            arg: an argument
        """
        await ctx.send("argh!")

    @__bday_command.command("get", pass_context=True, invoke_without_command=True)
    async def get(self, ctx: commands.Context):
        """
        Get your birthday (in case you forget it or something lol)
        """
        await ctx.send("get bday")


def setup(bot):
    bot.add_cog(BirthdayManager(bot))
