import time

import discord
from discord.ext import commands, tasks

import main


class Punisher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_for_expired_bans.start()

    # BANNING USERS
    @commands.command(name="ban")
    async def __ban_member_cmd(self, ctx: commands.Context, member: discord.Member, length: int, *, reason: str):
        if ctx.author == member:
            await ctx.reply("you can't ban yourself using this command")
            return
        await self.__ban_member(ctx.guild, member, length, reason=reason)

    @staticmethod
    async def __ban_member(guild: discord.Guild, member: discord.Member, length: int, reason: str):
        lenstr = f"for {length} day(s)" if length >= 0 else "indefinitely"
        await member.send(f"You have been banned {lenstr} from the {guild.name} Discord server for the "
                          f"following reason(s):\n{reason}")
        await member.ban(delete_message_days=0, reason=reason)

        if length <= 0:
            return  # The member was permanently banned, we dont need to add the ban to the database
        await Punisher.__add_ban_to_db(guild.id, member.id, length, reason=reason)

    @staticmethod
    async def __add_ban_to_db(guild_id: int, member_id: int, length: int, reason: str):
        main.db.bans.insert_one(
            {
                "guild_id": guild_id,
                "user_id": member_id,
                "reason": reason,
                "length": length,
                "time": time.time()
            }
        )

    # UNBANNING USERS
    @tasks.loop(seconds=10)
    async def check_for_expired_bans(self):
        now = time.time()
        bans = main.db.bans.find(
            {
                "length": {
                    "$gte": 1
                }
            }
        )
        bans = list(bans)
        if not bans:
            return
        for ban in bans:
            if now - ban["time"] >= ban["length"] * 60:
                print(f"unbanning user {ban['user_id']}")
                guild: discord.Guild = await self.bot.fetch_guild(ban["guild_id"])
                user: discord.User = await self.bot.fetch_user(ban["user_id"])
                await guild.unban(user, reason="[AUTO] temporary ban timer expired")
                await user.send(f"Your temporary ban from the {guild.name} Discord server is over! You are free to "
                                f"join the server again.")

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        main.db.bans.delete_one(
            {
                "guild_id": guild.id,
                "user_id": user.id
            }
        )


def setup(bot):
    bot.add_cog(Punisher(bot))
