import discord
from discord.ext import commands

import main
from utils.database.collections import BANNED_WORDS


class BannedWords(commands.Cog, name="Banned Word Remover"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban_word")
    async def __ban_word_cmd(self, ctx: commands.Context, word: str):
        """
        Adds 'word' to the list of words than cannot be said in text channels

        Arguments:
            word: the word to ban
        """
        main.db["banned_words"].insert_one(
            {
                "guild_id": ctx.guild.id,
                "token": word.lower()
            }
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        words = main.db[BANNED_WORDS].find(
            {
                "guild_id": message.guild.id
            }
        )
        for word in words:
            print(word["token"])


def setup(bot):
    bot.add_cog(BannedWords(bot))
