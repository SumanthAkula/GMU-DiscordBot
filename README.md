# DiscordBot
Python Based Discord Bot created by the GMU CS community

File structure

* root
	* `venv/` virtual environment for developing the bot (not essential as long as you have python and dependencies on your computer)
	* `main.py` the entry point for the bot
	* `cogs/`
		* `command_handler.py` has an event handler for `on_command_error`
		* `uwuifier.py` has a single `uwu` command handler for uwuifing messages
		* any other cogs that you want. these files will have the command and event handlers necessary.  
	* `util/` (empty right now, but will have helpers and stuff later)
