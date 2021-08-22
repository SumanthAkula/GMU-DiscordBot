import discord
from discord.ext import commands

import main
from utils.database.collections import MOD_ROLES


class Moderator(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@staticmethod
	async def moderator_role_check(ctx: commands.Context):
		class NoModeratorRoleError(commands.CheckFailure):
			pass

		role_data = main.db[MOD_ROLES].find_one(
			{
				"guild_id": ctx.guild.id
			}
		)
		if role_data is None or ctx.author.get_role(role_data["role_id"]) is None:
			raise NoModeratorRoleError
		return True

	@commands.command()
	@commands.check(moderator_role_check)
	async def setmodrole(self, ctx: commands.Context, role_id: int):
		role: discord.Role = ctx.guild.get_role(role_id)
		if role is None:
			await ctx.reply(":x: That role does not exist in this guild!")
			return
		result = main.db[MOD_ROLES].replace_one(
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
	bot.add_cog(Moderator(bot))
