#BanditBot v1 Release

#imports
import discord
from discord.ext import tasks
import configparser
from configparser import RawConfigParser
from datetime import datetime
import pytz
from colors import color, red, blue, green, yellow, cyan
import re
from bs4 import BeautifulSoup
import cfscrape
import os
import json
import glob
import requests


#setup
bot = discord.Client()
tag_line = "This server is supported by BanditBot v1.0 (Free) - get a copy at www.scumbandit.com"

# main_loop
@tasks.loop(seconds=62.0)
async def main_loop():
    log(blue(">>> Main loop has started. >>>"))
    await server_restart_announcement()
    await grab_logs()
    await process_kill_feed()
    await post_admin_logs()
    await process_chat_logs()
    log(blue("<<< Main loop has ended. <<<"))


@main_loop.before_loop
async def before_loop():
    log(green("Waiting for bot to be ready."))
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    log(green(f"Bandit Bot has initiated!"))
    main_loop.start()


#main commands
async def server_restart_announcement():
    try:
        config = configparser.ConfigParser()
        with open('settings.ini', 'r', encoding="utf-8") as ini:
            config.read_file(ini)
            if config['DISCORD']['post_serverrestartreminder'] == "1":
                if await get_local_time() in config['SERVER']['restart_reminder']:
                    channel_to_send = bot.get_channel(int(config['DISCORD']['server_restart_announcements_channel']))
                    message = (f"```The server will restart shortly!\n\n"
                               f"Remember, server restarts are scheduled at {config['SERVER']['restart_schedule']}.```\n")
                    embed = discord.Embed(title="", color=0xff0000)
                    embed.set_thumbnail(url=f"http://www.scumbandit.com/weapons/Unknown.png")
                    embed.add_field(name="Scheduled Server Restart Reminder", value=message, inline=False)
                    embed.set_footer(text=f"{tag_line}")
                    await channel_to_send.send(embed=embed)
    except Exception as e:
        log(red("Unable to post server restart announcement."))
        log(red(e))


async def grab_logs():
    # load ini
    config = RawConfigParser()
    with open('settings.ini', 'r', encoding="utf-8") as ini:
        config.read_file(ini)
        server_id = config['GPORTAL']['server_id']
        location = config['GPORTAL']['location']
        user_name = config['GPORTAL']['user_name']
        password = config['GPORTAL']['password']
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
        login_url = 'https://id2.g-portal.com/login?redirect=https://www.g-portal.{0}/auth/login?redirectAfterLogin=https://www.g-portal.{0}/es/'.format(location)
        logs_url = 'https://www.g-portal.{0}/server/scum/{1}/logs'.format(location, server_id)
    # create logs folder if it doesnt exist
    if not os.path.exists(config['GPORTAL']['logs_folder']): os.makedirs(config['GPORTAL']['logs_folder'])
    with cfscrape.create_scraper() as session:
        try:
            log(yellow('Connecting to G-Portal & downloading log files.'))
            # submit login
            data = {'_method': 'POST', 'login': user_name, 'password': password, 'rememberme': '1'}
            raw_response = session.post(login_url, headers=headers, data=data)
            # grab log files
            raw_response = session.get(logs_url, headers=headers)
            response = raw_response.text
            html = BeautifulSoup(response, 'html.parser')
            select = html.find('div', {'class': 'wrapper logs'})
            loglist = select['data-logs']
            logs = json.loads(loglist)
            # sort log files by type
            for i in range(len(logs)):
                getid = logs["file_" + str(i + 1)]
                id = (getid[int(getid.find('Logs')) + 5:])
                type = id.split('_')[0]
                if config['GPORTAL'][type + '_file'] != '':
                    if id < config['GPORTAL'][type + '_file']:
                        continue
                # download specific log file & create locally
                data = {'_method': 'POST', 'load': 'true', 'ExtConfig[config]': getid}
                raw_response = session.post(logs_url, headers=headers, data=data)
                response = raw_response.text
                content = json.loads(response)
                lines = content["ExtConfig"]["content"].splitlines()
                file = config['GPORTAL']['logs_folder'] + id
                file = open(file, "a+", encoding='utf-8')
                found = False
                writing = False
                for line in lines:
                    # check name of log file
                    if id == config['GPORTAL'][type + '_file'] and not found:
                        if line == config['GPORTAL'][type + '_line']:
                            found = True
                            continue
                    else:
                        file.write(line + '\n')
                        log(green("Creating {}".format(id)))
                file.close()
                config['GPORTAL'][type + '_file'] = id
                config['GPORTAL'][type + '_line'] = lines[-1]
            with open('settings.ini', 'w', encoding="utf-8") as update:
                config.write(update)
                log(yellow("Download complete."))
        except Exception as e:
            log(red('Failed to obtain logs from Gportal!'))
            log(red(e))
            pass


