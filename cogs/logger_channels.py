import discord
from discord.ext import commands

import main
from utils.database.collections import LOG_CHANNELS
from utils.log_channel_types import LogChannelType


class LoggerChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group("channel", pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def __channel_cmd(self, ctx: commands.Context):
        """
        You can set channels as 'logs' the bot can send messages to for moderation purposes
        """
        await ctx.reply(f"Run the `{ctx.prefix}help channel` command for more information on how to use this command")

    @__channel_cmd.command("set", pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def __set(self, ctx: commands.Context):
        options: [discord.SelectOption] = []
        for log_type in LogChannelType:
            options.append(discord.SelectOption(label=log_type.name, default=False))

        class LogTypeSelector(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.selected_type = None

            @discord.ui.select(placeholder="Select what type of log you want to set", options=options)
            async def selection_made(self, select_menu: discord.ui.Select, interaction: discord.Interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message("Only the person who ran the command can "
                                                            "select a log type!", ephemeral=True)
                    return
                self.selected_type = LogChannelType[select_menu.values[0]]

            @property
            def get_type(self):
                return self.selected_type

        view = LogTypeSelector()
        original: discord.Message = await ctx.reply("Chose an option from the dropdown menu", view=view)

        def interaction_check(_interaction: discord.Interaction):
            return _interaction.user == ctx.author and \
                   _interaction.channel == ctx.channel and \
                   _interaction.application_id == self.bot.application_id and \
                   _interaction.message == original
        await self.bot.wait_for("interaction", check=interaction_check, timeout=view.timeout)

        await original.edit(content=f"Reply to this message and tag the channel you would like to set as the "
                                    f"{view.get_type.name} log channel", view=None)

        def message_check(_message: discord.Message):
            return _message.guild == ctx.guild and \
                   _message.author == ctx.author and \
                   _message.channel == ctx.channel and \
                   _message.channel_mentions and \
                   _message.reference.message_id == original.id
        channel: discord.TextChannel = \
            (await self.bot.wait_for("message", check=message_check, timeout=180)).channel_mentions[0]
        await self.set_channel(ctx, view.get_type, channel)

    @staticmethod
    async def set_channel(ctx: commands.Context, log_type: LogChannelType, channel: discord.TextChannel):
        if ctx.guild.id != channel.guild.id:
            await ctx.reply("The channel must be a text channel from this server!")
            return
        main.db[LOG_CHANNELS].replace_one(
            {
                "guild_id": ctx.guild.id,
                "log_type": log_type.value
            },
            {
                "guild_id": ctx.guild.id,
                "log_type": log_type.value,
                "channel_id": channel.id
            },
            upsert=True
        )
        await ctx.reply(f":white_check_mark: set {channel.mention} as `{log_type.name}` channel")

    @staticmethod
    async def get_channel(bot: commands.Bot, guild_id: int, log_type: LogChannelType):
        data = main.db[LOG_CHANNELS].find_one(
            {
                "guild_id": guild_id,
                "log_type": log_type.value
            }
        )
        if data is None:
            return None
        else:
            return await bot.fetch_channel(data["channel_id"])


def setup(bot):
    bot.add_cog(LoggerChannels(bot))
