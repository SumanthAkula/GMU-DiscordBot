# DiscordBot
Python Based Discord Bot created by the GMU CS community

## File structure

* root
	* `venv/` virtual environment for developing the bot (not essential as long as you have python and dependencies on your computer)
	* `main.py` the entry point for the bot
	* `cogs/`
		* `command_handler.py` has an event handler for `on_command_error`
		* `uwuifier.py` has a single `uwu` command handler for uwuifing messages
		* any other cogs that you want. these files will have the command and event handlers necessary.  
	* `util/` (empty right now, but will have helpers and stuff later)

Stuff I'm considering adding:
* Slash commands
	* They're apparently not horrible on mobile anymore since there was an update to the mobile app
* A local SQLite database (unless we're planning on using something different) for storing invite data, banned words, warnings, birthdays, and deleted messages
	* Each of those things I just listed would be their own table in the database
	* Planned database structure:
		* `INVITE_TABLE` Table to store invite data
			* *I've not worked with invited before so I'll have to look at the API before making this feature*
		* `BANNED_WORDS_TABLE` Table to store banned words
			* `WORDS` `(TEXT)` Self explanatory
		* `MEMBER_WARNINGS_TABLE` Table to store warning data for members
			* `USER_ID` `(INTEGER)` ID of each member
			* `WARNING_COUNT` `(INTEGER)` Number of warning that user has
		* `BIRTHDAYS_TABLE` Table to store birthday stuff
			* `USER_ID` `(INTEGER)` ID of each user
			* `TIME` `(INTEGER)` The time that the birthday occurs at (probably gonna be epoch or somethign idk yet)
		* `DELETED_MESSAGES_TABLE` Table to store deleted messages
			* `USER_ID` `(INTEGER)` ID of each user
			* *I'm not sure how this will work yet.  Maybe I can store just the text but that won't work for images so yeahhh*