async def process_kill_feed():
    #load .ini
    config = configparser.ConfigParser(allow_no_value=True)
    with open('settings.ini', 'r', encoding="utf-8") as ini:
        config.read_file(ini)
        for logfile in glob.glob(config['GPORTAL']['logs_folder'] + '/kill_*.log'):
            with open(logfile, 'r', encoding='utf8') as f:
                try:
                    # file size is bigger than zero, so must have data to process
                    if os.stat(logfile).st_size > 0:
                        if config['DISCORD']['post_killfeed'] == "1":
                            log(cyan("Updating kill feed."))
                            for line in f:
                                #select only json data lines
                                if "IsInGameEvent" in line:
                                    js = line[21::]
                                    kill_feed = json.loads(js)
                                    #dont process event kills
                                    if kill_feed["Killer"]["IsInGameEvent"] == 1:
                                        log(red("Event kill found, skipping."))
                                    else:
                                        killer_name = (kill_feed["Killer"]["ProfileName"])
                                        killer_id = (kill_feed["Killer"]["UserId"])
                                        killer_x = float((kill_feed["Killer"]["ServerLocation"]["X"]))
                                        killer_y = float((kill_feed["Killer"]["ServerLocation"]["Y"]))
                                        killer_z = float((kill_feed["Killer"]["ServerLocation"]["Z"]))

                                        victim_name = (kill_feed["Victim"]["ProfileName"])
                                        victim_id = (kill_feed["Victim"]["UserId"])
                                        victim_x = float((kill_feed["Victim"]["ServerLocation"]["X"]))
                                        victim_y = float((kill_feed["Victim"]["ServerLocation"]["Y"]))
                                        victim_z = float((kill_feed["Victim"]["ServerLocation"]["Z"]))

                                        sector = await get_sector(victim_x, victim_y)

                                        #set weapon name
                                        weapon = (kill_feed["Weapon"])
                                        if weapon == "": weapon = "Unknown"
                                        for weapons in config['WEAPONS']:
                                            if weapons.lower() in weapon.lower():
                                                weapon = config.get("WEAPONS", weapons)
                                                break

                                        #set distance
                                        for mines in config['MINES']:
                                            if mines.lower() in weapon.lower():
                                                distance = 0
                                                break
                                            else:
                                                distance = (((victim_x - killer_x) ** 2) + ((victim_y - killer_y) ** 2) + ((victim_z - killer_z) ** 2)) ** (1 / 2) / 100
                                        distance = int(distance)

                                        channel_to_send = bot.get_channel(int(config['DISCORD']['kill_feed_channel']))

                                        #send embed to channel
                                        embed = discord.Embed(title="Kill Confirmation", color=0xff0000)
                                        #embed.set_thumbnail(url=f"http://www.scumbandit.com/weapons/{WeaponURL}")
                                        # other details
                                        embed.add_field(name="**Sector**", value=sector, inline=True)
                                        embed.add_field(name="**Distance**", value=f"{distance}m", inline=True)
                                        embed.add_field(name="**Weapon**", value=weapon, inline=True)
                                        # killer details
                                        embed.add_field(name="**Killer**", value=killer_name, inline=True)
                                        # victim details
                                        embed.add_field(name="**Victim**", value=victim_name, inline=True)
                                        embed.set_footer(text=f"{tag_line}")
                                        await channel_to_send.send(embed=embed)
                    f.close()
                    os.remove(logfile)
                except Exception as e:
                    log(red("Error in post kill feed function."))
                    log(red(e))


