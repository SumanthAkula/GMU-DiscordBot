import discord
from discord.ext import commands

from utils.log_channel_types import LogChannelType


class Boost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        nitro_role = before.guild.premium_subscriber_role
        if nitro_role is None:
            return
        if nitro_role not in before.roles and nitro_role in after.roles:
            gen_chat: discord.TextChannel = \
                await self.bot.get_cog("LoggerChannels").get_channel(self.bot, after.guild.id, LogChannelType.General)
            embed = discord.Embed(title="AYYYY A NEW BOOSTER LETS GOOOOO", color=nitro_role.color)
            embed.set_image(
                url="https://raw.githubusercontent.com/Sc0pz/DiscordBot/notsumo_Dev/assets/booster_banner.PNG")
            embed.description = after.mention
            await gen_chat.send(embed=embed)


def setup(bot):
    bot.add_cog(Boost(bot))
