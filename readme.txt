BANDIT BOT V1 - RELEASE BY POOCHINGTON & SCREECH
WWW.SCUMBANDIT.COM
------------------------------------------------------------------

Thanks to the few in the Scum and Python communities who have helped us along the way in creating this bot.

Use this as a guide for setting up your settings.ini file.

To set up this Discord bot, you first need to create your own Discord bot on the Discord Developer Portal (https://discord.com/developers). This is a 2 minute process and there are numerous guides available on how to do this on Google if you are unsure. Once you have set up your bot, you need the bot's TOKEN to be able to associate this code with your Bot.

You also need to enable Developer mode in Discord (again, guides are available on Google if you are unsure) to get your "Channel IDs" to set up the [DISCORD SETTINGS] section below. Once Developer mode is enabled in Discord, you simply right-click the channel where you want the Bot to post messages to and select "Copy ID".

Please note, the first time you run this bot it might take a while to catch up "posting things" to Discord, depending on how busy your server has been. Just leave it running, it will catch up.


------------------------------------------------------------------

[BANDITBOT]
token = Your_Discord_Bot_Token_Here

------------------------------------------------------------------

[DISCORD SETTINGS]
These toggles can also be changed "on the fly" in discord using the !toggle command, by someone who has the "administrator" role.
1 = Enabled
0/anything other than 1 = Disabled

post_admincommands = 1 or 0
admin_logs_channel = Channel ID where you want Admin logs to be posted. 

post_killfeed = 1 or 0
kill_feed_channel = Channel ID where you want Kill Feed to be posted.

post_chatlogs = 1 or 0
chat_logs_channel = Channel ID where you want Chat logs to be posted - suggest Admin only channel.

post_serverinfo = 1 or 0 Enable or disable the Discord !server command
battlemetrics_url = the URL of your server on the BattleMetrics website

------------------------------------------------------------------

[GPORTAL SETTINGS]
login_url = https://id2.g-portal.com/login (You should not need to change this)
server_id = Your GPortal server ID
location = either US or COM depending on where your GPortal server is located. You'll get this from the address bar in your webbrowser when you log in to GPortal.
logs_folder = where you want your logs to be downloaded to (default is logs/)
user_name = GPortal Username
password = GPortal Password

------------------------------------------------------------------

[WEAPONS SECTION]
The format used here is "scumcode = Name to show up on the Kill Feed".
Edit it however you want to. 
When new weapons are released on the game, you'll have to add them into the settings.ini under the [WEAPONS] section for them to be properly displayed on the Kill Feed.

------------------------------------------------------------------

[MINES SECTION]
The format used here is "scumcode = mine".
Make sure all mines and traps capable of killing a player are listed here.



