# Libraries
import asyncio
import asyncpraw
import cpuinfo
import datetime
import discord
import matplotlib
import mysql.connector
import numpy as np
import os
import platform
import psutil
import pyotp
import random
import re
import requests
import sys
import time
import uuid
from PIL import Image
from colormap import rgb2hex, hex2rgb
from discord.ext import commands
from discord.utils import get
from discord_components import *
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
from dotenv import load_dotenv
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from mcstatus import MinecraftServer
from mysql.connector import Error


class PixelBot:
    def __init__(self):
        pass

    def run():
        startup_start_timer = time.time()

        # Init
        load_dotenv()
        client = commands.AutoShardedBot(
            shard_count=1, command_prefix=".", intents=discord.Intents.all()
        )
        server_ip = os.getenv("IP")
        server = MinecraftServer.lookup(server_ip)
        slash = SlashCommand(client, sync_commands=True)
        reddit = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="PixelBotV1",
        )

        # Variables
        guild_ids = [834516102184828970]
        snipe_message_author = {}
        snipe_message_content = {}
        snipe_message_time = {}
        esnipe_message_author = {}
        before_esnipe_message_content = {}
        after_esnipe_message_content = {}
        esnipe_message_time = {}
        ops = [551398454962946049, 589529734631784448]
        global all_posts
        all_posts = []
        # Emoji's
        checkmark = "a:checkmark:848898022921732166"
        cross = "a:cross:848897550610333737"
        # No U words
        gei = ["pixiebot gei", "pixiebot gay", "spirax gei", "spirax gay"]

        async def log(message):
            print(message)
            log_channel = await client.fetch_channel(869135534163886110)
            await log_channel.send(
                "`"
                + str(datetime.datetime.utcnow())
                + "+00:00 app[worker.1]: "
                + message
                + "`"
            )
            return

        def find(url):
            regex = "([^\\s]+(\\.(jpe?g|png|gif|bmp))$)"
            p = re.compile(regex)
            if not url == None:
                if re.search(p, url):
                    return True
                else:
                    return False
            else:
                return False

        # Main Program

        # Connection Commands
        @client.event
        async def on_connect():
            log_channel = await client.fetch_channel(869135534163886110)
            await log_channel.send(
                "`"
                + str(datetime.datetime.utcnow())
                + "+00:00 heroku[worker.1]: "
                + "Starting process "
                "with command "
                "'python Main.py'" + "`"
            )
            await log_channel.send(
                "`"
                + str(datetime.datetime.utcnow())
                + "+00:00 heroku[worker.1]: "
                + "State changed from "
                "starting to up" + "`"
            )
            await log(
                f"Connected to Discord (latency: {client.latency * 1000:,.0f} ms)"
            )

        @client.event
        async def on_ready():
            DiscordComponents(client)
            client.remove_command("help")
            client.loop.create_task(status_task())
            client.loop.create_task(reddit_update())
            client.loop.create_task(channel_update())
            try:
                discovery.build(
                    "commentanalyzer",
                    "v1alpha1",
                    developerKey=os.getenv("API_KEY"),
                    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version"
                    "=v1alpha1",
                    static_discovery=False,
                )
                print("Successfully connected to Google Perspective Api")
            except:
                print("Google Perspective Api Error")
            global startTime
            startTime = time.time()
            await log(
                f"{client.user} is Ready. (Startup Time - {round((time.time() - startup_start_timer), 2)}s)"
            )

        @client.event
        async def on_shard_ready(shard_id):
            print(f"Shard ID {shard_id} is ready")

        @client.event
        async def on_resumed():
            await log("Bot reconnected")

        @client.event
        async def on_disconnect():
            await log("Bot disconnected")

        # Changing Bot Status
        async def status_task():
            while client.is_ready():
                random_temp = random.randint(1, 9)
                if random_temp == 1:
                    await client.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.playing,
                            name="on play.pixel-heim.com",
                        )
                    )
                    await asyncio.sleep(random.randint(15, 35))
                elif random_temp == 2:
                    await client.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching, name="Server Status"
                        )
                    )
                    await asyncio.sleep(random.randint(15, 30))
                elif random_temp == 3:
                    await client.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.listening, name="General Chat"
                        )
                    )
                    await asyncio.sleep(random.randint(15, 30))
                elif random_temp == 4:
                    await client.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.listening, name=".help"
                        )
                    )
                    await asyncio.sleep(random.randint(15, 25))
                elif random_temp == 5:
                    await client.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching, name="over PixelHeim"
                        )
                    )
                    await asyncio.sleep(random.randint(15, 30))
                elif random_temp == 6:
                    await client.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching, name="Cpu Usage"
                        )
                    )
                    await asyncio.sleep(random.randint(5, 15))
                elif random_temp == 7:
                    await client.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching, name="Ram Usage"
                        )
                    )
                    await asyncio.sleep(random.randint(5, 15))
                elif random_temp == 8:
                    await client.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching, name="People Quarrel"
                        )
                    )
                    await asyncio.sleep(random.randint(5, 10))
                elif random_temp == 9:
                    await client.change_presence(
                        activity=discord.Activity(
                            type=discord.ActivityType.watching,
                            name="PixelHeim's Videos",
                        )
                    )
                    await asyncio.sleep(random.randint(10, 25))

        # Updating Reddit Database
        async def reddit_update():
            while client.is_ready():
                reddit_fetch_start = time.time()
                await log("Fetching submissions from Reddit")
                subreddit = await reddit.subreddit("memes")
                async for submission in subreddit.top("week", limit=500):
                    if not submission.stickied:
                        all_posts.append(submission)
                await log(
                    f"Fetched submissions in {str(datetime.timedelta(seconds=int(round(time.time() - reddit_fetch_start))))} seconds"
                )
                await asyncio.sleep(3600)

        # Updating Channel Names
        async def channel_update():
            while client.is_ready():
                temp = 0
                guild = client.get_guild(834516102184828970)

                # Roles
                staffrole = guild.get_role(834716935018512395)
                botrole = guild.get_role(834702204421537792)

                # Members Counts
                membercount = guild.member_count
                staffcount = len(staffrole.members)
                botcount = len(botrole.members)

                # Channels
                allmembers = await client.fetch_channel(842317190677266456)
                serverplayers = await client.fetch_channel(841387979427545148)
                staff = await client.fetch_channel(835074204721610763)
                bots = await client.fetch_channel(835073527312154634)
                if str(allmembers) != "All Members: {0}".format(membercount):
                    await log("Updated All Members: {0}".format(membercount))
                    await allmembers.edit(name="All Members: {0}".format(membercount))

                if str(staff) != "Staff: {0}".format(staffcount):
                    await log("Updated Staff: {0}".format(staffcount))
                    await staff.edit(name="Staff: {0}".format(staffcount))

                if str(bots) != "Bots: {0}".format(botcount):
                    await log("Updated Bots:{0}".format(botcount))
                    await bots.edit(name="Bots: {0}".format(botcount))

                try:
                    status = server.status()
                    temp = 1
                except:
                    if str(serverplayers) != "Server Status: Offline":
                        await log(
                            "Server has not responded waiting for 60 seconds and retrying"
                        )
                        await asyncio.sleep(60)
                        try:
                            status = server.status()
                            temp = 1
                        except:
                            temp = 0
                            await log(
                                "Server hasn't responded on 2nd Attempt updated Server Status: Offline"
                            )
                            await serverplayers.edit(name="Server Status: Offline")

                if temp == 1:
                    if str(serverplayers) != "Server Players: {0}".format(
                        status.players.online
                    ):
                        await log(
                            "Updated Server Players: {0}".format(status.players.online)
                        )
                        await serverplayers.edit(
                            name="Server Players: {0}".format(status.players.online)
                        )
                await asyncio.sleep(300)

        # User Join Welcome Message
        @client.event
        async def on_member_join(member):
            welcomechannel = await client.fetch_channel(834516102649741349)
            await log("{0} joined the server".format(member.name))
            welcome = discord.Embed(
                title="**We hope to meet you at play.pixel-heim.com**",
                description="Please check <#834687920211755049> and <#836172359446298674> before checking out the other "
                "channels to meet other players!",
                colour=discord.Colour.from_rgb(255, 0, 0),
            )
            welcome.set_image(url="https://i.imgur.com/fdGMZdu.png")
            await welcomechannel.send(
                "**Welcome to PixelHeim {0} !**".format(member.mention), embed=welcome
            )
            try:
                await member.send(
                    "**Welcome to PixelHeim's Discord server!**\nDon't forget to read the <#834687920211755049>\nHere is "
                    "our server IP: **play.pixel-heim.com**"
                )
            except:
                await log(
                    f"{member.name} has direct messages from server members set to off"
                )

        # Nitro Booster Check
        @client.event
        async def on_member_update(before, after):
            if len(before.roles) < len(after.roles):
                guild = client.get_guild(834516102184828970)
                boost_channel_staff = await client.fetch_channel(853716907224203294)
                boost_channel = await client.fetch_channel(853734369113931816)
                roles_change = list(set(after.roles) - set(before.roles))
                if str(roles_change[0]) == "PixelHeim Booster":
                    await log("{0} boosted the server.".format(after.name))
                    await boost_channel_staff.send(
                        "{1} boosted the server.Give the role to {0}".format(
                            after.name, after.mention
                        )
                    )
                    boost = discord.Embed(
                        title="**Thank you for boosting the server, {0}!!**".format(
                            after.name
                        ),
                        description="Enjoy your [In Game Perks](https://discord.com/channels/834516102184828970/834689721484836874/856087996780511232).",
                        colour=discord.Colour.from_rgb(255, 0, 0),
                    )
                    boost.set_thumbnail(url=after.avatar_url)
                    boost.set_footer(
                        text="Total server boosts: {0}".format(
                            guild.premium_subscription_count
                        )
                    )
                    await boost_channel.send(embed=boost)
            elif len(before.roles) > len(after.roles):
                boost_channel_staff = await client.fetch_channel(853716907224203294)
                roles_change = list(set(before.roles) - set(after.roles))
                if str(roles_change[0]) == "PixelHeim Booster":
                    await log(
                        "{0}'s server boost ended or was cancelled.".format(after.name)
                    )
                    await boost_channel_staff.send(
                        "{1}'s server boost ended or was cancelled.Remove the in game role from {0}".format(
                            after.name, after.mention
                        )
                    )

        # Main Listeners
        @client.listen("on_message")
        async def toxic_check(message):
            if not message.author.bot:
                if client.is_ready():
                    if not str(message.channel.type) == "private":
                        if not message.content == "":
                            guild = client.get_guild(834516102184828970)
                            warn = discord.Embed(
                                title="Please refrain from using inappropriate language!",
                                description="You have been warned since your message was detected to be toxic.",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            warn.set_author(
                                name=message.author, icon_url=message.author.avatar_url
                            )
                            warn.set_footer(
                                text="Report this to the staff if you think this was a mistake."
                            )
                            try:
                                report_channel = await client.fetch_channel(
                                    867676625063116830
                                )
                                google_client = discovery.build(
                                    "commentanalyzer",
                                    "v1alpha1",
                                    developerKey=os.getenv("API_KEY"),
                                    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version"
                                    "=v1alpha1",
                                    static_discovery=False,
                                )
                                analyze_request = {
                                    "comment": {"text": f"{message.content}"},
                                    "languages": ["en"],
                                    "requestedAttributes": {
                                        "TOXICITY": {},
                                        "SEVERE_TOXICITY": {},
                                    },
                                }
                                response = (
                                    google_client.comments()
                                    .analyze(body=analyze_request)
                                    .execute()
                                )
                                if (
                                    round(
                                        (
                                            response["attributeScores"][
                                                "SEVERE_TOXICITY"
                                            ]["spanScores"][0]["score"]["value"]
                                        )
                                        * 100,
                                        1,
                                    )
                                    > 85
                                ):
                                    toxic = discord.Embed(
                                        title="Severely Toxic Message Detected",
                                        description=f'"[{message.content}]({message.jump_url})"',
                                        colour=discord.Colour.from_rgb(255, 0, 0),
                                    )
                                    toxic.set_author(
                                        name=message.author,
                                        icon_url=message.author.avatar_url,
                                    )
                                    toxic.add_field(
                                        name="Channel:",
                                        value=str(message.channel).capitalize(),
                                    )
                                    toxic.add_field(
                                        name="Toxicity Value:",
                                        value=round(
                                            (
                                                response["attributeScores"][
                                                    "SEVERE_TOXICITY"
                                                ]["spanScores"][0]["score"]["value"]
                                            ),
                                            2,
                                        ),
                                    )
                                    await report_channel.send(embed=toxic)
                                    if (
                                        round(
                                            (
                                                response["attributeScores"][
                                                    "SEVERE_TOXICITY"
                                                ]["spanScores"][0]["score"]["value"]
                                            )
                                            * 100,
                                            1,
                                        )
                                        > 90
                                    ):
                                        if message.channel.id not in [
                                            834701773071450143,
                                            834702336839909376,
                                            834520752568664136,
                                        ]:
                                            if (
                                                get(guild.roles, id=834716935018512395)
                                                not in message.author.roles
                                            ):
                                                await message.reply(embed=warn)
                                elif (
                                    round(
                                        (
                                            response["attributeScores"]["TOXICITY"][
                                                "spanScores"
                                            ][0]["score"]["value"]
                                        )
                                        * 100,
                                        1,
                                    )
                                    > 85
                                ):
                                    toxic = discord.Embed(
                                        title="Toxic Message Detected",
                                        description=f'"[{message.content}]({message.jump_url})"',
                                        colour=discord.Colour.from_rgb(255, 0, 0),
                                    )
                                    toxic.set_author(
                                        name=message.author,
                                        icon_url=message.author.avatar_url,
                                    )
                                    toxic.add_field(
                                        name="Channel:",
                                        value=str(message.channel).capitalize(),
                                    )
                                    toxic.add_field(
                                        name="Toxicity Value:",
                                        value=round(
                                            (
                                                response["attributeScores"]["TOXICITY"][
                                                    "spanScores"
                                                ][0]["score"]["value"]
                                            ),
                                            2,
                                        ),
                                    )
                                    await report_channel.send(embed=toxic)
                                    if (
                                        round(
                                            (
                                                response["attributeScores"]["TOXICITY"][
                                                    "spanScores"
                                                ][0]["score"]["value"]
                                            )
                                            * 100,
                                            1,
                                        )
                                        > 90
                                    ):
                                        if message.channel.id not in [
                                            834701773071450143,
                                            834702336839909376,
                                            834520752568664136,
                                        ]:
                                            if (
                                                get(guild.roles, id=834716935018512395)
                                                not in message.author.roles
                                            ):
                                                await message.reply(embed=warn)
                            except HttpError as e:
                                await log(
                                    "Error response status code : {0}, reason : {1}".format(
                                        e.status_code, e.error_details
                                    )
                                )

        @client.listen("on_message")
        async def message_commands(message):
            if not message.author.bot:
                if client.is_ready():
                    if not str(message.channel.type) == "private":

                        if "<@!841357639685242890>" in message.content:
                            await log(f"{message.author} pinged me.")
                            await message.reply("Type `.help` for more info.")

                        if message.channel.id == 848894973876764672:
                            await log(
                                f"New message detected in <#848894973876764672> adding reactions"
                            )
                            await message.add_reaction(checkmark)
                            await message.add_reaction(cross)

                        if ".ticket" in message.content.lower():
                            await log(f"{message.author} used .ticket")
                            await message.add_reaction(checkmark)
                            ticket = discord.Embed(
                                title="**How to File a Ticket.**",
                                description="Go to <#834520977694130226> and click on the :tickets: button.",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            ticket.set_image(url="https://i.imgur.com/2nR55qk.png")
                            ticket.set_thumbnail(url="https://i.imgur.com/PSfetR6.png")
                            await message.channel.send(embed=ticket)

                        if ".report" in message.content.lower():
                            await log(f"{message.author} used .report")
                            await message.add_reaction(checkmark)
                            report = discord.Embed(
                                title="**Format For Reporting A Player:-**",
                                description="Your Name:\nName of the player your reporting:\nReason:\nProof:",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            report.set_thumbnail(url="https://i.imgur.com/PSfetR6.png")
                            await message.channel.send(embed=report)

                        if ".appeal" in message.content.lower():
                            await log(f"{message.author} used .appeal")
                            await message.add_reaction(checkmark)
                            appeal = discord.Embed(
                                title="**Hello Pixels please follow the following format to appeal for your ban**",
                                description="1. Your Name in-game:\n2. Name of the staff who banned you:\n3.Reason for "
                                "ban:\n4.Is your ban reasonable:\n5.How long is your ban:\n6.Why should we unban "
                                "you:",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            appeal.set_thumbnail(url="https://i.imgur.com/PSfetR6.png")
                            await message.channel.send(embed=appeal)

                        if ".format" in message.content.lower():
                            await log(f"{message.author} used .format")
                            await message.add_reaction(checkmark)
                            format = discord.Embed(
                                title="**Hello Pixels our staff will be here soon to help you, In the meantime please "
                                "follow the format and describe your concern:**",
                                description="Your In Game Name :\nConcern :\nProof :",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            format.set_thumbnail(url="https://i.imgur.com/PSfetR6.png")
                            await message.channel.send(embed=format)

                        if ".ip" in message.content.lower():
                            await log(f"{message.author} used .ip")
                            await message.add_reaction(checkmark)
                            ip = discord.Embed(
                                title="**IP**",
                                description=f"**{server_ip}**",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            ip.set_thumbnail(url="https://i.imgur.com/PSfetR6.png")
                            await message.channel.send(embed=ip)

                        if (
                            ".status" in message.content.lower()
                            and message.channel.id
                            not in [834517964308873242, 835431995865038858]
                        ):
                            await log(f"{message.author} used .status")
                            try:
                                temp = 1
                                status = server.status()
                            except:
                                offline = discord.Embed(
                                    colour=discord.Colour.from_rgb(255, 0, 0),
                                    description="Server is currently offline",
                                )
                                offline.set_author(
                                    name="Server Status:",
                                    icon_url="https://i.imgur.com/PSfetR6.png",
                                )
                                await message.channel.send(embed=offline)
                                await message.add_reaction(cross)
                                temp = 0
                            if temp == 1:
                                players = discord.Embed(
                                    colour=discord.Colour.from_rgb(255, 0, 0),
                                    description="There are **{0}** players currently online".format(
                                        status.players.online
                                    ),
                                )
                                players.set_author(
                                    name="Server Status:",
                                    icon_url="https://i.imgur.com/PSfetR6.png",
                                )
                                await message.channel.send(embed=players)
                                await message.add_reaction(checkmark)

                        if ".help" in message.content.lower():
                            await log(f"{message.author} used .help")
                            await message.add_reaction(checkmark)
                            if message.author.id in ops:
                                help = discord.Embed(
                                    title="**Help:**",
                                    description="**👋🏽 Support**\n**.format** : Sends format for reporting a issue in a ticket\n**.appeal** : Sends format for appealing a ban\n**.report** : Sends format for reporting a player\n**.logs** : Sends guide on how to send logs\n**.ticket** : Sends format for creating a ticket\n**.links**     : Sends a list of PixelHeim related links\n**/apply**     : Application for PixelHeim Staff\n\n**🏢 Minecraft**\n**.ip**     : Sends server's IP adress\n**.status**     : Shows the server's current status\n**.bans <username>**      - Checks if a player is banned\n**.vote**      - Sends the links to the server's voting websites\n**/list**      - Sends a list of players online\n\n**✨ PixelHeim**\n**.ping**     : Checks Pixiebot's response times\n**.info**     : Shows information about Pixiebot\n**.serverinfo**     : Gives an overview of PixelHeim's Discord Server\n**.suggest**     : Write a suggestion related to PixelHeim\n**.calc**     : Use a calculator\n**.meme**     : Get top memes from r/memes\n**/avatar**     : Get a users avatar\n**/whois**     : Get information about a user\n**/poll**     : Create a Poll\n**/clear**     : Clear messages\n**.snipe**     : Shows last deleted message\n**.editsnipe**     : Shows last edited message\n**.sysinfo**     : Shows System Information",
                                    colour=discord.Colour.from_rgb(255, 0, 0),
                                )
                            else:
                                help = discord.Embed(
                                    title="**Help:**",
                                    description="**👋🏽 Support**\n**.format** : Sends format for reporting a issue in a ticket\n**.appeal** : Sends format for appealing a ban\n**.report** : Sends format for reporting a player\n**.logs** : Sends guide on how to send logs\n**.ticket** : Sends format for creating a ticket\n**.links**     : Sends a list of PixelHeim related links\n**/apply**     : Application for PixelHeim Staff\n\n**🏢 Minecraft**\n**.ip**     : Sends server's IP adress\n**.status**     : Shows the server's current status\n**.bans <username>**      - Checks if a player is banned\n**.vote**      - Sends the links to the server's voting websites\n**/list**      - Sends a list of players online\n\n**✨ PixelHeim**\n**.ping**     : Checks Pixiebot's response times\n**.info**     : Shows information about Pixiebot\n**.serverinfo**     : Gives an overview of PixelHeim's Discord Server\n**.suggest**     : Write a suggestion related to PixelHeim\n**.calc**     : Use a calculator\n**.meme**     : Get top memes from r/memes\n**/avatar**     : Get a users avatar\n**/whois**     : Get information about a user\n**/poll**     : Create a Poll",
                                    colour=discord.Colour.from_rgb(255, 0, 0),
                                )
                            await message.channel.send(embed=help)

                        if ".logs" in message.content.lower():
                            await log(f"{message.author} used .logs")
                            await message.add_reaction(checkmark)
                            logs = discord.Embed(
                                title="**How to send your Logs:-**",
                                description="Step 1- Press 'Windows Key' and 'r' simultaneously.\nStep 2- Type this in the run window \"%appdata%\"\nStep 3- Go to the .minecraft folder\nStep 4- Go to the logs folder\nStep 5- Send all the logs with today's date to the ticket",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            await message.channel.send(embed=logs)

                        if ".links" in message.content.lower():
                            await log(f"{message.author} used .links")
                            await message.add_reaction(checkmark)
                            links = discord.Embed(
                                title="**Links:**",
                                description="•[Official Website](https://pixel-heim.com)\n•[Store](https://store.pixel-heim.com)\n•[YouTube Channel](https://www.youtube.com/channel/UChVgbFKjriq820ydBDmdnaQ)\n•[FaceBook Page](https://www.facebook.com/pixelheim2021)\n•[Reddit](https://www.reddit.com/r/pixelheim/)\n•[Instagram](https://www.instagram.com/pixelheim_/)",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            links.set_thumbnail(url="https://i.imgur.com/PSfetR6.png")
                            await message.channel.send(embed=links)

                        if ".vote" in message.content.lower():
                            await log(f"{message.author} used .vote")
                            await message.add_reaction(checkmark)
                            vote = discord.Embed(
                                description="•[Minecraft-Server.net](https://minecraft-server.net/vote/Pixel-Heim/)\n•[Minecraft Mp](https://minecraft-mp.com/server/285568/vote/)\n•[TopG](https://topg.org/minecraft-servers/server-628713)\n•[Top Minecraft Servers](https://topminecraftservers.org/vote/17681)\n•[MinecraftServers.org](https://minecraftservers.org/vote/614264)\n•[Planet Minecraft ](https://www.planetminecraft.com/server/pixel-heim/vote/)\n•[Minecraft Survival Servers](https://minecraftsurvivalservers.com/vote/105)",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            vote.set_author(
                                name="Voting Links:",
                                icon_url="https://i.imgur.com/PSfetR6.png",
                            )
                            await message.channel.send(embed=vote)

                        if ".info" in message.content.lower():
                            await log(f"{message.author} used .info")
                            await message.add_reaction(checkmark)
                            guild = await client.fetch_guild(834516102184828970)
                            creator = await client.fetch_user(551398454962946049)
                            info = discord.Embed(
                                description="I am a custom bot made for **PixelHeim** that has lots of useful features!\nUse ``.help`` to see all the Commands",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            info.add_field(name="Version:", value="v2.4.3")
                            info.add_field(name="Language:", value=" Python")
                            info.add_field(
                                name="Latency:",
                                value=" {0} ms".format(round(client.latency * 1000, 2)),
                            )
                            info.set_author(
                                name="PixelHeim",
                                icon_url="https://i.imgur.com/6op0EWv.gif",
                            )
                            info.set_image(url="https://i.imgur.com/fdGMZdu.png")
                            info.set_footer(
                                text=f"Creator: {creator.name}#{creator.discriminator} | Shard {guild.shard_id} | Uptime {str(datetime.timedelta(seconds=int(round(time.time() - startTime))))}",
                                icon_url="https://cdn.discordapp.com/avatars/551398454962946049/a_80f779b8a6faa8320e1315edc121aa2e.gif?size=1024",
                            )
                            await message.channel.send(embed=info)

                        if ".ping" in message.content.lower():
                            await log(f"{message.author} used .ping")
                            loading = await message.channel.send(
                                "<a:loading:859434860337954866> Checking the Latency"
                            )
                            try:
                                singapore = mysql.connector.connect(
                                    host=os.getenv("HOST"),
                                    database=os.getenv("DATABASE"),
                                    user=os.getenv("USER"),
                                    password=os.getenv("PASSWORD"),
                                )
                                cursor = singapore.cursor(buffered=True)
                                start = time.time()
                                cursor.execute("/* ping */ SELECT 1")
                                end = time.time()
                                db_latency = "{0} ms".format(
                                    round(((end - start) * 1000), 3)
                                )
                                cursor.close()
                            except:
                                await log(
                                    "A Database error has occurred while trying to connect"
                                )
                                db_latency = "Offline"
                            try:
                                server.status()
                                mc_status = "Online"
                            except:
                                mc_status = "Offline"
                                await log("Could not connect to PixelHeim Server")
                            ping = discord.Embed(
                                title="**Response Times:**",
                                description=":timer: Discord-  {0} ms\n\n:desktop: Database-  {1}\n\n:office: Minecraft-  {2}".format(
                                    round(client.latency * 1000, 3),
                                    db_latency,
                                    mc_status,
                                ),
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            await loading.delete()
                            await message.channel.send(embed=ping)

                        if ".serverinfo" in message.content.lower():
                            await log(f"{message.author} used .serverinfo")
                            await message.add_reaction(checkmark)
                            guild = client.get_guild(834516102184828970)
                            region = str(guild.region)
                            serverinfo = discord.Embed(
                                title="Server Info",
                                description="This is PixelHeim's Official Discord server!! Tune in to announcements or chat with players in <#834517964308873242>.",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            serverinfo.set_author(
                                name=guild.name,
                                icon_url=guild.icon_url,
                                url="https://pixel-heim.com",
                            )
                            serverinfo.add_field(
                                name="Owner:", value="<@{0}>".format(guild.owner_id)
                            )
                            serverinfo.add_field(
                                name="Server Members:",
                                value="{0}/{1}".format(
                                    guild.member_count, guild.max_members
                                ),
                            )
                            serverinfo.add_field(
                                name="Server Boost:",
                                value="Level {0}".format(guild.premium_tier),
                            )
                            serverinfo.add_field(
                                name="Roles:", value=f"{len(guild.roles)}"
                            )
                            serverinfo.add_field(
                                name="Channels:", value=f"{len(guild.text_channels)}"
                            )
                            serverinfo.add_field(
                                name="Voice Channels:",
                                value=f"{len(guild.voice_channels)}",
                            )
                            serverinfo.add_field(
                                name="Emojis:",
                                value="{0}/{1}".format(
                                    len(guild.emojis), guild.emoji_limit
                                ),
                            )
                            serverinfo.add_field(
                                name="Region:", value=region.capitalize()
                            )
                            serverinfo.add_field(
                                name="Primary Language:", value=guild.preferred_locale
                            )
                            serverinfo.set_footer(
                                text="Server ID: {1}  •  Created On: {0}".format(
                                    guild.created_at.strftime("%d %B, %Y"), guild.id
                                )
                            )
                            await message.channel.send(embed=serverinfo)

                        if "patato" in message.content.lower():
                            random_temp = random.randint(1, 3)
                            if random_temp == 1:
                                await message.channel.send(
                                    "Thou hast summoned da **Patato Club**"
                                )

                        if message.content.lower() in gei:
                            await message.add_reaction(cross)
                            await message.channel.send("***No U***")

                        if "never gonna give you up" in message.content.lower():
                            await message.channel.send("Never gonna let you down")
                            await message.channel.send(
                                "https://tenor.com/view/dance-moves-dancing-singer-groovy-gif-17029825"
                            )

                        if "kawaii" in message.content.lower():
                            random_temp = random.randint(1, 9)
                            if random_temp == 1:
                                await message.channel.send("Did someone say Kawaii?")
                                await message.channel.send(
                                    "https://tenor.com/view/puppy-pomeranian-cute-small-gif-21361421"
                                )
                            elif random_temp == 2:
                                await message.channel.send("Kawaii!!")
                                await message.channel.send(
                                    "https://tenor.com/view/cute-cat-oh-yeah-awesome-cats-amazing-gif-15805236"
                                )
                            elif random_temp == 3:
                                await message.channel.send("UwU")
                                await message.channel.send(
                                    "https://tenor.com/view/cute-bird-oiseau-parrot-perroquet-gif-13534341"
                                )
                            elif random_temp == 4:
                                await message.channel.send(":D")
                                await message.channel.send(
                                    "https://tenor.com/view/baby-boy-cute-chubby-cheeks-speak-gif-4956341"
                                )
                            elif random_temp == 5:
                                await message.channel.send(
                                    "https://tenor.com/view/ratatouille-cute-rat-eating-spaghetti-gif-15430973"
                                )

        @client.listen("on_message_delete")
        async def snipe_logs(message):
            if not message.author.bot:
                snipe_message_author[message.channel.id] = message.author
                snipe_message_content[message.channel.id] = message.content
                snipe_message_time[message.channel.id] = datetime.datetime.utcnow()

        @client.listen("on_message_edit")
        async def esnipe_logs(before, after):
            if not before.author.bot:
                esnipe_message_author[before.channel.id] = before.author
                before_esnipe_message_content[before.channel.id] = before.content
                after_esnipe_message_content[before.channel.id] = after.content
                esnipe_message_time[before.channel.id] = datetime.datetime.utcnow()

        # Error Handler
        @client.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                return
            elif isinstance(error, commands.CommandOnCooldown):
                if str(ctx.channel.type) == "private":
                    return ()
                if error.retry_after > 60:
                    m = await ctx.send(
                        f"Try again in **{round(error.retry_after / 60)}min**"
                    )
                elif round(error.retry_after) <= 0:
                    m = await ctx.send(f"Try again! (Slow down)**")
                elif error.retry_after <= 60:
                    m = await ctx.send(
                        f"Try again in **{round(error.retry_after)}sec**"
                    )
                await asyncio.sleep(10)
                await m.delete()
            elif isinstance(error, commands.MissingPermissions):
                m = await ctx.send(
                    f"<a:cross:848897550610333737>You don't have permission to do that!"
                )
                await asyncio.sleep(5)
                await m.delete()
            elif isinstance(error, commands.BadArgument):
                m = await ctx.send(
                    f"<a:cross:848897550610333737>That is not a valid input!"
                )
                await asyncio.sleep(5)
                await m.delete()
            else:
                await log("An Error has occurred : " + str(error))

        # Commands.Discord
        @client.command(name="bans")
        @commands.cooldown(1, 15, commands.BucketType.user)
        async def bans(ctx, name: str = None):
            if str(ctx.channel.type) == "private":
                return ()
            elif name is None:
                m = await ctx.send(
                    embed=discord.Embed(
                        description='Please specify the name of the person to search! `e.g. ".bans Spiraxx"`',
                        colour=discord.Colour.from_rgb(255, 0, 0),
                    )
                )
                await asyncio.sleep(10)
                await m.delete()
                return ()
            else:
                if name.lower() == "sherr06":
                    await ctx.send("**Owner can't be banned in his own server**")
                else:
                    start = time.time()
                    loading = await ctx.send(
                        f"<a:loading:859434860337954866> Gathering information on {name}"
                    )
                    try:
                        litebans = mysql.connector.connect(
                            host=os.getenv("HOST"),
                            database=os.getenv("DATABASE"),
                            user=os.getenv("USER"),
                            password=os.getenv("PASSWORD"),
                        )
                        cursor = litebans.cursor()
                        await log(
                            f"You're connected to database: ('Litebans') to gather info on {name} for {ctx.author}"
                        )

                        history = (
                            "SELECT * FROM litebans_history where name = '{0}'".format(
                                name
                            )
                        )
                        cursor.execute(history)
                        user_history = cursor.fetchall()
                        uuid = ""
                        for row in user_history:
                            uuid = row[3]
                            name = row[2]
                        if uuid == "":
                            final_embed = discord.Embed(
                                title=f"{name} has never joined the server.",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                        else:
                            bans = (
                                "SELECT * FROM litebans_bans where uuid = '{0}'".format(
                                    uuid
                                )
                            )
                            cursor.execute(bans)
                            user_bans = cursor.fetchall()
                            if not user_bans:
                                final_embed = discord.Embed(
                                    title=f"{name} has never been banned in PixelHeim.",
                                    colour=discord.Colour.from_rgb(255, 0, 0),
                                )
                            else:
                                for row in user_bans:
                                    reason = row[3]
                                    executor = row[5]
                                    banned_on = row[9]
                                    banned_until = row[10]
                                    server = row[12]
                                    active = row[16]
                                if active == 1:
                                    if banned_until == -1:
                                        banned_until = "Permanent Ban"
                                    else:
                                        banned_until = (
                                            f"<t:{round(banned_until / 1000)}:d>"
                                        )
                                    final_embed = discord.Embed(
                                        title="Ban Details",
                                        colour=discord.Colour.from_rgb(255, 0, 0),
                                    )
                                    final_embed.add_field(name="Username:", value=name)
                                    final_embed.add_field(name="\u200b", value="\u200b")
                                    final_embed.add_field(
                                        name="Banned By:", value=executor
                                    )
                                    final_embed.add_field(
                                        name="Banned On:",
                                        value=f"<t:{round(banned_on / 1000)}:d>",
                                    )
                                    final_embed.add_field(name="\u200b", value="\u200b")
                                    final_embed.add_field(
                                        name="Until:", value=banned_until
                                    )
                                    final_embed.add_field(name="Reason:", value=reason)
                                    if server is not None:
                                        final_embed.set_footer(
                                            text=f"Ban Origin: {server.capitalize()}"
                                        )
                                else:
                                    final_embed = discord.Embed(
                                        title=f"**{name} has no active bans in PixelHeim.**",
                                        colour=discord.Colour.from_rgb(255, 0, 0),
                                    )
                    except Error as e:
                        final_embed = discord.Embed(
                            title="A database error occurred while trying to retrieve the data!!",
                            description="Contact an administrator to fix the issue.",
                            colour=discord.Colour.from_rgb(255, 0, 0),
                        )
                        await log("Error while connecting to MySQL" + str(e))
                        name = "Db Error"
                    finally:
                        if name != "Db Error":
                            if litebans.is_connected():
                                litebans.close()
                                cursor.close()
                                await log("MySQL connection terminated")

                    end = time.time()
                    await asyncio.sleep(3.75 - (end - start))
                    await loading.delete()
                    await ctx.send(embed=final_embed)

        @client.command(name="suggest", aliases=["suggestion"])
        @commands.cooldown(1, 60, commands.BucketType.user)
        async def suggest(ctx, *, suggestion: str = None):
            if str(ctx.channel.type) == "private":
                return ()
            elif suggestion is None:
                await ctx.message.delete()
                msg = await ctx.send(
                    embed=discord.Embed(
                        description=f"{ctx.author.mention} your suggestion cannot be empty!",
                        colour=discord.Colour.from_rgb(255, 0, 0),
                    )
                )
                await asyncio.sleep(10)
                await msg.delete()
                return ()
            else:
                await log(f"{ctx.author} added a suggestion")
                await ctx.message.delete()
                suggestionchannel = await client.fetch_channel(834690230375940106)
                suggestionembed = discord.Embed(
                    title="Suggestion:",
                    description=suggestion,
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
                suggestionembed.set_author(
                    name=ctx.author, icon_url=ctx.author.avatar_url
                )
                message = await suggestionchannel.send(embed=suggestionembed)
                await message.add_reaction(checkmark)
                await message.add_reaction(cross)
                msg = await ctx.send(
                    f"{ctx.author.mention} your Suggestion has been added to <#834690230375940106>"
                )
                await asyncio.sleep(5)
                await msg.delete()

        @client.command(name="clear")
        @commands.has_permissions(manage_messages=True)
        async def clear(ctx, amount=0):
            if not amount == 0:
                await log(
                    f"{ctx.author} deleted {amount} messages in {ctx.channel.name}"
                )
                await ctx.message.delete()
                await ctx.channel.purge(limit=amount)
                m = await ctx.send(
                    embed=discord.Embed(
                        description=f"Deleted `{amount} messages` from <#{ctx.channel.id}>",
                        colour=discord.Colour.from_rgb(255, 0, 0),
                    )
                )
                await asyncio.sleep(5)
                await m.delete()
            else:
                m = await ctx.send(
                    embed=discord.Embed(
                        description=f'Please specify the number of messages to be deleted! `e.g. ".clear 5"`',
                        colour=discord.Colour.from_rgb(255, 0, 0),
                    )
                )
                await asyncio.sleep(10)
                await m.delete()

        @client.command(name="snipe")
        async def snipe(ctx):
            if ctx.author.id in ops:
                await log(f"{ctx.author} used .snipe")
                if ctx.channel.id in snipe_message_content:
                    embed = discord.Embed(
                        description=snipe_message_content[ctx.channel.id],
                        colour=discord.Colour.from_rgb(255, 0, 0),
                        timestamp=snipe_message_time[ctx.channel.id],
                    )
                    embed.set_author(
                        name=f"{snipe_message_author[ctx.channel.id].name}#{snipe_message_author[ctx.channel.id].discriminator}",
                        icon_url=snipe_message_author[ctx.channel.id].avatar_url,
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"There is nothing to snipe.")
            else:
                m = await ctx.send(
                    f"<a:cross:848897550610333737>You don't have permission to do that!"
                )
                await asyncio.sleep(5)
                await m.delete()

        @client.command(name="editsnipe", aliases=["esnipe"])
        async def editsnipe(ctx):
            if ctx.author.id in ops:
                await log(f"{ctx.author} used .esnipe")
                if ctx.channel.id in before_esnipe_message_content:
                    embed = discord.Embed(
                        description=f"**Before:** {before_esnipe_message_content[ctx.channel.id]}\n**After:** {after_esnipe_message_content[ctx.channel.id]}",
                        colour=discord.Colour.from_rgb(255, 0, 0),
                        timestamp=esnipe_message_time[ctx.channel.id],
                    )
                    embed.set_author(
                        name=f"{esnipe_message_author[ctx.channel.id].name}#{esnipe_message_author[ctx.channel.id].discriminator}",
                        icon_url=esnipe_message_author[ctx.channel.id].avatar_url,
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"There is nothing to snipe.")
            else:
                m = await ctx.send(
                    f"<a:cross:848897550610333737>You don't have permission to do that!"
                )
                await asyncio.sleep(5)
                await m.delete()

        @client.command(name="meme")
        @commands.cooldown(1, 1, commands.BucketType.user)
        async def meme(ctx):
            if not len(all_posts) == 0:
                random_post = random.choice(all_posts)
                while not find(random_post.url):
                    all_posts.remove(random_post)
                    random_post = random.choice(all_posts)
                all_posts.remove(random_post)
                meme_embed = discord.Embed(
                    title=random_post.title,
                    url="https://www.reddit.com" + random_post.permalink,
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
                meme_embed.set_image(url=random_post.url)
                meme_embed.set_footer(
                    text=f"👍 {random_post.score} | 💬 {random_post.num_comments}"
                )
                await ctx.send(embed=meme_embed)
            else:
                await reddit_update()

        @client.command(name="sysinfo")
        async def sysinfo(ctx):
            if ctx.author.id in ops:
                await log(f"{ctx.author} used .sysinfo")
                system_info = discord.Embed(
                    title="System Information",
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
                system_info.add_field(
                    name="OS:", value=f"```{platform.system()} {platform.release()}```"
                )
                system_info.add_field(
                    name="Arch:", value=f"```{platform.architecture()[0]}```"
                )
                system_info.add_field(
                    name="Sys Uptime:",
                    value=f"```{str(datetime.timedelta(seconds=int(round(time.time() - psutil.boot_time()))))}```",
                )
                system_info.add_field(
                    name="Processor:",
                    value=f"```{cpuinfo.get_cpu_info()['brand_raw']}```",
                    inline=False,
                )
                system_info.add_field(
                    name="Physical Cores:",
                    value=f"```{psutil.cpu_count(logical=False)}```",
                )
                system_info.add_field(
                    name="CPU Usage:",
                    value=f"```{psutil.cpu_percent(interval=None)}%```",
                )
                system_info.add_field(
                    name="Clock Speed:",
                    value=f"```{round(psutil.cpu_freq().current / 1000, 2)} GHz```",
                )
                system_info.add_field(
                    name="Memory:",
                    value=f"```{round(psutil.virtual_memory()[3] / 1000000000, 2)} / {round(psutil.virtual_memory()[0] / 1000000000, 2)} GB```",
                )
                system_info.add_field(
                    name="Python:", value=f"```v{platform.python_version()}```"
                )
                await ctx.send(embed=system_info)
            else:
                m = await ctx.send(
                    f"<a:cross:848897550610333737>You don't have permission to do that!"
                )
                await asyncio.sleep(5)
                await m.delete()

        @client.command(name="restart")
        @commands.is_owner()
        async def restart(ctx):
            await log(f"{ctx.author} used .restart")
            await ctx.send("See you soon!")
            await client.change_presence(activity=None, status=discord.Status.offline)
            await client.close()
            raise SystemExit("SIGKILL")

        @client.command(name="calc")
        @commands.cooldown(1, 1, commands.BucketType.user)
        async def calc(ctx):
            await log(f"{ctx.author} used .calc")
            await ctx.message.delete()
            keys = [
                [
                    Button(style=ButtonStyle.blue, label="("),
                    Button(style=ButtonStyle.blue, label=")"),
                    Button(style=ButtonStyle.blue, label="⌫"),
                    Button(style=ButtonStyle.red, label="AC"),
                ],
                [
                    Button(style=ButtonStyle.grey, label="7"),
                    Button(style=ButtonStyle.grey, label="8"),
                    Button(style=ButtonStyle.grey, label="9"),
                    Button(style=ButtonStyle.blue, label="÷"),
                ],
                [
                    Button(style=ButtonStyle.grey, label="4"),
                    Button(style=ButtonStyle.grey, label="5"),
                    Button(style=ButtonStyle.grey, label="6"),
                    Button(style=ButtonStyle.blue, label="×"),
                ],
                [
                    Button(style=ButtonStyle.grey, label="1"),
                    Button(style=ButtonStyle.grey, label="2"),
                    Button(style=ButtonStyle.grey, label="3"),
                    Button(style=ButtonStyle.blue, label="-"),
                ],
                [
                    Button(style=ButtonStyle.grey, label="0"),
                    Button(style=ButtonStyle.grey, label="."),
                    Button(style=ButtonStyle.green, label="="),
                    Button(style=ButtonStyle.blue, label="+"),
                ],
            ]
            keys_disabled = [
                [
                    Button(style=ButtonStyle.blue, label="(", disabled=True),
                    Button(style=ButtonStyle.blue, label=")", disabled=True),
                    Button(style=ButtonStyle.blue, label="⌫", disabled=True),
                    Button(style=ButtonStyle.red, label="AC", disabled=True),
                ],
                [
                    Button(style=ButtonStyle.grey, label="7", disabled=True),
                    Button(style=ButtonStyle.grey, label="8", disabled=True),
                    Button(style=ButtonStyle.grey, label="9", disabled=True),
                    Button(style=ButtonStyle.blue, label="÷", disabled=True),
                ],
                [
                    Button(style=ButtonStyle.grey, label="4", disabled=True),
                    Button(style=ButtonStyle.grey, label="5", disabled=True),
                    Button(style=ButtonStyle.grey, label="6", disabled=True),
                    Button(style=ButtonStyle.blue, label="×", disabled=True),
                ],
                [
                    Button(style=ButtonStyle.grey, label="1", disabled=True),
                    Button(style=ButtonStyle.grey, label="2", disabled=True),
                    Button(style=ButtonStyle.grey, label="3", disabled=True),
                    Button(style=ButtonStyle.blue, label="-", disabled=True),
                ],
                [
                    Button(style=ButtonStyle.grey, label="0", disabled=True),
                    Button(style=ButtonStyle.grey, label=".", disabled=True),
                    Button(style=ButtonStyle.green, label="=", disabled=True),
                    Button(style=ButtonStyle.blue, label="+", disabled=True),
                ],
            ]
            calc_embed = discord.Embed(
                description="```                              0```",
                colour=discord.Colour.from_rgb(255, 0, 0),
            )
            calc_embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            calc_msg = await ctx.send(embed=calc_embed, components=keys)

            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author

            final_equation = ""
            previous_input = ""
            equation_valid = True
            format_error = False
            while True:
                try:
                    res = await client.wait_for("button_click", check=check, timeout=60)
                except asyncio.TimeoutError:
                    await calc_msg.edit(components=keys_disabled)
                    return
                await res.respond(type=6)

                current_input = res.component.label
                if current_input == "=":
                    if not equation_valid:
                        continue
                    if final_equation == "":
                        final_equation = "0"

                    def is_number(item):
                        try:
                            float(item)
                            return True
                        except ValueError:
                            return False

                    def set_up_list():
                        a_list = []
                        for item in final_equation:
                            a_list.append(item)
                        count = 0
                        while count < len(a_list) - 1:
                            if is_number(a_list[count]) and is_number(
                                a_list[count + 1]
                            ):
                                a_list[count] += a_list[count + 1]
                                del a_list[count + 1]
                            elif is_number(a_list[count]) and a_list[count + 1] == ".":
                                try:
                                    x = a_list[count + 2]
                                except IndexError:
                                    format_error = True
                                if is_number(a_list[count + 2]):
                                    a_list[count] += (
                                        a_list[count + 1] + a_list[count + 2]
                                    )
                                    del a_list[count + 2]
                                    del a_list[count + 1]
                            else:
                                count += 1
                        return a_list

                    def perform_operation(n1, operand, n2):
                        if operand == "+":
                            return str(float(n1) + float(n2))
                        elif operand == "-":
                            return str(float(n1) - float(n2))
                        elif operand == "×":
                            return str(float(n1) * float(n2))
                        elif operand == "÷":
                            try:
                                n = str(float(n1) / float(n2))
                                return n
                            except ZeroDivisionError:
                                log(f"Zero Division Error!")

                    expression = set_up_list()
                    emergency_count = 0
                    P = ["(", ")"]
                    while len(expression) != 1:
                        count = 0
                        while count < len(expression) - 1:
                            if expression[count] == "(":
                                if expression[count + 2] == ")":
                                    del expression[count + 2]
                                    del expression[count]
                            count += 1
                        count = 0
                        while count < len(expression) - 1:
                            if expression[count] in ["×", "÷"] and not (
                                expression[count + 1] in P or expression[count - 1] in P
                            ):
                                expression[count - 1] = perform_operation(
                                    expression[count - 1],
                                    expression[count],
                                    expression[count + 1],
                                )
                                del expression[count + 1]
                                del expression[count]
                            count += 1
                        count = 0
                        while count < len(expression) - 1:
                            if expression[count] in ["+", "-"] and not (
                                expression[count + 1] in P or expression[count - 1] in P
                            ):
                                expression[count - 1] = perform_operation(
                                    expression[count - 1],
                                    expression[count],
                                    expression[count + 1],
                                )
                                del expression[count + 1]
                                del expression[count]
                            count += 1
                        emergency_count += 1
                        if emergency_count >= 1000:
                            calc_embed = discord.Embed(
                                description="```         Operation was bugged!!```",
                                colour=discord.Colour.from_rgb(255, 0, 0),
                            )
                            calc_embed.set_author(
                                name=ctx.author, icon_url=ctx.author.avatar_url
                            )
                            await calc_msg.edit(
                                embed=calc_embed, components=keys_disabled
                            )
                            return
                    if expression[0] is None:
                        calc_embed = discord.Embed(
                            description="```   You tried to divide by zero!!```",
                            colour=discord.Colour.from_rgb(255, 0, 0),
                        )
                        calc_embed.set_author(
                            name=ctx.author, icon_url=ctx.author.avatar_url
                        )
                        await calc_msg.edit(embed=calc_embed, components=keys_disabled)
                        return
                    elif format_error:
                        calc_embed = discord.Embed(
                            description="```      Error in your formatting!!```",
                            colour=discord.Colour.from_rgb(255, 0, 0),
                        )
                        calc_embed.set_author(
                            name=ctx.author, icon_url=ctx.author.avatar_url
                        )
                        await calc_msg.edit(embed=calc_embed, components=keys_disabled)
                        return
                    if float(expression[0]).is_integer():
                        final_equation = str(round(float(expression[0])))
                    else:
                        final_equation = str(float(expression[0]))
                elif current_input == "AC":
                    final_equation = ""
                    calc_embed = discord.Embed(
                        description="```                              0```",
                        colour=discord.Colour.from_rgb(255, 0, 0),
                    )
                    calc_embed.set_author(
                        name=ctx.author, icon_url=ctx.author.avatar_url
                    )
                    await calc_msg.edit(embed=calc_embed, components=keys)
                    continue
                elif current_input == "⌫":
                    if final_equation == "":
                        continue
                    final_equation = final_equation[0 : len(final_equation) - 1]
                elif (
                    (
                        previous_input in ["×", "÷", "+", "-", ""]
                        and current_input == "."
                    )
                    or (previous_input == "." and current_input in ["×", "÷", "+", "-"])
                    or (previous_input == "" and current_input in ["×", "÷", "+", "-"])
                    or (previous_input in ["×", "÷", "+", "-"] and current_input == ".")
                ):
                    final_equation = final_equation + "0" + current_input
                elif previous_input == ")" and current_input == ".":
                    final_equation = final_equation + "×0" + current_input
                elif (
                    previous_input in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
                    and current_input == "("
                ) or (
                    previous_input == ")"
                    and current_input
                    in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
                ):
                    final_equation = final_equation + "×" + current_input
                elif (
                    previous_input in ["×", "÷", "+", "-"] and current_input == ")"
                ) or (
                    previous_input == "("
                    and current_input in [")", "×", "÷", "+", "-", "%"]
                ):
                    continue
                elif previous_input in ["×", "÷", "+", "-"] and current_input in [
                    "×",
                    "÷",
                    "+",
                    "-",
                ]:
                    final_equation = final_equation[0 : len(final_equation) - 1]
                    final_equation = final_equation + current_input
                else:
                    final_equation = final_equation + current_input

                if len(final_equation) > 31:
                    calc_embed = discord.Embed(
                        description="```       Operation was too long!!```",
                        colour=discord.Colour.from_rgb(255, 0, 0),
                    )
                    calc_embed.set_author(
                        name=ctx.author, icon_url=ctx.author.avatar_url
                    )
                    await calc_msg.edit(embed=calc_embed, components=keys_disabled)
                    return
                len_whitespace = 31 - len(final_equation)
                whitespace = ""
                while len_whitespace != 0:
                    whitespace = " " + whitespace
                    len_whitespace = len_whitespace - 1
                calc_embed = discord.Embed(
                    description=f"```{whitespace}{final_equation}```",
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
                calc_embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
                await calc_msg.edit(embed=calc_embed, components=keys)
                if current_input in [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "0",
                    "×",
                    "÷",
                    "+",
                    "-",
                ]:
                    previous_input = current_input

        # Cooldown Bypass for Ops
        @suggest.after_invoke
        async def reset_cooldown(ctx):
            if ctx.author.id in ops:
                suggest.reset_cooldown(ctx)

        @bans.after_invoke
        async def reset_cooldown(ctx):
            if ctx.author.id in ops:
                bans.reset_cooldown(ctx)

        # Slash Commands
        @slash.slash(
            name="ping",
            description="Checks PixelHeim's response to discord",
            guild_ids=guild_ids,
        )
        async def ping(ctx):
            await ctx.defer()
            await log(f"{ctx.author} used /ping")
            try:
                singapore = mysql.connector.connect(
                    host=os.getenv("HOST"),
                    database=os.getenv("DATABASE"),
                    user=os.getenv("USER"),
                    password=os.getenv("PASSWORD"),
                )
                cursor = singapore.cursor(buffered=True)
                start = time.time()
                cursor.execute("/* ping */ SELECT 1")
                end = time.time()
                db_latency = "{0} ms".format(round(((end - start) * 1000), 3))
                cursor.close()
            except:
                db_latency = "Offline"
                await log("A Database error has occurred while trying to connect")
            try:
                server.status()
                mc_status = "Online"
            except:
                mc_status = "Offline"
                await log("Could not connect to PixelHeim Server")
            ping = discord.Embed(
                title="**Response Times:**",
                description=":timer: Discord-  {0} ms\n\n:desktop: Database-  {1}\n\n:office: Minecraft-  {2}".format(
                    round(client.latency * 1000, 3), db_latency, mc_status
                ),
                colour=discord.Colour.from_rgb(255, 0, 0),
            )
            await ctx.send(embed=ping)

        @slash.slash(
            name="help",
            description="Shows you a list of Commands.",
            guild_ids=guild_ids,
        )
        async def help(ctx):
            await log(f"{ctx.author} used /help")
            if ctx.author.id in ops:
                help = discord.Embed(
                    title="**Help:**",
                    description="**👋🏽 Support**\n**.format** : Sends format for reporting a issue in a ticket\n**.appeal** : Sends format for appealing a ban\n**.report** : Sends format for reporting a player\n**.logs** : Sends guide on how to send logs\n**.ticket** : Sends format for creating a ticket\n**.links**     : Sends a list of PixelHeim related links\n**/apply**     : Application for PixelHeim Staff\n\n**🏢 Minecraft**\n**.ip**     : Sends server's IP adress\n**.status**     : Shows the server's current status\n**.bans <username>**      - Checks if a player is banned\n**.vote**      - Sends the links to the server's voting websites\n**/list**      - Sends a list of players online\n\n**✨ PixelHeim**\n**.ping**     : Checks Pixiebot's response times\n**.info**     : Shows information about Pixiebot\n**.serverinfo**     : Gives an overview of PixelHeim's Discord Server\n**.suggest**     : Write a suggestion related to PixelHeim\n**.calc**     : Use a calculator\n**.meme**     : Get top memes from r/memes\n**/avatar**     : Get a users avatar\n**/whois**     : Get information about a user\n**/poll**     : Create a Poll\n**/clear**     : Clear messages\n**.snipe**     : Shows last deleted message\n**.editsnipe**     : Shows last edited message\n**.sysinfo**     : Shows System Information",
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
            else:
                help = discord.Embed(
                    title="**Help:**",
                    description="**👋🏽 Support**\n**.format** : Sends format for reporting a issue in a ticket\n**.appeal** : Sends format for appealing a ban\n**.report** : Sends format for reporting a player\n**.logs** : Sends guide on how to send logs\n**.ticket** : Sends format for creating a ticket\n**.links**     : Sends a list of PixelHeim related links\n**/apply**     : Application for PixelHeim Staff\n\n**🏢 Minecraft**\n**.ip**     : Sends server's IP adress\n**.status**     : Shows the server's current status\n**.bans <username>**      - Checks if a player is banned\n**.vote**      - Sends the links to the server's voting websites\n**/list**      - Sends a list of players online\n\n**✨ PixelHeim**\n**.ping**     : Checks Pixiebot's response times\n**.info**     : Shows information about Pixiebot\n**.serverinfo**     : Gives an overview of PixelHeim's Discord Server\n**.suggest**     : Write a suggestion related to PixelHeim\n**.calc**     : Use a calculator\n**.meme**     : Get top memes from r/memes\n**/avatar**     : Get a users avatar\n**/whois**     : Get information about a user\n**/poll**     : Create a Poll",
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
            await ctx.send(embed=help)

        @slash.slash(
            name="info",
            description="Shows information about Pixiebot.",
            guild_ids=guild_ids,
        )
        async def info(ctx):
            await log(f"{ctx.author} used /info")
            guild = await client.fetch_guild(834516102184828970)
            creator = await client.fetch_user(551398454962946049)
            info = discord.Embed(
                description="I am a custom bot made for **PixelHeim** that has lots of useful features!\nUse ``.help`` to see all the Commands",
                colour=discord.Colour.from_rgb(255, 0, 0),
            )
            info.add_field(name="Version:", value="v2.4.3")
            info.add_field(name="Language:", value=" Python")
            info.add_field(
                name="Latency:", value=" {0} ms".format(round(client.latency * 1000, 2))
            )
            info.set_author(
                name="PixelHeim", icon_url="https://i.imgur.com/6op0EWv.gif"
            )
            info.set_image(url="https://i.imgur.com/fdGMZdu.png")
            info.set_footer(
                text=f"Creator: {creator.name}#{creator.discriminator} | Shard {guild.shard_id} | Uptime {str(datetime.timedelta(seconds=int(round(time.time() - startTime))))}",
                icon_url="https://cdn.discordapp.com/avatars/551398454962946049/a_80f779b8a6faa8320e1315edc121aa2e.gif?size=1024",
            )
            await ctx.send(embed=info)

        @slash.slash(
            name="ip",
            description="Shows you the server's IP adress.",
            guild_ids=guild_ids,
        )
        async def ip(ctx):
            await log(f"{ctx.author} used /ip")
            ip = discord.Embed(
                title="**IP**",
                description=f"**{server_ip}**",
                colour=discord.Colour.from_rgb(255, 0, 0),
            )
            ip.set_thumbnail(url="https://i.imgur.com/PSfetR6.png")
            await ctx.send(embed=ip)

        @slash.slash(
            name="status",
            description="Shows the server's current status",
            guild_ids=guild_ids,
        )
        async def status(ctx):
            await log(f"{ctx.author} used /status")
            await ctx.defer()
            try:
                temp = 1
                status = server.status()
            except:
                serveroffline = discord.Embed(
                    colour=discord.Colour.from_rgb(255, 0, 0),
                    description="Server is currently offline",
                )
                serveroffline.set_author(
                    name="Server Status:", icon_url="https://i.imgur.com/PSfetR6.png"
                )
                await ctx.send(embed=serveroffline)
            if temp == 1:
                serverplayers = discord.Embed(
                    colour=discord.Colour.from_rgb(255, 0, 0),
                    description="There are **{0}** players currently online".format(
                        status.players.online
                    ),
                )
                serverplayers.set_author(
                    name="Server Status:", icon_url="https://i.imgur.com/PSfetR6.png"
                )
                await ctx.send(embed=serverplayers)

        @slash.slash(
            name="vote",
            description="Sends the links to the server's voting websites",
            guild_ids=guild_ids,
        )
        async def vote(ctx):
            await log(f"{ctx.author} used /vote")
            vote = discord.Embed(
                description="•[Minecraft-Server.net](https://minecraft-server.net/vote/Pixel-Heim/)\n•[Minecraft Mp](https://minecraft-mp.com/server/285568/vote/)\n•[TopG](https://topg.org/minecraft-servers/server-628713)\n•[Top Minecraft Servers](https://topminecraftservers.org/vote/17681)\n•[MinecraftServers.org](https://minecraftservers.org/vote/614264)\n•[Planet Minecraft ](https://www.planetminecraft.com/server/pixel-heim/vote/)\n•[Minecraft Survival Servers](https://minecraftsurvivalservers.com/vote/105)",
                colour=discord.Colour.from_rgb(255, 0, 0),
            )
            vote.set_author(
                name="Voting Links:", icon_url="https://i.imgur.com/PSfetR6.png"
            )
            await ctx.send(embed=vote)

        @slash.slash(
            name="serverinfo",
            description="Gives an overview of PixelHeim's Discord Server",
            guild_ids=guild_ids,
        )
        async def serverinfo(ctx):
            await log(f"{ctx.author} used /serverinfo")
            guild = client.get_guild(834516102184828970)
            region = str(guild.region)
            serverinfo = discord.Embed(
                title="Server Info",
                description="This is PixelHeim's Official Discord server!! Tune in to announcements or chat with players in <#834517964308873242>.",
                colour=discord.Colour.from_rgb(255, 0, 0),
            )
            serverinfo.set_author(
                name=guild.name, icon_url=guild.icon_url, url="https://pixel-heim.com"
            )
            serverinfo.add_field(name="Owner:", value="<@{0}>".format(guild.owner_id))
            serverinfo.add_field(
                name="Server Members:",
                value="{0}/{1}".format(guild.member_count, guild.max_members),
            )
            serverinfo.add_field(
                name="Server Boost:", value="Level {0}".format(guild.premium_tier)
            )
            serverinfo.add_field(name="Roles:", value=f"{len(guild.roles)}")
            serverinfo.add_field(name="Channels:", value=f"{len(guild.text_channels)}")
            serverinfo.add_field(
                name="Voice Channels:", value=f"{len(guild.voice_channels)}"
            )
            serverinfo.add_field(
                name="Emojis:",
                value="{0}/{1}".format(len(guild.emojis), guild.emoji_limit),
            )
            serverinfo.add_field(name="Region:", value=region.capitalize())
            serverinfo.add_field(name="Primary Language:", value=guild.preferred_locale)
            serverinfo.set_footer(
                text="Server ID: {1}  •  Created On: {0}".format(
                    guild.created_at.strftime("%d %B, %Y"), guild.id
                )
            )
            await ctx.send(embed=serverinfo)

        @slash.slash(
            name="avatar",
            description="Get a users avatar.",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="user",
                    description="User to fetch the avatar from",
                    option_type=6,
                    required=False,
                )
            ],
        )
        async def avatar(ctx, user: discord.Member = None):
            await log(f"{ctx.author} used /avatar")
            if not user:
                user = ctx.author
            avatar = discord.Embed(
                title="{0}#{1}".format(user.name, user.discriminator), colour=user.color
            )
            avatar.set_image(url=user.avatar_url)
            await ctx.send(embed=avatar)

        @slash.slash(
            name="whois",
            description="Get information about a user.",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="user",
                    description="User to get the info from",
                    option_type=6,
                    required=False,
                )
            ],
        )
        async def whois(ctx, user: discord.Member = None):
            await log(f"{ctx.author} used /whois")
            if not user:
                user = ctx.author
            roles = [role for role in user.roles[1:]]
            whois = discord.Embed(
                description="**{0}**\n----------------------------------------------------------".format(
                    user.mention
                ),
                colour=user.color,
            )
            whois.set_author(
                name="{0}#{1}".format(user.name, user.discriminator),
                icon_url=user.avatar_url,
            )
            whois.set_thumbnail(url=user.avatar_url)
            whois.add_field(
                name="Joined:",
                value=f"<t:{round(time.mktime(user.joined_at.timetuple()))}:D>",
            )
            whois.add_field(
                name="Registered:",
                value=f"<t:{round(time.mktime(user.created_at.timetuple()))}:D>",
            )
            if user.premium_since is None:
                whois.add_field(name="Server Boosting:", value="False")
            else:
                whois.add_field(
                    name="Server Boosting:",
                    value=f"<t:{round(time.mktime(user.premium_since.timetuple()))}:D>",
                )
            whois.add_field(name="Status:", value=str(user.status).capitalize())
            badge = (
                str(user.public_flags.all())
                .replace("[<UserFlags.", "")
                .replace(">]", "")
                .replace("_", " ")
                .replace(":", "")
                .title()
            )
            badge = "".join([i for i in badge if not i.isdigit()])
            if len(badge) == 2:
                whois.add_field(name="Badge:", value="N.A.")
            else:
                whois.add_field(name="Badge:", value=badge)
            whois.add_field(name="\u200b", value="\u200b")
            whois.add_field(
                name="Roles [{0}] :".format(len(roles)),
                value=" ".join([role.mention for role in reversed(roles)]),
            )
            whois.set_footer(
                text="User  ID: {0}  •  Bot: {1}".format(user.id, user.bot)
            )
            await ctx.send(embed=whois)

        @slash.slash(
            name="poll",
            description="Create a Poll.",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="message",
                    description="The question of the poll",
                    option_type=3,
                    required=True,
                ),
                create_option(
                    name="choice1", description="Choice", option_type=3, required=True
                ),
                create_option(
                    name="choice2", description="Choice", option_type=3, required=True
                ),
                create_option(
                    name="choice3", description="Choice", option_type=3, required=False
                ),
                create_option(
                    name="choice4", description="Choice", option_type=3, required=False
                ),
                create_option(
                    name="choice5", description="Choice", option_type=3, required=False
                ),
                create_option(
                    name="choice6", description="Choice", option_type=3, required=False
                ),
                create_option(
                    name="choice7", description="Choice", option_type=3, required=False
                ),
                create_option(
                    name="choice8", description="Choice", option_type=3, required=False
                ),
                create_option(
                    name="choice9", description="Choice", option_type=3, required=False
                ),
            ],
        )
        async def poll(
            ctx,
            message: str,
            choice1: str,
            choice2: str,
            choice3: str = None,
            choice4: str = None,
            choice5: str = None,
            choice6: str = None,
            choice7: str = None,
            choice8: str = None,
            choice9: str = None,
        ):
            await ctx.defer(hidden=True)
            await log(f"{ctx.author} used /poll")
            options = [
                choice1,
                choice2,
                choice3,
                choice4,
                choice5,
                choice6,
                choice7,
                choice8,
                choice9,
            ]
            options = [i for i in options if i]
            des_reactions = [
                "1️⃣",
                "2️⃣",
                "3️⃣",
                "4️⃣",
                "5️⃣",
                "6️⃣",
                "7️⃣",
                "8️⃣",
                "9️⃣",
            ]
            if (
                len(options) == 2
                and options[0].lower() == "yes"
                and options[1].lower() == "no"
            ):
                reactions = [checkmark, cross]
            else:
                reactions = [
                    "1️⃣",
                    "2️⃣",
                    "3️⃣",
                    "4️⃣",
                    "5️⃣",
                    "6️⃣",
                    "7️⃣",
                    "8️⃣",
                    "9️⃣",
                ]
            description = []
            for x, option in enumerate(options):
                description += "\n{} {}\n".format(des_reactions[x], option)
            poll = discord.Embed(
                title=message.capitalize(),
                description="".join(description),
                colour=discord.Colour.from_rgb(255, 0, 0),
            )
            poll.set_footer(
                text="Poll by {0}".format(ctx.author), icon_url=ctx.author.avatar_url
            )
            msg = await ctx.channel.send(embed=poll)
            for reaction in reactions[: len(options)]:
                await msg.add_reaction(reaction)
            await ctx.send(hidden=True, content="Your poll has been created.")

        @slash.slash(
            name="suggest",
            description="Write a suggestion related to PixelHeim",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="suggestion",
                    description="The thing you want to suggest",
                    option_type=3,
                    required=True,
                )
            ],
        )
        async def suggest(ctx, suggestion: str):
            await ctx.defer(hidden=True)
            suggestionchannel = await client.fetch_channel(834690230375940106)
            suggestionembed = discord.Embed(
                title="Suggestion:",
                description=suggestion,
                colour=discord.Colour.from_rgb(255, 0, 0),
            )
            suggestionembed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
            message = await suggestionchannel.send(embed=suggestionembed)
            await message.add_reaction(checkmark)
            await message.add_reaction(cross)
            await log(f"{ctx.author} added a suggestion")
            await ctx.send(
                "Your Suggestion has been added to <#834690230375940106>", hidden=True
            )

        @slash.slash(
            name="list",
            description="Shows a list of players online",
            guild_ids=guild_ids,
        )
        async def player_list(ctx):
            await log(f"{ctx.author} used /list")
            try:
                query = server.query()
                players = query.players.names
                total = len(players)
                formatted = "\n• ".join(players)
                temp = f"• {str(formatted)}"
                if len(players) == 0:
                    temp = "No one is online :("
                list = discord.Embed(
                    title=f"Players Online [{total}] ",
                    description=temp,
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )

            except:
                list = discord.Embed(
                    title="Server is Offline", colour=discord.Colour.from_rgb(255, 0, 0)
                )
            await ctx.send(hidden=True, embed=list)

        @slash.slash(
            name="links",
            description="Send PixelHeim related links",
            guild_ids=guild_ids,
        )
        async def links(ctx):
            await log(f"{ctx.author} used /links")
            links = discord.Embed(
                title="**Links:**",
                description="•[Official Website](https://pixel-heim.com)\n•[Store](https://store.pixel-heim.com)\n•[YouTube Channel](https://www.youtube.com/channel/UChVgbFKjriq820ydBDmdnaQ)\n•[FaceBook Page](https://www.facebook.com/pixelheim2021)\n•[Reddit](https://www.reddit.com/r/pixelheim/)\n•[Instagram](https://www.instagram.com/pixelheim_/)",
                colour=discord.Colour.from_rgb(255, 0, 0),
            )
            links.set_thumbnail(url="https://i.imgur.com/PSfetR6.png")
            await ctx.send(embed=links)

        @slash.slash(
            name="rps",
            description="Rock Paper Scissors against the bot.",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="choice",
                    description="Your choice",
                    option_type=3,
                    required=True,
                )
            ],
        )
        async def rps(ctx, choice: str):
            choice = choice.lower()
            if choice in ["rock", "paper", "scissors"]:
                bot_choice = random.choice(["rock", "paper", "scissors"])
                if choice == bot_choice:
                    text = f"Both played {choice.capitalize()}. It's a tie!"
                elif choice == "rock":
                    if bot_choice == "scissors":
                        text = "Rock smashes scissors! You win!"
                    else:
                        text = "Paper covers rock! You lose."
                elif choice == "paper":
                    if bot_choice == "rock":
                        text = "Paper covers rock! You win!"
                    else:
                        text = "Scissors cuts paper! You lose."
                elif choice == "scissors":
                    if bot_choice == "paper":
                        text = "Scissors cuts paper! You win!"
                    else:
                        text_ = "Rock smashes scissors! You lose."
                result = discord.Embed(
                    title=text, colour=discord.Colour.from_rgb(255, 0, 0)
                )
                result.add_field(name="You choose", value=choice.capitalize())
                result.add_field(name="\u200b", value="\u200b")
                result.add_field(name="I choose", value=bot_choice.capitalize())
                await ctx.send(embed=result)
            else:
                invalid_choice = discord.Embed(
                    title=f'"{choice.capitalize()}" is not a valid choice!',
                    description="**Valid Choices**:\n•Rock\n•Paper\n•Scissors",
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
                await ctx.send(hidden=True, embed=invalid_choice)

        @slash.slash(
            name="randomnumber",
            description="Generates a Random number",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="start",
                    description="Starting number",
                    option_type=4,
                    required=False,
                ),
                create_option(
                    name="upto",
                    description="Ending number",
                    option_type=4,
                    required=False,
                ),
            ],
        )
        async def rng(ctx, start: int = 0, end: int = 999999):
            await ctx.send(
                embed=discord.Embed(
                    title=random.randint(start, end),
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
            )

        @slash.slash(
            name="color",
            description="Visualize any color!",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="color",
                    description="Hex/RGB/Name (Ex: '#FFFFFF' or '255, 255, 255' or 'White')",
                    option_type=3,
                    required=True,
                )
            ],
        )
        async def color(ctx, color: str):
            try:
                rgb = hex2rgb(matplotlib.colors.cnames[color.lower()])
            except:
                try:
                    rgb = hex2rgb(color.lower())
                except:
                    try:
                        rgb = hex2rgb("#" + color.lower())
                    except:
                        try:
                            rgb_string = color.split(",")
                            rgb = list(map(int, rgb_string))
                            if rgb[0] > 255 or rgb[1] > 255 or rgb[2] > 255:
                                await ctx.send(
                                    embed=discord.Embed(
                                        description="❌ RGB Values cannot exceed 255!",
                                        colour=discord.Colour.from_rgb(255, 0, 0),
                                    )
                                )
                                return
                        except:
                            await ctx.send(
                                embed=discord.Embed(
                                    description="❌ Invalid Color!",
                                    colour=discord.Colour.from_rgb(255, 0, 0),
                                )
                            )
                            return

            im = Image.open("assets/logo_white_template.png")
            data = np.array(im)
            red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
            mask = (red == 255) & (green == 255) & (blue == 255)
            data[:, :, :3][mask] = [rgb[0], rgb[1], rgb[2]]
            im = Image.fromarray(data)
            im = im.resize((80, 80))
            im.save("assets/temp/PixelHeim-Color.png")

            color = discord.Embed(
                colour=discord.Colour.from_rgb(rgb[0], rgb[1], rgb[2])
            )
            color.add_field(
                name="Hex", value=rgb2hex(rgb[0], rgb[1], rgb[2]), inline=False
            )
            color.add_field(
                name="RGB", value=f"{rgb[0]}, {rgb[1]}, {rgb[2]} ", inline=False
            )
            color.set_thumbnail(url="attachment://PixelHeim-Color.png")
            await ctx.send(
                file=discord.File(
                    "assets/temp/PixelHeim-Color.png", filename="PixelHeim-Color.png"
                ),
                embed=color,
            )

        @slash.slash(
            name="randomcolor",
            description="Generates a Random Color",
            guild_ids=guild_ids,
        )
        async def randomcolor(ctx):
            await ctx.defer()
            rand_red = random.randint(0, 255)
            rand_green = random.randint(0, 255)
            rand_blue = random.randint(0, 255)

            im = Image.open("assets/logo_white_template.png")
            data = np.array(im)
            red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
            mask = (red == 255) & (green == 255) & (blue == 255)
            data[:, :, :3][mask] = [rand_red, rand_green, rand_blue]
            im = Image.fromarray(data)
            im = im.resize((80, 80))
            im.save("assets/temp/PixelHeim-Random-Color.png")

            randomcolor = discord.Embed(
                colour=discord.Colour.from_rgb(rand_red, rand_green, rand_blue)
            )
            randomcolor.add_field(
                name="Hex", value=rgb2hex(rand_red, rand_green, rand_blue), inline=False
            )
            randomcolor.add_field(
                name="RGB",
                value=f"{rand_red}, {rand_green}, {rand_blue} ",
                inline=False,
            )
            randomcolor.set_thumbnail(url="attachment://PixelHeim-Random-Color.png")
            await ctx.send(
                file=discord.File(
                    "assets/temp/PixelHeim-Random-Color.png",
                    filename="PixelHeim-Random-Color.png",
                ),
                embed=randomcolor,
            )

        @slash.slash(name="flip", description="Flip a coin", guild_ids=guild_ids)
        async def flip(ctx):
            await ctx.send(
                embed=discord.Embed(
                    title=random.choice(["Heads", "Tails"]),
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
            )

        @slash.slash(name="roll", description="Roll a die", guild_ids=guild_ids)
        async def dice(ctx):
            await ctx.send(
                file=discord.File(
                    f"assets/dice{random.randint(1, 6)}.png",
                    filename=f"PixelHeim-Die-Face.png",
                )
            )

        @slash.slash(
            name="8ball",
            description="Ask the Magic 8ball a question",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="question",
                    description="Ask your question",
                    option_type=3,
                    required=True,
                )
            ],
        )
        async def magic_ball(ctx, question: str):
            await ctx.defer()
            await asyncio.sleep(random.randint(0, 1))
            if not question.endswith("?"):
                question = question + "?"
            await ctx.send(
                embed=discord.Embed(
                    title=question,
                    description=random.choice(
                        [
                            "It is Certain.",
                            "It is decidedly so.",
                            "Without a doubt.",
                            "Yes definitely.",
                            "You may rely on it.",
                            "As I see it, yes.",
                            "Most likely.",
                            "Outlook good.",
                            "Yes.",
                            "Signs point to yes.",
                            "Reply hazy, try again.",
                            "Ask again later.",
                            "Better not tell you now.",
                            "Cannot predict now.",
                            "Concentrate and ask again.",
                            "Don't count on it.",
                            "My reply is no.",
                            "My sources say no.",
                            "Outlook not so good.",
                            "Very doubtful.",
                        ]
                    ),
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
            )

        @slash.slash(
            name="apply",
            description="Application for PixelHeim Staff",
            guild_ids=guild_ids,
            options=[
                create_option(
                    name="role",
                    description="Admin / Helper / Builder / Streamer",
                    option_type=3,
                    required=True,
                )
            ],
        )
        async def apply(ctx, role: str = "null"):
            guild = client.get_guild(834516102184828970)
            staff_app_channel = guild.get_channel(834691226644906015)
            author = ctx.author
            await log(f"{author} used /apply")
            if not staff_app_channel.permissions_for(author).view_channel:
                await ctx.send(
                    hidden=True,
                    embed=discord.Embed(
                        title="Sorry!",
                        description="Applications for staff are currently closed.",
                        colour=discord.Colour.from_rgb(255, 0, 0),
                    ),
                )
                return
            applications = ["admin", "helper", "builder", "streamer"]
            if author.id not in ops:
                if get(guild.roles, id=834716935018512395) in author.roles:
                    await log(
                        f"{author} was denied permission to apply for staff. (Reason: Already a staff member)"
                    )
                    await ctx.send(
                        hidden=True,
                        embed=discord.Embed(
                            description=f"{author.mention} sorry staff members cant apply for staff.",
                            colour=discord.Colour.from_rgb(255, 0, 0),
                        ),
                    )
                    return
            if role.lower() not in applications:
                await ctx.send(
                    hidden=True,
                    embed=discord.Embed(
                        description=f"**{role}** is not a correct option please choose from one of the following and "
                        f"retry.\n**• Admin**\n**• Helper**\n**• Builder**\n**• Streamer**",
                        colour=discord.Colour.from_rgb(255, 0, 0),
                    ),
                )
                return
            await ctx.defer(hidden=True)
            await log(f"{author} is applying for {role.capitalize()}")
            if role.lower() == "streamer":
                streamer_apply = discord.Embed(
                    title="Streamer Application",
                    description=f"{author.name} you need to file a [ticket](https://discord.com/channels/834516102184828970/834520977694130226/862606239703367720) in order to apply for Streamer.",
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
                streamer_apply.set_image(url="https://i.imgur.com/2nR55qk.png")
                await ctx.send(hidden=True, embed=streamer_apply)
            elif role.lower() == "builder":
                builder_apply = discord.Embed(
                    title="Builder Application",
                    description=f"{author.name} you need to file a [ticket](https://discord.com/channels/834516102184828970/834520977694130226/862606239703367720) in order to apply for Builder.",
                    colour=discord.Colour.from_rgb(255, 0, 0),
                )
                builder_apply.set_image(url="https://i.imgur.com/2nR55qk.png")
                await ctx.send(hidden=True, embed=builder_apply)
            else:
                author_uuid = str(
                    uuid.uuid3(
                        uuid.NAMESPACE_OID, f"{author.id}{role.lower()}{time.time()}"
                    )
                )
                r = requests.post(
                    "https://spirax.herokuapp.com/api/v1/applyinfdump",
                    headers={
                        "X-OAUTH-TOKEN": str(pyotp.TOTP(os.getenv("TOTP_TOKEN")).now())
                    },
                    json={
                        "uuid": author_uuid,
                        "name": str(author.name),
                        "discriminator": str(author.discriminator),
                        "role": role.lower(),
                        "avatar_url": author.avatar_url,
                        "user_id": author.id,
                        "joined_date": str(author.joined_at.strftime("%d %b, %Y")),
                        "channel_id": ctx.channel.id,
                    },
                )
                if r.status_code != 200:
                    await ctx.send(
                        hidden=True,
                        embed=discord.Embed(
                            title="Internal Server Error!",
                            description=f"Contact an administrator to fix the issue.",
                            colour=discord.Colour.from_rgb(255, 0, 0),
                        ),
                    )
                    await log(
                        f"Error while connecting to Spirax Server. (Status Code: {r.status_code})"
                    )
                    return
                await ctx.send(
                    hidden=True,
                    embed=discord.Embed(
                        title=f"{role.capitalize()} Application",
                        description=f"[Click Here to apply.](https://forms.pixel-heim.com/"
                        f"{role.lower()}?id={author_uuid})",
                        colour=discord.Colour.from_rgb(255, 0, 0),
                    ),
                )

        client.run(os.getenv("TOKEN"), reconnect=True)
