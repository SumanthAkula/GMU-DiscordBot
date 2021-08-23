import discord
from discord.ext import commands

import main
from utils.database.collections import MOD_ROLES


class NoModeratorRoleError(commands.CheckFailure):
	pass


def moderator_role_check():
	def predicate(ctx: commands.Context):
		role_data = main.db[MOD_ROLES].find_one(
			{
				"guild_id": ctx.guild.id
			}
		)
		if ctx.guild.owner == ctx.author:
			return True
		elif role_data is None:
			raise NoModeratorRoleError(":x: No moderator role has been set! Contact the server owner to get this "
									   "fixed.")
		elif ctx.author.get_role(role_data["role_id"]) is None:
			raise NoModeratorRoleError(":x: Only moderators can run this command!")
		return True

	return commands.check(predicate)


class ModerationRoleManager(commands.Cog, name="Moderation roles"):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@moderator_role_check()
	async def setmodrole(self, ctx: commands.Context, role_id: int):
		role: discord.Role = ctx.guild.get_role(role_id)
		if role is None:
			await ctx.reply(":x: That role does not exist in this guild!")
			return
		main.db[MOD_ROLES].replace_one(
			{
				"guild_id": ctx.guild.id
			},
			{
				"guild_id": ctx.guild.id,
				"role_id": role_id
			},
			upsert=True
		)
		await ctx.reply(f":white_check_mark: Moderator role set to `{role.name}`!")


# do stuff here
def setup(bot):
	bot.add_cog(ModerationRoleManager(bot))