async def post_admin_logs():
    config = configparser.ConfigParser()
    with open('settings.ini', 'r', encoding="utf-8") as ini:
        config.read_file(ini)
        for logfile in glob.glob(config['GPORTAL']['logs_folder'] + '/admin_*.log'):
            with open(logfile, 'r', encoding='utf8') as f:
                try:
                    if os.stat(logfile).st_size > 0:
                        if config['DISCORD']['post_admincommands'] == '1':
                            log(cyan("Pushing admin commands to channel."))
                            for line in f:
                                if len(line) > 50:
                                    date = line[:10:]
                                    time = line[11:19:]
                                    time.replace(".", ":")

                                    admin = line.strip()
                                    admin = re.sub(r'^.*?\'.*?:', "", admin)
                                    admin = re.sub(r'\(.*$', "", admin)

                                    command = line[40::].replace(admin, "")
                                    command = re.sub(r'^.*?\'.', "", command)

                                    channel = bot.get_channel(int(config['DISCORD']['admin_logs_channel']))

                                    await channel.send("```ini\n"
                                                           f"[{date} @ {time}] - [{admin}]\n\n"
                                                           f"{command}```")
                    f.close()
                    os.remove(logfile)
                except Exception as e:
                    log(red("Unable to post admin logs to Discord."))
                    log(red(e))


async def process_chat_logs():
    try:
        config = configparser.ConfigParser()
        with open('settings.ini', 'r', encoding="utf-8") as ini:
            config.read_file(ini)
            for logfile in glob.glob(config['GPORTAL']['logs_folder'] + '/chat_*.log'):
                with open(logfile, 'r', encoding='utf8') as f:
                    if os.stat(logfile).st_size > 0:
                        log(cyan("Pushing chat logs to channel."))
                        for line in f:
                            if len(line) > 50:
                                date = line[:10:]
                                time = line[11:19:]
                                time.replace(".", ":")

                                steam_id = line[22:39:]

                                player_name = line.strip()
                                player_name = re.sub(r'^.*?\'.*?:', "", player_name)
                                player_name = re.sub(r'\(.*$', "", player_name)

                                player_id = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', "", line[21::])
                                player_id = player_id.replace("' ", "").replace("'", " ")
                                z = len(player_name) + 18
                                player_id = player_id.replace(player_id[18:int(z):], "")
                                player_id = player_id[19::]
                                player_id = re.findall("^.*?\)", player_id)
                                player_id = player_id[0].replace("(", "").replace(")", "")

                                chat_type = line.strip()
                                chat_type = re.sub(r'^.*?\'.*?\'.\'', "", chat_type)
                                chat_type = re.sub(r':.*$', "", chat_type)

                                chat_message = re.sub(r'^.*(\d).\'.\'', "", line)
                                chat_message = re.sub(r'^.*?:.', "", chat_message)
                                chat_message = chat_message[:-2:]

                                raid_cmd = str(config['DISCORD']['raid_command'])

                                #raid alarm
                                if raid_cmd in line:
                                    if config['DISCORD']['enable_raid_alarm'] == "1":
                                        channel_to_send = bot.get_channel(int(config['DISCORD']['raid_alert_channel']))
                                        #raid alarm details
                                        embed = discord.Embed(title="RAID ALARM", color=0xff0000)
                                        embed.set_thumbnail(url="http://www.scumbandit.com/weapons/alarm.png")
                                        embed.add_field(name="**Name**", value=player_name, inline=True)
                                        embed.add_field(name="**Date**", value=date, inline=True)
                                        embed.add_field(name="**Time**", value=time, inline=True)
                                        embed.add_field(name="\u200b", value="\u200b", inline=False)
                                        embed.set_footer(text=f"{tag_line}")
                                        await channel_to_send.send(embed=embed)
                                        await channel_to_send.send("@everyone")

                                #general chat logs
                                if config['DISCORD']['post_chatlogs'] == "1":
                                    channel = bot.get_channel(int(config['DISCORD']['chat_logs_channel']))
                                    if chat_type == "Global":
                                        await channel.send("```ini\n"
                                                           f"+[Global Chat] - [{date} @ {time}] - [{player_name}]+\n\n"
                                                           f"{chat_message}```")
                                    if chat_type == "Local":
                                        await channel.send(f"```+[Local Chat] - [{date} @ {time}] - [{player_name}]+\n\n"
                                                           f"{chat_message}```")
                                    if chat_type == "Squad":
                                        await channel.send("```diff\n"
                                                           f"+[Squad Chat] - [{date} @ {time}] - [{player_name}]+\n\n"
                                                           f"{chat_message}```")
                    f.close()
                    os.remove(logfile)
    except Exception as e:
        log(red("Unable to post chat logs."))
        print(e)


