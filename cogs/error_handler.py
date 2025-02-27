import asyncio.exceptions

from discord.ext import commands
from discord.ext.commands import errors


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, errors.MissingRequiredArgument):
            await ctx.reply(f"You are missing the `{error.param.name}` argument! "
                            f"Run the help command to see how this command should be used")
        elif isinstance(error, errors.NoPrivateMessage):
            await ctx.reply("This command cannot be used in DMs!")
        elif isinstance(error, errors.PrivateMessageOnly):
            await ctx.reply("This command can only be used in DMs!")
        elif isinstance(error, errors.CommandNotFound):
            pass
        elif isinstance(error, errors.CommandOnCooldown):
            await ctx.reply(f"This command is on a cooldown, "
                            f"try running that command again in {error.retry_after} second(s)")
        elif isinstance(error, errors.DisabledCommand):
            await ctx.reply("You cannot run that command because it has been disabled")
        elif isinstance(error, errors.CommandInvokeError):
            if isinstance(error.original, asyncio.exceptions.TimeoutError):
                await ctx.reply("The command you were trying to run timed out! ")
        elif isinstance(error, errors.MissingPermissions):
            message = "You are missing the following permissions needed to run this command:\n"
            for perm in error.missing_permissions:
                message += f"`- '{perm}'`\n"
            await ctx.reply(message)
        else:
            await ctx.reply(str(error))
            raise error


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
