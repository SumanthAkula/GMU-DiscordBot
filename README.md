# DiscordBot
Python Based Discord Bot created by the GMU CS community

## File structure

* `assets/` contain images/files that the bot might need to send to Discord.  
* `cogs/`
	* `command_handler.py` has an event handler for `on_command_error`
	* `uwuifier.py` has a single `uwu` command handler for uwuifing messages.
	* any other cogs that you want. these files will have the command and event handlers necessary.  
* `main.py` the entry point for the bot.
* `util/` 
	* `database/`
		* `database.py` contains the `DatabaseController` class that is used for inserting to, deleting from, and querying the MongoDB database (this class is currently unused though)
	* `log_channel_types.py` contains an enum class that lists the different types of logging channels (Discord channels) this bot will need to send messages to.
