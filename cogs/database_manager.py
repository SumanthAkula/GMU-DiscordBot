from main import db
import discord
from discord.ext import commands


class DatabaseManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        @commands.Cog.listener
        async def on_guild_join(self, guild: discord.Guild):
            """
            check if a collection exists for this guild.  if it does, do nothing.  otherwise create the collection
            and create empty fields
            """
            if f"GUILD_{guild.id}" in db.list_collection_names():
                return
            collection = db[f"GUILD_{guild.id}"]
            guild_id = {
                "guild_id": guild.id
            }
            collection.inesrt_one(guild_id)

        @commands.command()
        async def force_collection_creation(self, ctx):
            await on_guild_join(ctx.guild)
            await ctx.send(f"Guild with ID {ctx.guild.id} added to database")


def setup(bot):
    bot.add_cog(DatabaseManager(bot))
