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
        await ctx.send(f"Banned ||{word}|| from being said in this server!")

    @commands.command(name="unban_word")
    @commands.guild_only()
    async def __unban_word_cmd(self, ctx: commands.Context, word: str):
        result: pymongo.results.DeleteResult = main.db[BANNED_WORDS].delete_one(
            {
                "guild_id": ctx.guild.id,
                "token": word.lower()
            }
        )
        if result.deleted_count < 1:
            await ctx.reply(":x: That word was not found on the banned words list! Nothing was removed")
        else:
            await ctx.reply(f":white_check_mark: '{word}' was successfully removed from the banned words list")

    @commands.command(name="banned_words")
    @commands.guild_only()
    async def __banned_words_cmd(self, ctx: commands.Context):
        words = main.db[BANNED_WORDS].find(
            {
                "guild_id": ctx.guild.id
            }
        )
        embed = discord.Embed(title="Banned Words", color=discord.Color.teal())
        if not words:
            embed.description = "There are no banned words in this server"
        else:
            for word in words:
                embed.description += f"{word['token']}\n"
        await ctx.reply(embed=embed)

    @staticmethod
    async def has_banned_word(guild_id: int, content: str) -> bool:
        words = main.db[BANNED_WORDS].find(
            {
                "guild_id": guild_id
            }
        )

        for word in words:
            if content.find(word["token"]) != -1:
                return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        ctx: commands.Context = await self.bot.get_context(message)
        if ctx.valid:
            return
        if await self.has_banned_word(message.guild.id, message.content):
            await message.channel.send(f"{message.author.mention}, you cannot say that here")
            await message.delete()


def setup(bot):
    bot.add_cog(BannedWords(bot))