#commands section
@bot.event
async def on_message(message):
    #make sure bot ignores own messages
    if message.author == bot.user:
        return

    #admin commands section
    if message.author.guild_permissions.administrator:

        if message.content.startswith('!toggle'):
            setting = message.content.replace("!toggle ", "")
            await toggle(setting, message.channel.id)

    #player commands section
    if message.content.startswith('!server'):
        await post_server_info(message.author.id)
        await message.delete()


#misc commands
def log(text):
    print('[%s] %s' % (datetime.strftime(datetime.now(), '%H:%M:%S'), text))


async def get_local_time():
    config = configparser.ConfigParser()
    with open('settings.ini', 'r', encoding="utf-8") as ini:
        config.read_file(ini)
        specified_local_time = config['SERVER']['timezone']
        now = datetime.now()
        full_date_time = datetime.now(pytz.timezone(specified_local_time))
        time_now = full_date_time.strftime("%H:%M")
        return time_now


def get_token():
    config = configparser.ConfigParser()
    with open('settings.ini', 'r', encoding="utf-8") as ini:
        config.read_file(ini)
        return config['BANDITBOT']['token']


async def get_sector(coordsX, coordsY):
    ssector = 0
    ssectors = ["D4", "D3", "D2", "D1", "C4", "C3", "C2", "C1", "B4", "B3", "B2", "B1", "A4", "A3", "A2", "A1"]
    if coordsX < 310000: ssector += 1
    if coordsX < 0: ssector += 1
    if coordsX < (-310000): ssector += 1
    if coordsY < 310000: ssector += 4
    if coordsY < 0: ssector += 4
    if coordsY < (-310000): ssector += 4
    return ssectors[ssector]


