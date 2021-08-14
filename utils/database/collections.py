"""
These are just the names of the different collections in the MongoDB database that the bot accesses.  The reason these
are defined here instead of elsewhere is just so that if a collection name needs to be changed, it can be changed
everywhere it is used all at once by just changing the string in this file.

Because everything is in this file, if you want to access the 'warnings' collection, for example, you will need to
import it from here
"""

BANNED_WORDS = "banned_words"
LOG_CHANNELS = "log_channels"
PUNISHMENTS = "punishments"
WARNINGS = "warnings"
BIRTHDAYS = "birthdays"
REMINDERS = "reminders"
DISABLED_COMMANDS = "disabled_commands"
