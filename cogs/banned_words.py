import discord
import pymongo.results
from discord.ext import commands

import main
from utils.database.collections import BANNED_WORDS


class BannedWords(commands.Cog, name="Banned Word Remover"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban_word")
    @commands.guild_only()
    async def __ban_word_cmd(self, ctx: commands.Context, word: str):
        """
        Adds 'word' to the list of words than cannot be said in text channels

        Arguments:
            word: the word to ban
        """
        main.db[BANNED_WORDS].insert_one(
            {
                "guild_id": ctx.guild.id,
                "token": word.lower()
            }
        )
        await ctx.send(f"Banned '{word}' from being said in this server!")

    @commands.command(name="unban_word")
    @commands.guild_only()
    async def __unban_word_cmd(self, ctx: commands.Context):
        words = await BannedWords.get_banned_words(ctx.guild.id)
        if not words:
            await ctx.send("There are no banned words in this server!")
            return
        options: [discord.SelectOption] = []
        for word in words:
            options.append(discord.SelectOption(label=word["token"], default=False))

        class WordsList(discord.ui.View):
            @discord.ui.select(placeholder="Select a word to unban...", options=options)
            async def selection_made(self, select_menu: discord.ui.Select, interaction: discord.Interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message("Only the person who ran the command can remove a word from"
                                                            " this list!", ephemeral=True)
                    return
                result = await BannedWords.unban_word(interaction.guild_id, select_menu.values[0])
                if result:
                    await interaction.message.edit(f":white_check_mark: "
                                                   f"The word '{select_menu.values[0]}' is now unbanned!", view=None)
                else:
                    await interaction.message.edit(":x: That word could not be unbanned :(", view=None)
        await ctx.send("Choose a word to unban", view=WordsList())

    @staticmethod
    async def unban_word(guild_id: int, word: str) -> bool:
        result: pymongo.results.DeleteResult = main.db[BANNED_WORDS].delete_one(
            {
                "guild_id": guild_id,
                "token": word.lower()
            }
        )
        if result.deleted_count < 1:
            return False
        return True

    @commands.command(name="banned_words")
    @commands.guild_only()
    async def __banned_words_cmd(self, ctx: commands.Context):
        words = await BannedWords.get_banned_words(ctx.guild.id)
        description = ""
        if not list(words):
            description = "There are no banned words in this server"
        else:
            for word in words:
                description += f"{word['token']}\n"
        embed = discord.Embed(title="Banned Words", color=discord.Color.teal(), description=description)

        await ctx.reply(embed=embed)

    @staticmethod
    async def get_banned_words(guild_id: int):
        words = main.db[BANNED_WORDS].find(
            {
                "guild_id": guild_id
            }
        )
        return list(words)

    @staticmethod
    async def has_banned_word(guild_id: int, content: str) -> (bool, str):
        words = await BannedWords.get_banned_words(guild_id)

        for word in words:
            if content.find(word["token"]) != -1:
                return True, word["token"]
        return False, None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        ctx: commands.Context = await self.bot.get_context(message)
        if ctx.valid:
            return
        if (result := await self.has_banned_word(message.guild.id, message.content))[0]:
            await self.bot.get_cog("Warnings").add_warning(message.guild.id, message.author.id, 8,
                                                           f"[AUTO] said a banned word: {result[1]}")
            await message.delete()


def setup(bot):
    bot.add_cog(BannedWords(bot))