async def toggle(setting, channel):
    config = configparser.ConfigParser()
    with open('settings.ini', 'r', encoding="utf-8") as ini:
        config.read_file(ini)

        if "admin commands" in setting:
            if config['DISCORD']['post_admincommands'] == "1":
                config['DISCORD']['post_admincommands'] = "0"
                await bot.get_channel(channel).send("```> Posting admin commands now disabled.```")
            else:
                config['DISCORD']['post_admincommands'] = "1"
                await bot.get_channel(channel).send("```> Posting admin commands now enabled.```")
            with open('settings.ini', 'w', encoding="utf-8") as update:
                config.write(update)

        elif "kill feed" in setting:
            if config['DISCORD']['post_killfeed'] == "1":
                config['DISCORD']['post_killfeed'] = "0"
                await bot.get_channel(channel).send("```> Posting kill feed now disabled.```")
            else:
                config['DISCORD']['post_killfeed'] = "1"
                await bot.get_channel(channel).send("```> Posting kill feed now enabled.```")
            with open('settings.ini', 'w', encoding="utf-8") as update:
                config.write(update)

        elif "server info" in setting:
            if config['DISCORD']['post_serverinfo'] == "1":
                config['DISCORD']['post_serverinfo'] = "0"
                await bot.get_channel(channel).send("```> !server command disabled.```")
            else:
                config['DISCORD']['post_serverinfo'] = "1"
                await bot.get_channel(channel).send("```> !server command enabled.```")
            with open('settings.ini', 'w', encoding="utf-8") as update:
                config.write(update)

        elif "restart reminders" in setting:
            if config['DISCORD']['post_serverrestartreminder'] == "1":
                config['DISCORD']['post_serverrestartreminder'] = "0"
                await bot.get_channel(channel).send("```> Server restart reminders disabled.```")
            else:
                config['DISCORD']['post_serverrestartreminder'] = "1"
                await bot.get_channel(channel).send("```> Server restart reminders enabled.```")
            with open('settings.ini', 'w', encoding="utf-8") as update:
                config.write(update)

        elif "raid alarm" in setting:
            if config['DISCORD']['enable_raid_alarm'] == "1":
                config['DISCORD']['enable_raid_alarm'] = "0"
                await bot.get_channel(channel).send("```> Server raid alerts disabled.```")
            else:
                config['DISCORD']['enable_raid_alarm'] = "1"
                await bot.get_channel(channel).send("```> Server raid alerts enabled.```")
            with open('settings.ini', 'w', encoding="utf-8") as update:
                config.write(update)

        elif "chat logs" in setting:
            if config['DISCORD']['post_chatlogs'] == "1":
                config['DISCORD']['post_chatlogs'] = "0"
                await bot.get_channel(channel).send("```> Posting chat logs disabled.```")
            else:
                config['DISCORD']['post_chatlogs'] = "1"
                await bot.get_channel(channel).send("```> Posting chat logs enabled.```")
            with open('settings.ini', 'w', encoding="utf-8") as update:
                config.write(update)

        else:
            embed = discord.Embed(color=0xff0000)
            embed.set_thumbnail(url="http://www.scumbandit.com/weapons/Unknown.png")
            embed.add_field(name='!toggle admin commands', value="Turn on/off automatic posting of Admin commands.", inline=False)
            embed.add_field(name='!toggle kill feed', value="Turn on/off kill feed notifications.", inline=False)
            embed.add_field(name='!toggle server info', value="Turn on/off !server command.", inline=False)
            embed.add_field(name='!toggle restart reminders', value="Turn on/off server scheduled restart reminders.", inline=False)
            embed.add_field(name='!toggle raid alarm', value="Turn on/off server raid alarm function.", inline=False)
            embed.add_field(name='!toggle chat logs', value="Turn on/off automatic posting of server chat logs.", inline=False)
            embed.add_field(name="\u200b", value=f"\u200b", inline=False)
            embed.set_footer(text=f"{tag_line}")
            await bot.get_channel(channel).send(embed=embed)


async def post_server_info(user):
    config = configparser.ConfigParser()
    with open('settings.ini', 'r', encoding="utf-8") as ini:
        config.read_file(ini)
        if config['DISCORD']['post_serverinfo'] == "1":
            url = config['DISCORD']['battlemetrics_url']
            html_content = requests.get(url).text
            soup = BeautifulSoup(html_content, features="html.parser")
            for data in soup.find_all("script", id="storeBootstrap", type="application/json"):
                js = re.sub("^<.+?>", "", str(data))
                js = re.sub("</script>$", "", js)
                js = json.loads(js)
                bm_id = url[-7::]
                server_name = js['servers']['servers'][bm_id]['name']
                online_players = js['servers']['servers'][bm_id]['players']
                max_players = js['servers']['servers'][bm_id]['maxPlayers']
                server_rank = js['servers']['servers'][bm_id]['rank']
                server_ip = js['servers']['servers'][bm_id]['ip']
                server_port = js['servers']['servers'][bm_id]['port']
                server_status = js['servers']['servers'][bm_id]['status']

                embed = discord.Embed(color=0x0008ff)
                #embed.set_thumbnail(url="http://www.scumbandit.com/weapons/Unknown.png")
                embed.add_field(name=server_name, value="\u200b", inline=False)
                embed.add_field(name="Players", value=f'{online_players} / {max_players}', inline=True)
                embed.add_field(name="Status", value=server_status, inline=True)
                embed.add_field(name="Rank", value=server_rank, inline=True)
                embed.add_field(name="Server IP & Port", value=f'{server_ip} : {server_port}', inline=True)
                embed.add_field(name="\u200b", value=f"\u200b", inline=False)
                embed.set_footer(text=f"{tag_line}")
                await bot.get_user(user).send(embed=embed)
        else:
            await bot.get_user(user).send(">>> !server command is currently disabled.")


bot.run(get_token())