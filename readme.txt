BANDIT BOT V1 - RELEASE BY POOCHINGTON & SCREECH
WWW.SCUMBANDIT.COM
------------------------------------------------------------------

Thanks to the few in the Scum and Python communities who have helped us along the way in creating this bot.

Use this as a guide for setting up your settings.ini file.

------------------------------------------------------------------

[SERVER SETTINGS]
Set this to match your scheduled restarts per your GPortal settings:
restart_schedule = 00:00, 06:00, 12:00, 18:00

Set this "x" minutes before your scheduled restart, when you want the reminder to appear in Discord.
the example settings mean that a reminder will be posted in Discord around 2 minutes prior to the scheduled restart.
restart_reminder = 23:58, 05:58, 11:58, 17:58

Set this to the timezone which the server/bot is running in
timezone = Europe/London


------------------------------------------------------------------

[DISCORD SETTINGS]
These toggles can also be changed "on the fly" in discord using the !toggle command, by someone who has the "administrator" role.
1 = Enabled
0/anything other than 1 = Disabled

post_admincommands = 1 or 0
admin_logs_channel = Channel ID where you want Admin logs to be posted.

post_killfeed = 1 or 0
kill_feed_channel = Channel ID where you want Kill Feed to be posted.

post_serverrestartreminder = 1 or 0
server_restart_announcements_channel = Channel ID where you want the Server Restart reminder to be posted.

post_chatlogs = 1 or 0
chat_logs_channel = Channel ID where you want Chat logs to be posted - suggest Admin only channel.

enable_raid_alarm = 1 or 0
raid_command = !raid
raid_alert_channel = Channel ID where you want the raid alarm to be posted - suggest Admin only channel.

post_serverinfo = 1 or 0 Enable or disable the Discord !server command
battlemetrics_url = the URL of your server on the BattleMetrics website

------------------------------------------------------------------

[GPORTAL SETTINGS]
login_url = https://id2.g-portal.com/login (You should not need to change this)
server_id = Your GPortal server ID
location = either us or com depending on where your GPortal server is located. You'll get this from the address bar in your webbrowser when you log in to GPortal.
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



