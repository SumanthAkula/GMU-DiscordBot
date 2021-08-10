# DiscordBot
Python Based Discord Bot created by the GMU CS community
This branch is managed by Sumo Akula

## File structure
* `assets/` contain images/files that the bot might need to send to Discord.  
* `cogs/`
	* `command_handler.py` has an event handler for `on_command_error`
	* `uwuifier.py` has a single `uwu` command handler for uwuifing messages.
	* any other cogs that you want. these files will have the command and event handlers necessary.  
* `main.py` the entry point for the bot.
* `secret.py` the file that contains the bot's token, and the URL/password to the MongoDB database (this file is gitignored, if you want to host the bot, you have to create this file)
* `utils/` 
	* `database/`
		* `collections.py` contains string constants for the different MongoDB collections that this bot uses
	* `log_channel_types.py` contains an enum class that lists the different types of logging channels (Discord channels) this bot will need to send messages to.
