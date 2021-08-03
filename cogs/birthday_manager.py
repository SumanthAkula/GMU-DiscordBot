import datetime
import re
from typing import Optional

import discord
import pymongo.results
from discord.ext import commands, tasks

import main
from utils.database.collections import BIRTHDAYS


class BirthdayManager(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.birthday_checker.start()

    @tasks.loop(seconds=1)
    async def birthday_checker(self):
        bdays = main.db[BIRTHDAYS].find()
        today = datetime.datetime.now()
        for bday in bdays:
            if bday["birthday"].day == today.day and bday["birthday"].month == today.month\
                    and today.year - bday["last_wished"].year >= 1:
                # it's someone's birthday, so we gotta wish them
                print(f"Happy birthday {bday['member_id']}!")
                main.db[BIRTHDAYS].update_one(
                    {
                        "_id": bday["_id"]
                    },
                    {
                        "$set": {
                            "last_wished": today
                        }
                    },
                    upsert=True
                )

    @commands.group("birthday", aliases=["bday"], pass_context=True, invoke_without_command=True)
    @commands.guild_only()
    async def __bday_command(self, ctx: commands.Context):
        """
        Get or set your birthday and the bot can wish you a happy birthday
        """
        await ctx.send(f"Run the `{ctx.prefix}help birthday` for information on how to use this command")

    @__bday_command.command("set", pass_context=True, invoke_without_command=True)
    async def __set(self, ctx: commands.Context, birthday: str):
        """
        Set or change your birthday

        Arguments:
            birthday: your birthday in UNIX epoch time :V
        """
        # parse birthday from input ugh
        regex = re.compile(r"\d{2}/\d{2}/\d{4}")
        if len(birthday) != 10 or regex.match(birthday) is None:
            await ctx.reply(":x: Your birthday was not formatted properly! Please format it as MM/DD/YYYY")
            return
        month, day, year = map(int, birthday.split("/"))

        result: pymongo.results.UpdateResult = main.db[BIRTHDAYS].update_one(
            {
                "guild_id": ctx.guild.id,
                "member_id": ctx.author.id
            },
            {
                "$set": {
                    "guild_id": ctx.guild.id,
                    "member_id": ctx.author.id,
                    "birthday": datetime.datetime(year, month, day),
                    "last_wished": datetime.datetime.fromtimestamp(0)
                }
            },
            upsert=True
        )
        if result.matched_count >= 1:
            await ctx.reply(":white_check_mark: Your birthday has been updated")
        else:
            await ctx.reply(":white_check_mark: Your birthday has been added")

    @__bday_command.command("get", pass_context=True, invoke_without_command=True)
    async def __get(self, ctx: commands.Context):
        """
        Get your birthday (in case you forget it or something lol)
        """
        bday = main.db[BIRTHDAYS].find_one(
            {
                "guild_id": ctx.guild.id,
                "member_id": ctx.author.id
            }
        )
        if bday is None:
            await ctx.reply("You have not set your birthday on this server!")
        else:
            await ctx.reply(f"Your birthday is on {bday['birthday'].strftime('%B %d, %Y')}")

    @__bday_command.command("age", pass_context=True, invoke_without_command=True)
    async def __age(self, ctx: commands.Context, member: Optional[discord.Member]):
        """
        Get the age of you or another member in the server

        Arguments:
            member (optional): the member you want to get the age of. if no member is specified, the command will return
             the age of whoever ran the command
        """
        if member is None:
            member = ctx.author
        today = datetime.datetime.now()
        bday = main.db[BIRTHDAYS].find_one(
            {
                "guild_id": ctx.guild.id,
                "member_id": member.id
            }
        )
        if bday is None:
            await ctx.reply(":x: That user has not saved their birthday to this bot!")
            return
        bday = bday["birthday"]
        time_delta = today.timestamp() - bday.timestamp()
        years = time_delta // 31556926  # calculate years
        time_delta -= years * 31556926
        months = time_delta // 2629743  # calculate months
        time_delta -= months * 2629743
        days = time_delta // 86400      # calculate days
        await ctx.reply(f"{years:.0f} years, {months:.0f} months, {days:.0f} days")


def setup(bot):
    bot.add_cog(BirthdayManager(bot))
