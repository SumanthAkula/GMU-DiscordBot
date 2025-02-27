import time
from enum import Enum
from typing import Union

import discord
from discord.ext import commands, tasks
import main
from utils.database.collections import PUNISHMENTS, MOD_ROLES


class Punishment(Enum):
    MUTE = 0
    BAN = 1


class Punisher(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_for_expired_punishments.start()

    @staticmethod
    async def assign_punishment(guild: discord.Guild, member: discord.Member, warnings: list):
        # TODO: ENABLE AUTO BAN
        if guild.id == 807278087074611240:
            return  # DO NOT BAN IN THE CS BOT TESTING DISCORD SERVER
        reasons = ""
        points = 0
        for i, warning in enumerate(warnings, start=1):
            reasons += f"{i}) {warning['reason']}\n"
            points += warning["points"]
        if points >= 10:  # permanent ban
            await Punisher.ban_member(guild, member, -1, reasons)
        elif points >= 6:  # 3 day temporary ban
            await Punisher.ban_member(guild, member, 3, reasons)
        elif points >= 4:  # 1 day temporary ban
            await Punisher.ban_member(guild, member, 1, reasons)
        elif points >= 2:  # 1 hour temporary mute
            await Punisher.mute_member(guild, member, 1, reasons)

    @staticmethod
    async def __add_punishment_to_db(guild_id: int, member_id: int, punishment_type: Punishment,
                                     length: int, reason: str):
        main.db[PUNISHMENTS].insert_one(
            {
                "guild_id": guild_id,
                "user_id": member_id,
                "type": punishment_type.value,
                "reason": reason,
                "length": length,
                "time": time.time()
            }
        )

    @tasks.loop(seconds=10)
    async def check_for_expired_punishments(self):
        now = time.time()
        punishments = main.db[PUNISHMENTS].find(
            {
                "length": {
                    "$gte": 1
                }
            }
        )
        punishments = list(punishments)
        if not punishments:
            return
        for punishment in punishments:
            if punishment["type"] == Punishment.BAN.value:
                if now - punishment["time"] >= punishment["length"] * 86400:
                    await self.revoke_temp_ban(punishment)
            elif punishment["type"] == Punishment.MUTE.value:
                if now - punishment["time"] >= punishment["length"] * 3600:
                    await self.revoke_mute(punishment)

    # BANNING USERS
    @commands.command(name="ban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def __ban_member_cmd(self, ctx: commands.Context, member: discord.Member, length: int, *, reason: str):
        """
        Bans a member for a specified amount of time (or indefinitely if you want).  The member will be automatically
        removed from the ban list after the specified amount of time has passed.

        Arguments:
            member: the member you want to ban (@ them)
            length: the length of the ban in days. Put a 0 or a negative number here to make it a permanent ban
            reason: the reason for the ban.  This will show up in the audit logs and will be sent to the member that is
            being banned via DM
        """
        if ctx.author == member:
            await ctx.reply("you can't ban yourself using this command")
            return
        user = f"{member.name}#{member.discriminator}"
        await self.ban_member(ctx.guild, member, length, reason)
        embed = discord.Embed(title=f"Banned {user}", color=discord.Color.red())
        embed.add_field(name="reason(s)", value=reason, inline=False)
        embed.add_field(name="duration", value=f"{length} day(s)" if length >= 0 else "*permanent*", inline=False)
        await ctx.reply(embed=embed)

    @staticmethod
    async def ban_member(guild: discord.Guild, member: discord.Member, length: int, reason: str):
        lenstr = f"for {length} day(s)" if length >= 0 else "indefinitely"
        message = f"You have been banned {lenstr} from the {guild.name} Discord server"
        embed = discord.Embed(title="You have been banned!", description=message, color=discord.Color.red())
        embed.add_field(name="reason(s)", value=reason, inline=False)
        if length > 0:
            if "VANITY_URL" in guild.features:
                invite = await guild.vanity_invite()
            else:
                invite = await guild.system_channel.create_invite(max_uses=1)
            embed.add_field(name="invite",
                            value=f"When your ban ends, you can rejoin the server with this invite:\n"
                                  f"{invite}", inline=False)
        await member.send(embed=embed)
        await member.ban(delete_message_days=0, reason=reason)

        if length <= 0:
            return  # The member was permanently banned, we dont need to add the ban to the database
        await Punisher.__add_punishment_to_db(guild.id, member.id, Punishment.BAN, length, reason)

    # UNBANNING USERS
    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        main.db[PUNISHMENTS].delete_one(
            {
                "guild_id": guild.id,
                "user_id": user.id,
                "type": Punishment.BAN.value
            }
        )

    async def revoke_temp_ban(self, ban: dict):
        guild: discord.Guild = await self.bot.fetch_guild(ban["guild_id"])
        user: discord.User = await self.bot.fetch_user(ban["user_id"])
        await guild.unban(user, reason="[AUTO] temporary ban timer expired")

    # MUTING MEMBERS
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_mute_role(self, ctx: commands.Context, role_id: int):
        """
        Set the role that will get assigned when a member is muted

        Arguments:
            role_id: the ID of the role to assign.
        """
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
        await ctx.reply(f":white_check_mark: Muted role set to `{role.name}`!")

    @staticmethod
    async def get_mute_role(guild: discord.Guild) -> Union[discord.Role, None]:
        data = main.db[MOD_ROLES].find_one(
            {
                "guild_id": guild.id
            }
        )
        if data is None:
            return None
        else:
            return guild.get_role(data["role_id"])

    @commands.command(name="mute")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def __mute_member(self, ctx: commands.Context, member: discord.Member, length: int, *, reason: str):
        if await Punisher.get_mute_role(ctx.guild) is None:
            await ctx.send(":x: There is no 'mute' role set for this server! Contact a server admin to have this fixed")
            return
        await self.mute_member(ctx.guild, member, length, reason)
        await ctx.reply(f":white_check_mark: Muted {member.mention} for {length} hour(s)")

    @commands.command(name="unmute")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def __unmute_member(self, ctx: commands.Context, member: discord.Member):
        data = main.db[PUNISHMENTS].find_one(
            {
                "guild_id": ctx.guild.id,
                "user_id": member.id,
                "type": Punishment.MUTE.value
            }
        )
        if data is None:
            await ctx.reply(":x: That member is not muted")
            return
        await self.revoke_mute(data, f"manually unmuted by {ctx.author.name}")
        await ctx.reply(f":white_check_mark: Unmuted {member.mention}")

    @staticmethod
    async def mute_member(guild: discord.Guild, member: discord.Member, length: int, reason: str):
        lenstr = f"for {length} hour(s)" if length >= 0 else "indefinitely"
        role = await Punisher.get_mute_role(guild)
        await member.add_roles(role, reason=f"{reason}")
        await Punisher.__add_punishment_to_db(guild.id, member.id, Punishment.MUTE, length, reason)
        await member.send(f"You have been muted {lenstr} in the {guild.name} Discord server for the following reason(s)"
                          f"\n{reason}")

    async def revoke_mute(self, punishment: dict, reason: str = "[AUTO] temporary mute expired"):
        guild: discord.Guild = await self.bot.fetch_guild(punishment["guild_id"])
        member: discord.Member = await guild.fetch_member(punishment["user_id"])
        role = await Punisher.get_mute_role(guild)
        await member.remove_roles(role, reason=reason)
        main.db[PUNISHMENTS].delete_one(
            {
                "guild_id": guild.id,
                "user_id": member.id,
                "type": Punishment.MUTE.value
            }
        )

        await member.send(f"You have been unmuted {guild.name} Discord server is over! You are free speak in the"
                          f" server again.")


def setup(bot):
    bot.add_cog(Punisher(bot))
