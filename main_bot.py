from discord.ext import commands
from discord.utils import get
import discord
import discord.user
from discord import Embed
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from botpackage import authentication
from botpackage import boards
from botpackage import diplomas
from botpackage import account_management
from botpackage import reviews
import datetime
import json
import random
import asyncio
import requests

# google sheets creds
scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "botpackage/client_secrets.json", scope)
google_client = gspread.authorize(creds)
questions_sheet = google_client.open("TriviaBot").worksheet("questions")
boards_sheet = google_client.open("TriviaBot").worksheet("leaderboards")
auth_sheet = google_client.open("TriviaBot").worksheet("auth")
transactions_sheet = google_client.open("TriviaBot").worksheet("transactions")

# bot token
token_file = open("bot_secrets", "r")
TOKEN = token_file.read()
token_file.close()
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)

# weather key
api_key = open("botpackage/openweathermap_key", "r").read()
base_url = "http://api.openweathermap.org/data/2.5/weather?"


@client.event
async def on_ready():
    print(f"I am ready to go - {client.user.name}")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,
                                                           name=f"{client.command_prefix}bot_help.\nThis bot is made by marinelairinavlad#0728."))

    # we display a random add, at a random time, through general channel only
    general_channel = client.get_channel(848949680809574463)
    ads_file = open("botpackage/ads.json", "r")
    ads_to_dict = json.load(ads_file)
    ads_file.close()

    print(f"We have in our data base {len(ads_to_dict.keys())} different ads.\n")
    sleep_list = [60 * 2, 60 * 3, 60 * 4, 60 * 5]
    # while the bot is on_ready mood, we send ads to general channel
    while True:
        time_interval = sleep_list[random.randint(0, 3)]
        print(f"I will wait {time_interval / 60} minutes before displaying the next ad.")
        await asyncio.sleep(time_interval)

        ad_dict = ads_to_dict[f"{random.randint(1, len(ads_to_dict.keys()))}"]

        embed = Embed(
            title=f"{ad_dict['brand']}",
            description=f"Hello @everyone!\n\nBy displaying this ad, you support us with 10lei!\nThis way, we can continue facilitate Python knowledge to everyone.\nWe are extremely grateful for your support!",
            colour=0xF4221F
        )

        ad_jpg = ad_dict['ad_name']
        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
        embed.set_image(url=ad_jpg)
        embed.set_thumbnail(url=trivia_logo_img)

        embed.set_footer(text=f"{datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
        await general_channel.send(embed=embed)
        print(f"I display the {ad_dict['brand']} ad.")

        # now we add 10 lei in server account for this add
        account_management.ads_remuneration(10)
        print("We added 10 lei in server account\n")


@client.event
async def on_member_join(member):
    server = client.get_guild(848949680809574460)
    guest = discord.utils.get(server.roles, name="Guest")
    await member.add_roles(guest)


# login command
@client.command(alliasses=["Help", "HELP"])
async def bot_help(ctx):
    print(f"**********************\nThe user {ctx.author.nick} has used !bot_help' command.\n-----")
    await ctx.send(f"Hello {ctx.author.mention}! What an awesome day it is today, right?")

    file_commands = open("commands.json", "r", encoding="utf8")
    dict_commands = json.load(file_commands)
    file_commands.close()

    embed = Embed(
        title=f"Trivia Bot commands' descriptions",
        description=f"Hi @everyone! 👋\nTriviaBot server's scope is to facilitate Python knowledge to everyone.\nWe are extremely happy that you've enjoyed our community!🤩\n\nHere are the features you can enjoy with us:",
        colour=0xF8F548,
        timestamp=ctx.message.created_at
    )
    # we generate the embed.add_field()  for each command
    for key in dict_commands.keys():
        invoke = dict_commands[key]["invoke"]
        if len(dict_commands[key]["permission_roles"]) == 5:
            permission_roles = "Permission roles: everyone"
        else:
            permission_roles = "Permission roles: "
            for role in dict_commands[key]["permission_roles"]:
                permission_roles += f"{role}, "
            # permission_roles = permission_roles[:-2] # we remove the last two charachters = ,_
            permission_roles = permission_roles.rstrip(", ")
        description = dict_commands[key]["description"]

        embed.add_field(name=f"👉    {invoke}", value=f"◻️{permission_roles}\n◻️Description: {description}\n",
                        inline=False)

    embed.add_field(name=f"👉🏽    NOTES:",
                    value=f"◻️Guest role: Is automatically assigned when the user joins the TriviaBot server.\n◻️Ads: Are displayed in #general channel at random times: 2, 3, 4 or 5 min.\n",
                    inline=False)

    trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
    embed.set_thumbnail(url=trivia_logo_img)
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/849695979775328296/863716464808034334/here20for20you20banner.png")
    embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
    embed.set_footer(text=f"Legend: everyone = Guest, Player, PremiumPlayer, PremiumMember, Admin")
    await ctx.send(embed=embed)


@client.command()
async def auth(context):
    print(f"***********************\nThe user {context.author.nick} has used !bot_help' command.\n-----")
    # we create a private channel for auth process with access for admin, bot and member only
    channel_name = f"auth_{context.author}"

    embed = Embed(
        title=f"Let's keep it private!",
        description=f"For authentication process, please see your new private channel: #{channel_name}.\nSee you there!",
        colour=0xB9BDA3
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/849695979775328296/860541113835978793/Private-877x432.png")
    embed.set_footer(text="❗ This message will be deleted in 15sec.")
    send = await context.send(embed=embed)
    await asyncio.sleep(15)
    await context.message.delete()
    await send.delete()

    guild = context.guild
    member = context.author
    admin_role = get(guild.roles, name="Admin")
    print(guild.default_role)
    print(guild.me)
    print(admin_role)
    print(member)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True),
        admin_role: discord.PermissionOverwrite(read_messages=True)
    }

    channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

    embed = Embed(
        title=f"Already a member of TriviaBot server?",
        description=f"Respond with 'y' or 'n'.",
        colour=0xB9BDA3
    )
    # then we start de auth process
    await channel.send(embed=embed)

    # This will make sure that the response will only be registered if the following conditions are met:
    def check(msg):
        return msg.author == context.author and msg.content != "" and msg.channel == channel

    msg = await client.wait_for("message", check=check)
    if msg.content.lower() == "y":
        embed = Embed(
            title=f"Perfect! 👌",
            description=f"Let's login 🙂",
            colour=0xB9BDA3
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860546794681139230/one-click-gmail-login-for-wordpress-featured-image.png")
        await channel.send(embed=embed)
        print("Login option:")
        while True:
            user = context.author.id
            embed = Embed(
                title="Your actual user(id):",
                description=f"{user}",
                colour=0xB9BDA3
            )
            await channel.send(embed=embed)
            print(f"Your actual user(id): {user}")

            embed = Embed(
                title="Password:",
                description="\u200b",
                colour=0xB9BDA3
            )
            await channel.send(embed=embed)
            password = await client.wait_for("message", check=check)
            print(f"Password: {password.content}")
            flag_login = authentication.login(str(user), password.content)
            embed = Embed(
                title=flag_login,
                description="\u200b",
                colour=0xB9BDA3
            )

            await channel.send(embed=embed)
            if "Welcome back " in flag_login:
                member = context.author
                player_role = discord.utils.get(context.message.guild.roles, name="Player")
                await member.add_roles(player_role)
                embed = Embed(
                    title="Glad to be part of our community",
                    description="You already have the Player role that let you enjoy our TriviaQuiz games!",
                    colour=0xB9BDA3
                )
                await channel.send(embed=embed)
                break

    else:
        embed = Embed(
            title="No problem!",
            description="Let's sign up.",
            colour=0xB9BDA3
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860544162105131058/signup.png")
        await channel.send(embed=embed)
        print("Sign up option")

        while True:
            user = context.author.id
            nickname = context.author.nick
            embed = Embed(
                title="Your actual user(id):",
                description=f"{user}",
                colour=0xB9BDA3
            )
            await channel.send(embed=embed)
            print(f"Your actual user: {user}")

            embed = Embed(
                title="Password:",
                description=f"(minimum 3 characters and no spaces)",
                colour=0xB9BDA3
            )
            await channel.send(embed=embed)
            password = await client.wait_for("message", check=check, timeout=60)
            print(f"Password: {password.content}")

            embed = Embed(
                title="Email:",
                description=f"(Please provide a valid email address)",
                colour=0xB9BDA3
            )
            await channel.send(embed=embed)
            email = await client.wait_for("message", check=check, timeout=60)
            print(f"Email: {email.content.lower()}")
            flag_signup = authentication.sign_up(str(user), password.content, email.content.lower(), nickname)

            embed = Embed(
                title=f"{flag_signup}",
                description="\u200b",
                colour=0xB9BDA3
            )
            await channel.send(embed=embed)
            if "The new account for the user " in flag_signup:
                member = context.author
                player_role = discord.utils.get(context.message.guild.roles, name="Player")
                await member.add_roles(player_role)
                break
            elif "The user already exists" in flag_signup:
                break
    embed = Embed(
        title="Warning!!",
        description=f"This channel ({channel_name}) will be deleted in 30 seconds.",
        colour=0xCA1218
    )
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/849695979775328296/860540162592211014/1200px-Gtk-dialog-warning.png")
    await channel.send(embed=embed)
    await asyncio.sleep(30)
    print('I waited 30 seconds. Channel deleted!')
    await channel.delete()


# clear command
@client.command()
async def clear(ctx):
    print(f"***********************\nThe user {ctx.author.nick} has used !clear command.\n-----")
    await ctx.channel.purge()


# trivia game
@client.command()
async def q(ctx):
    print(f"***********************\nThe user {ctx.author.nick} has used !q command.\n-----")
    server = client.get_guild(848949680809574460)
    player = discord.utils.get(server.roles, name="Player")
    if player in ctx.author.roles:
        print(f"{ctx.author} has the Player role.")

        if ctx.channel.id == 853194875478343701:
            # we display the trivia game rules first:
            embed = Embed(
                title=f"Trivia Game's rules:",
                description=f"Hi {ctx.author.mention}! 👋\nBefore playing, please check out the game's rules below.\nGood luck!",
                colour=0x55D13C,
                timestamp=ctx.message.created_at
            )

            embed.add_field(name=f"◻️Permission roles:",
                            value=f"Player, PremiumPlayer, PremiumMember, Admin\n"
                            ,
                            inline=False)
            embed.add_field(name=f"◻️Questions' difficulty:",
                            value=
                            f"- The bot gives you questions of two levels of difficulty:\n"
                            f"1. Easy - if you are a Player and PremiumPlayer\n"
                            f"2. Easy & Hard - if you are a PremiumPlayers\n"
                            ,
                            inline=False)
            embed.add_field(name=f"◻️How to answer:",
                            value=
                            f"- To answer, just click on the corresponding emoji number to the chosen option. The bot will give you feedback about your answer and then will delete the question.\n"
                            f"- You must select an answer in maximum 60 seconds. Otherwise, you will be notified and get 0 points.\n"
                            f"- Each correct answer gives you one point.\n"
                            ,
                            inline=False)
            embed.add_field(name=f"◻️How the game works:",
                            value=
                            f"- After each question, you can choose to continue('👍') or to stop ('👎') the game (20 sec).\n"
                            f"- You become a Premium Player after getting 20 points(=20 correct answers).\n"
                            f"- At the end of the game you will get your new total score and info about your current role. If you reach the minimum 20 points, you get the Premium Player role and a notification via email.\n",

                            inline=False)
            embed.add_field(name=f"◻️Your game activity:",
                            value=f"- The Bot measures the time session(end time - start time) and the number of total and correct answers.\n"
                                  f"- On the leaderboard, if there are two identical total scores, the tie will be made according to correct answer rate.\n"
                                  f"- You appear on leaderboard only if you are in the top 3 players. Anyway, you can use anytime the !myself command to find out info about your game account.",
                            inline=False)

            trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
            embed.set_thumbnail(url=trivia_logo_img)
            embed.set_image(
                url="https://cdn.discordapp.com/attachments/849695979775328296/883732026128211998/rules-text-red-grungy-lines-stamp-vintage-rubber-204706512.png")
            embed.set_footer(text="The Trivia Quiz Game will start in 60 seconds. Take a look on the rules first.",
                             icon_url="https://cdn.discordapp.com/attachments/849695979775328296/884052315554844702/360_F_302021050_Hmcj61mWDRhKVRxJ8O9oMRIa8QmlqFOx.png")
            embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

            # we wait 60 seconds before starting the game
            await asyncio.sleep(60)

            # then we start the game session
            scoring_sheet = google_client.open("TriviaBot").worksheet("scoring")
            id = ctx.author.id
            start_session_time = datetime.datetime.now().strftime("%d/%m/%y %H-%M-%S")
            start = datetime.datetime.now()
            no_questions = 0
            score = 0

            # questions from 1 - 10 are considered easy - for both Player & PremiumPlayer roles
            # questions starting from 11 are considered hard - only for PremiumPlayer role
            server = client.get_guild(848949680809574460)
            premium_player = discord.utils.get(server.roles, name="PremiumPlayer")
            if premium_player in ctx.author.roles:
                number_q = len(questions_sheet.col_values(1)) - 1
            else:
                number_q = 10

            while True:
                selected_question = random.randint(2, number_q + 1)
                if selected_question <= 10:
                    difficulty_level = "easy"
                else:
                    difficulty_level = "hard"
                question_list = questions_sheet.row_values(selected_question)
                q_id = question_list[0]
                q_question = question_list[1]
                q_ans1 = question_list[2]
                q_ans2 = question_list[3]
                q_ans3 = question_list[4]
                q_ans4 = question_list[5]
                q_correct = question_list[6]
                # await ctx.message.delete()  # the question is deleted

                embed = Embed(
                    title=f"{q_id}. {q_question}",
                    description="\u200b",
                    colour=0x2BDF26
                )
                embed.add_field(name=f"1. {q_ans1}", value="\u200b", inline=False)
                embed.add_field(name=f"2. {q_ans2}", value="\u200b", inline=False)
                embed.add_field(name=f"3. {q_ans3}", value="\u200b", inline=False)
                embed.add_field(name=f"4. {q_ans4}", value="\u200b", inline=False)

                trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                embed.set_thumbnail(url=trivia_logo_img)

                embed.set_author(
                    name=ctx.author.nick,
                    icon_url=ctx.author.avatar_url)

                embed.set_footer(
                    text=f"Difficulty level: {difficulty_level}\nDate: {datetime.datetime.now().strftime('%d/%m/%y    %H-%M-%S')}")

                msg = await ctx.send(embed=embed)

                await msg.add_reaction("1️⃣")
                await msg.add_reaction("2️⃣")
                await msg.add_reaction("3️⃣")
                await msg.add_reaction("4️⃣")

                try:
                    map_answers = {
                        "1": "1️⃣",
                        "2": "2️⃣",
                        "3": "3️⃣",
                        "4": "4️⃣"
                    }

                    def check_react(reaction, user):
                        if reaction.message.id != msg.id:
                            return False
                        if user != ctx.message.author:
                            return False
                        if str(reaction.emoji) not in map_answers.values():
                            return False
                        return True

                    reaction, user = await client.wait_for('reaction_add', check=check_react, timeout=60)

                    if reaction.emoji == map_answers[str(q_correct)]:
                        embed = Embed(
                            title=f"Bravo!",
                            description=f"Your answer is correct, {user.mention}!",
                            colour=0x88D21E
                        )
                        good_msg = await reaction.message.channel.send(embed=embed)
                        await good_msg.add_reaction("👏")
                        await reaction.message.delete()
                        no_questions += 1
                        score += 1
                    else:
                        embed = Embed(
                            title=f"Try better next time!",
                            description=f"Your answer is incorrect, {user.mention}!",
                            colour=0xF70A08
                        )
                        bad_msg = await reaction.message.channel.send(embed=embed)
                        await bad_msg.add_reaction("👎")
                        await reaction.message.delete()
                        no_questions += 1
                        score += 0  # no score added
                except asyncio.TimeoutError:
                    embed = Embed(
                        title=f"Too SLOW!!!",
                        description=f"Be faster next time!",
                        colour=0xC8E538
                    )
                    slow_msg = await ctx.send(embed=embed)
                    await slow_msg.add_reaction("🐌")
                    await msg.delete()
                    no_questions += 1
                    score += 0  # no score added

                list_msg = ["Having fun? Continue playing?",
                            "Good job! Are we continuing the game?",
                            "Curious about next question?",
                            "Are you ready for the next one?",
                            "Keep going?"
                            ]
                embed = Embed(
                    title=f"{list_msg[random.randint(0, len(list_msg) - 1)]}",
                    description="\u200b",
                    colour=0xCBCDC1
                )
                random_msg = await ctx.send(embed=embed)
                await random_msg.add_reaction("👍")
                await random_msg.add_reaction("👎")
                try:
                    def check_continue(reaction, user):
                        if reaction.message.id != random_msg.id:
                            return False
                        if user != ctx.message.author:
                            return False
                        if str(reaction.emoji) not in ["👎", "👍"]:
                            return False
                        return True

                    reaction, user = await client.wait_for('reaction_add', check=check_continue, timeout=20)

                    if str(reaction.emoji) == '👎':
                        stop = datetime.datetime.now()
                        time = (stop - start).seconds

                        embed = Embed(
                            title=f"TriviaGame over!",
                            description=f"Congrats {user.mention}!You've answered {no_questions} questions in {time} sec, and get a total session score of {score} points.",
                            colour=0xE368F3
                        )
                        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/attachments/849695979775328296/860529484511838278/2Q.png")
                        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y    %H-%M-%S')}",
                                         icon_url=trivia_logo_img)

                        await ctx.send(embed=embed)

                        new_line = len(scoring_sheet.col_values(1)) + 1
                        new_scoring = [str(id), start_session_time, time, no_questions, score]
                        scoring_sheet.insert_row(new_scoring, new_line)
                        print(
                            f"New scoring stored in google scoring sheet:\n=> {id} - {start_session_time} - {time} - {no_questions} questions - {score} points.")
                        await reaction.message.delete()

                        if boards.total_score(str(id)) >= 20:
                            member = ctx.author
                            premium_player_role = discord.utils.get(ctx.message.guild.roles, name="PremiumPlayer")
                            await member.add_roles(premium_player_role)

                            premium_user = client.get_user(int(id))

                            embed = Embed(
                                title=f"Congrats! 🥳",
                                description=f"{premium_user.mention}, your total score is now {boards.total_score(str(id))}, which gives you the PremiumPlayer role!",
                                colour=0x68B3F3
                            )
                            trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/attachments/849695979775328296/860528793763315742/3686d2a0cc9076dce800a14af5f47bdc.png")
                            embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y    %H-%M-%S')}",
                                             icon_url=trivia_logo_img)

                            await ctx.send(embed=embed)

                            # we send the diploma only if we didn't sent it before
                            dict = diplomas.get_email(str(id))
                            if dict['premium_player'] == "no":
                                diplomas.send_diploma("premium_player", dict["email"],
                                                      diplomas.generate_diploma("premium_player", ctx.author.nick))
                                embed = Embed(
                                    title="You have 1 new e-mail message",
                                    description="Check out your inbox! 😉",
                                    colour=0xED94F0
                                )
                                pic = "https://cdn.discordapp.com/attachments/849695979775328296/860836715403673600/shutterstock_119977678-700x467.png"
                                embed.set_thumbnail(url=pic)
                                embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                                await ctx.send(embed=embed)
                            # we put a note in the auth gs that we sent the diploma
                            auth_sheet.update_cell(int(dict["row"]), 6, "yes")
                        else:
                            premium_user = client.get_user(id)
                            embed = Embed(
                                title=f"Keep playing! 🕹️",
                                description=f"{premium_user.mention}, you only need {20 - boards.total_score(f'{id}')} more points to get the PremiumPlayer role!",
                                colour=0x68B3F3
                            )
                            trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/attachments/849695979775328296/860529909848211456/48631962.png")
                            embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y    %H-%M-%S')}",
                                             icon_url=trivia_logo_img)

                            await ctx.send(embed=embed)

                        break
                    else:
                        await reaction.message.delete()
                        continue
                except asyncio.TimeoutError:
                    embed = Embed(
                        title=f"Too SLOW!!!",
                        description=f"Be faster next time! Your session ended.",
                        colour=0xC8E538
                    )
                    slow_msg = await ctx.send(embed=embed)
                    await slow_msg.add_reaction("🐌")

                    # we follow the same code from "end game" option

                    stop = datetime.datetime.now()
                    time = (stop - start).seconds

                    embed = Embed(
                        title=f"TriviaGame over!",
                        description=f"Congrats {ctx.author.mention}!You've answered {no_questions} questions in {time} sec, and get a total session score of {score} points.",
                        colour=0xE368F3
                    )
                    trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/849695979775328296/860529484511838278/2Q.png")
                    embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y    %H-%M-%S')}",
                                     icon_url=trivia_logo_img)

                    await ctx.send(embed=embed)

                    new_line = len(scoring_sheet.col_values(1)) + 1
                    new_scoring = [str(id), start_session_time, time, no_questions, score]
                    scoring_sheet.insert_row(new_scoring, new_line)
                    print(
                        f"New scoring stored in google scoring sheet:\n=> {id} - {start_session_time} - {time} - {no_questions} questions - {score} points.")

                    if boards.total_score(str(id)) >= 20:
                        member = ctx.author
                        premium_player_role = discord.utils.get(ctx.message.guild.roles, name="PremiumPlayer")
                        await member.add_roles(premium_player_role)

                        premium_user = client.get_user(int(id))

                        embed = Embed(
                            title=f"Congrats! 🥳",
                            description=f"{premium_user.mention}, your total score is now {boards.total_score(str(id))}, which gives you the PremiumPlayer role!",
                            colour=0x68B3F3
                        )
                        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/attachments/849695979775328296/860528793763315742/3686d2a0cc9076dce800a14af5f47bdc.png")
                        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y    %H-%M-%S')}",
                                         icon_url=trivia_logo_img)

                        await ctx.send(embed=embed)

                        # we send the diploma only if we didn't sent it before
                        dict = diplomas.get_email(str(id))
                        if dict['premium_player'] == "no":
                            diplomas.send_diploma("premium_player", dict["email"],
                                                  diplomas.generate_diploma("premium_player", ctx.author.nick))
                            embed = Embed(
                                title="You have 1 new e-mail message",
                                description="Check out your inbox! 😉",
                                colour=0xED94F0
                            )
                            pic = "https://cdn.discordapp.com/attachments/849695979775328296/860836715403673600/shutterstock_119977678-700x467.png"
                            embed.set_thumbnail(url=pic)
                            embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                            await ctx.send(embed=embed)
                        # we put a note in the auth gs that we sent the diploma
                        auth_sheet.update_cell(int(dict["row"]), 6, "yes")

                    break


        else:
            embed = Embed(
                title="Wrong channel!",
                description="Please visit #trivia-game.",
                colour=0x68B3F3
            )
            trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/849695979775328296/860548227480944640/d2xgw61-4edbb414-b68e-4edf-ae7a-7ec230e2217e.png")
            embed.set_footer(
                text=f"❗ This message will be deleted in 15sec.   |   Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}",
                icon_url=trivia_logo_img)

            send = await ctx.send(embed=embed)
            await asyncio.sleep(15)
            await ctx.message.delete()
            await send.delete()

    else:

        embed = Embed(
            title="You don't have the Player role.",
            description="Please use the !auth command to role-in!",
            colour=0x68B3F3
        )
        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860548650433511424/30823194-access-denied-stamp.png")

        embed.set_footer(
            text=f"❗ This message will be deleted in 15sec.   |   Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}",
            icon_url=trivia_logo_img)

        send = await ctx.send(embed=embed)
        await asyncio.sleep(15)
        await ctx.message.delete()
        await send.delete()


@client.command()
async def role(ctx, user: discord.Member, *, role: discord.Role):
    print(f"***********************\nThe user {ctx.author.nick} has used !role command.\n-----")

    server = client.get_guild(848949680809574460)
    admin = discord.utils.get(server.roles, name="Admin")
    if admin not in ctx.author.roles:
        await ctx.send(f"{user.mention}, you need Admin role for this command!")
        print(f"{user.mention}, you need Admin role for this command!")
    else:

        if role.position > ctx.author.top_role.position:  # if the role is above users top role it sends error
            print("That role is above your top role!")
            return await ctx.send('**:x: | That role is above your top role!**')

        if role in user.roles:
            await user.remove_roles(role)  # removes the role if user already has
            await ctx.send(f"Removed {role} from {user.mention}")
            print(f"Removed {role} from {user.mention}")
        else:
            await user.add_roles(role)  # adds role if not already has it
            await ctx.send(f"Added {role} to {user.mention}")
            print(f"Added {role} to {user.mention}")


@client.command()
async def leaderboard(ctx):
    print(f"***********************\nThe user {ctx.author.nick} has used !leaderboard command.\n-----")

    server = client.get_guild(848949680809574460)
    player = discord.utils.get(server.roles, name="Player")
    guest = discord.utils.get(server.roles, name="Guest")
    top_role = ctx.author.top_role
    if ctx.author.top_role.position >= player.position:
        embed = Embed(
            title="Feature access granted!",
            description=f"Your top role is {top_role} (>=Player) so you can see the up-to-date leaderboard in #leaderboards channel!",
            colour=0x68B3F3,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860549674498654258/Access_Granted_01.png")
        await ctx.send(embed=embed)
        await ctx.message.delete(delay=3)
        boards.leaderboards()
        channel = client.get_channel(853926464152141844)
        await channel.purge()

        embed = Embed(
            title="TriviaQuiz leaderboard",
            description="HELLO @everyone!\nCurious about the TriviaQuiz Game winners?\n🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁🥁",
            colour=0xF4221F
        )

        second_user = client.get_user(int(boards_sheet.cell(3, 1).value))
        first_user = client.get_user(int(boards_sheet.cell(2, 1).value))
        third_user = client.get_user(int(boards_sheet.cell(4, 1).value))
        embed.add_field(name=f"2ND PLACE",
                        value=f"{second_user.mention}\nTP: {boards_sheet.cell(3, 5).value}\nCAR: {boards_sheet.cell(3, 6).value}%")  # second place
        embed.add_field(name=f"1ST PLACE",
                        value=f"{first_user.mention}\nTP: {boards_sheet.cell(2, 5).value}\nCAR: {boards_sheet.cell(2, 6).value}%")  # first place
        embed.add_field(name=f"3RD PLACE",
                        value=f"{third_user.mention}\nTP: {boards_sheet.cell(4, 5).value}\nCAR: {boards_sheet.cell(4, 6).value}%")  # third place

        podium_img = "https://cdn.discordapp.com/attachments/849695979775328296/860492007536853002/white-winners-podium-vector-18474376.jpg"
        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
        embed.set_image(url=podium_img)
        # embed.set_thumbnail(url=trivia_logo_img)

        embed.set_author(
            name=ctx.author.nick,
            icon_url=ctx.author.avatar_url)

        # embed.timestamp = datetime.datetime.now()
        embed.set_footer(text="Legend: TP=Total Points | CAR=correct answer rate")
        await channel.send(embed=embed)

        # we send diplomas to each winner
        accolades = ["first_place", "second_place", "third_place"]

        embed = Embed(
            title="Congrats you nerds! 🤓",
            description=f"Check out your e-mails, {first_user.mention}, {second_user.mention} & {third_user.mention}! 📥😉",
            colour=0xF4221F
        )
        congrats_img = "https://cdn.discordapp.com/attachments/849695979775328296/860490493758537728/congrats.jpg"
        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
        embed.set_image(url=congrats_img)
        # embed.set_thumbnail(url=trivia_logo_img)
        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y    %H-%M-%S')}",
                         icon_url=trivia_logo_img)
        await channel.send(embed=embed)

        for i in range(2, 5):
            dict = diplomas.get_email(str(boards_sheet.cell(i, 1).value))
            user = await client.fetch_user(int(boards_sheet.cell(i, 1).value))
            # print(str(user).split("#")[0])
            diplomas.send_diploma(accolades[i - 2], dict["email"],
                                  diplomas.generate_diploma(accolades[i - 2], str(user).split("#")[0]))


    elif ctx.author.top_role == guest:
        embed = Embed(
            title="Limited access!",
            description=f"Sorry {ctx.message.author.mention}! You have a Guest role with no access to leaderboards. Sign-in for Player role using <!auth> command!",
            colour=0x68B3F3,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860550698474930186/limited-access-stamp-round-vintage-grunge-label-sign-186966914.png")
        await ctx.send(embed=embed)
    else:
        embed = Embed(
            title="You have no roles!",
            description=f"Sorry {ctx.message.author.mention}! You have no roles assigned yet! Sign-in for Player role using <!auth> command!",
            colour=0x68B3F3,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860550698474930186/limited-access-stamp-round-vintage-grunge-label-sign-186966914.png")
        await ctx.send(embed=embed)


@client.command()
async def set_account(ctx):
    print(f"***********************\nThe user {ctx.author.nick} has used !set_account command.\n-----")

    accounts_list = transactions_sheet.col_values(1)

    if str(ctx.author.id) in accounts_list:
        embed = Embed(
            title="Game account already exists",
            description=f"Dear {ctx.author.mention}!\n\nYou already have a game account. Your actual sold is {account_management.check_balance(ctx.author.id)} lei.\nFor more features please use !manage_account command.\n\nEnjoy!",
            colour=0x4BC569,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/861200616412020736/error.png")
        await ctx.send(embed=embed)
        print("Error! Account already exists.")
    else:
        if account_management.create_account(ctx.author.id, 0) == ctx.author.id:
            embed = Embed(
                title="Solved: game account request",
                description=f"Dear {ctx.author.mention}!\nYour game account has been set with the amount of {0.0} lei.\nEnjoy our features!",
                colour=0x4BC569,
                timestamp=ctx.message.created_at
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/849695979775328296/860804683144495164/360_F_61871364_18N7Ha2pFz02dotLzpsw7NXNBfXh9rW1.png")
            await ctx.send(embed=embed)
            print("The account was set up!")


@client.command()
async def manage_account(ctx):
    print(f"***********************\nThe user {ctx.author.nick} has used !manage_account command.\n-----")

    # we first verify if the user has the account:
    accounts_list = transactions_sheet.col_values(1)

    if str(ctx.author.id) not in accounts_list:
        embed = Embed(
            title="Game account doesn't exist",
            description=f"Dear {ctx.author.mention}!\n\nYou don't have a game account.\nPlease use !set_account commmand to get one. After this, you cand use !manage_account for more features!\n\nThank you for understanding!",
            colour=0x4BC569,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860548650433511424/30823194-access-denied-stamp.png")
        await ctx.send(embed=embed)
        print("Game account doesn't exist")
    else:
        # we create a private channel for manage_account feature with access for admin, bot and user only
        channel_name = f"manage_account_{ctx.author}_{datetime.datetime.today()}"

        embed = Embed(
            title=f"Let's keep it private!",
            description=f"For account management features, please see your new private channel: #{channel_name}.\nSee you there!",
            colour=0xB9BDA3
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860541113835978793/Private-877x432.png")
        embed.set_footer(
            text=f"❗ This message will be deleted in 15sec.   |   Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")

        send = await ctx.send(embed=embed)
        await asyncio.sleep(15)
        await ctx.message.delete()
        await send.delete()

        guild = ctx.guild
        member = ctx.author
        admin_role = get(guild.roles, name="Admin")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            admin_role: discord.PermissionOverwrite(read_messages=True)
        }

        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)
        print("Private channel created for manage_account")

        while True:
            embed = Embed(
                title=f"Account management options:",
                description=f"Please choose emoji number corresponding to your option.",
                colour=0xB9BDA3
            )

            trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
            embed.set_thumbnail(url=trivia_logo_img)

            embed.add_field(name="1.", value="Check your account balance")
            embed.add_field(name="2.", value="Buy Premium Member Title (100lei)")
            embed.add_field(name="3.", value="Refund your account")
            embed.add_field(name="4.", value="Donate to TriviaBot server")
            embed.add_field(name="5.", value="Generate account statement via email")
            embed.add_field(name="6", value="Exit & Delete channel")

            # This will make sure that the response will only be registered if the following conditions are met:
            # def check(msg):
            #     return msg.author == ctx.author and msg.content != "" and msg.channel == channel

            msg = await channel.send(embed=embed)

            await msg.add_reaction("1️⃣")
            await msg.add_reaction("2️⃣")
            await msg.add_reaction("3️⃣")
            await msg.add_reaction("4️⃣")
            await msg.add_reaction("5️⃣")
            await msg.add_reaction("6️⃣")
            try:
                map_answers = {
                    "1": "1️⃣",
                    "2": "2️⃣",
                    "3": "3️⃣",
                    "4": "4️⃣",
                    "5": "5️⃣",
                    "6": "6️⃣"
                }

                def check_react(reaction, user):
                    if reaction.message.id != msg.id:
                        return False
                    if user != ctx.message.author:
                        return False
                    if str(reaction.emoji) not in map_answers.values():
                        return False
                    return True

                reaction, user = await client.wait_for('reaction_add', check=check_react, timeout=120)

                if reaction.emoji == map_answers['1']:
                    print(50 * "*" + "\nOpt 1 - account balance")

                    sold = account_management.check_balance(ctx.author.id)

                    embed = Embed(
                        title=f"Your account balance",
                        description=f"Dear {ctx.author.mention},\nYou still have {sold} lei in your account.\nSpend them with pleasure!",
                        colour=0xC14BC5
                    )
                    trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                    embed.set_thumbnail(url=trivia_logo_img)
                    embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                    await channel.send(embed=embed)

                    print(f"{ctx.author.mention} has {sold} lei in his/her account.")

                elif reaction.emoji == map_answers['2']:
                    print(50 * "*" + "\nOpt 2 - Buy Premium Member Title")

                    sold = account_management.check_balance(ctx.author.id)
                    if float(sold) < float(100):
                        embed = Embed(
                            title=f"Insufficient balance",
                            description=f"Dear {ctx.author.mention},\nYou only have {sold} lei in your account which is not enough for buying the Premium Member Title (fee: 100 lei).\nRefund your account!",
                            colour=0xED94F0
                        )
                        pic = "https://cdn.discordapp.com/attachments/849695979775328296/860830985347137536/Monopoly-Man-Broke-Broke-Ass-Stuart1.png"
                        embed.set_thumbnail(url=pic)
                        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                        await channel.send(embed=embed)

                        print("Insufficient balance for buying Premium Member Title.")
                    else:
                        server_id = ctx.message.guild.id
                        if account_management.donate(ctx.author.id, server_id, 100, "Premium Member Title"):
                            member = ctx.author
                            premium_member_role = discord.utils.get(ctx.message.guild.roles, name="PremiumMember")
                            await member.add_roles(premium_member_role)

                            embed = Embed(
                                title=f"Congrats",
                                description=f"Dear {ctx.author.mention},\nYou have now the Premium Member Title.\nEnjoy the new features!",
                                colour=0xED94F0
                            )
                            pic = "https://cdn.discordapp.com/attachments/849695979775328296/860528793763315742/3686d2a0cc9076dce800a14af5f47bdc.png"
                            embed.set_thumbnail(url=pic)
                            embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                            await channel.send(embed=embed)
                            print(f"{ctx.author.mention} have now the Premium Member Title.")

                            # we send the diploma only if we didn't sent it before
                            dict = diplomas.get_email(str(ctx.author.id))
                            if dict['premium_member'] == "no":
                                diplomas.send_diploma("premium_member", dict["email"],
                                                      diplomas.generate_diploma("premium_member", ctx.author.nick))

                                embed = Embed(
                                    title="You have 1 new e-mail message",
                                    description="Check out your inbox! 😉",
                                    colour=0x94E61E
                                )
                                pic = "https://cdn.discordapp.com/attachments/849695979775328296/860836715403673600/shutterstock_119977678-700x467.png"
                                embed.set_thumbnail(url=pic)
                                embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                                await channel.send(embed=embed)

                                print("Diploma from Premium Member was sent via email.")
                            else:
                                print("Diploma from Premium Member was already sent.")

                            # we put a note in the auth gs that we sent the diploma
                            auth_sheet.update_cell(int(dict["row"]), 7, "yes")
                            print("Trivia Bot sheet from google was updated with the new Premium Member Title.")
                elif reaction.emoji == map_answers['3']:
                    print(50 * '*' + "\nOpt 3 - refund account")

                    def check(msg):
                        return msg.author == ctx.author and msg.content != "" and msg.channel == channel

                    while True:
                        embed = Embed(
                            title="Amount to be refund:",
                            description=f"Enter only integers please (e.g. 150)!",
                            colour=0xB9BDA3
                        )
                        await channel.send(embed=embed)
                        amount = await client.wait_for("message", check=check, timeout=60)
                        print(amount.content)
                        try:
                            print(f"Refund of {float(amount.content)} lei")
                            break
                        except:
                            await channel.send("Please enter only integers(e.g. 325)")
                            print("Wrong format!")

                    admin = client.get_user(805790299133706241)

                    embed = Embed(
                        title="Refund account request",
                        description=f"Hello {admin.mention}!\nPlease approve my account refund with the {float(amount.content)} lei.\nThank you!",
                        colour=0x4BC569
                    )
                    embed.set_thumbnail(
                        url="https://cdn.discordapp.com/attachments/849695979775328296/860847924284227594/Make-more-money-2021-1024x576.png")
                    embed.set_author(
                        name=ctx.author.nick,
                        icon_url=ctx.author.avatar_url)
                    embed.set_footer(text="Expected answer: 'ok'")
                    await channel.send(embed=embed)

                    def check(msg):
                        return msg.author.id == 805790299133706241 and msg.content != "" and msg.channel == channel

                    msg = await client.wait_for("message", check=check)

                    if msg.content.lower() == "ok":
                        if account_management.refund_account(ctx.author.id, float(amount.content)):
                            embed = Embed(
                                title="Refund account done",
                                description=f"Hello {ctx.author.mention}!\nYour account was refunded with {float(amount.content)}lei.\nYour current balance is {account_management.check_balance(ctx.author.id)}lei.\nEnjoy!",
                                colour=0x4BC569
                            )
                            await channel.send(embed=embed)
                            print(
                                f"The account was refunded with {float(amount.content)}lei.\nYour current balance is {account_management.check_balance(ctx.author.id)}lei.")
                    else:
                        await channel.send(f"Sorry! Refund account rejected by Admin!")
                        print(f"Sorry! Refund account rejected by Admin!")
                elif reaction.emoji == map_answers['4']:
                    print(50 * '*' + "\nOpt 4 - Donate to TriviaBot server")

                    def check(msg):
                        return msg.author == ctx.author and msg.content != "" and msg.channel == channel

                    while True:
                        embed = Embed(
                            title="Amount to be donated:",
                            description=f"Enter only integers please (e.g. 250)!",
                            colour=0xB9BDA3
                        )
                        await channel.send(embed=embed)
                        amount = await client.wait_for("message", check=check, timeout=60)
                        print(amount.content)
                        try:
                            print(f"Refund of {float(amount.content)} lei")
                            break
                        except:
                            await channel.send("Please enter only integers(e.g. 325)")
                            print("Wrong format!")

                    sold = account_management.check_balance(ctx.author.id)
                    if float(sold) < float(amount.content):
                        embed = Embed(
                            title=f"Insufficient balance",
                            description=f"Dear {ctx.author.mention},\nYou only have {sold}lei in your account.\nRefund your account!",
                            colour=0xED94F0
                        )
                        pic = "https://cdn.discordapp.com/attachments/849695979775328296/860830985347137536/Monopoly-Man-Broke-Broke-Ass-Stuart1.png"
                        embed.set_thumbnail(url=pic)
                        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                        await channel.send(embed=embed)

                        print("Insufficient balance for desired donation.")
                    else:
                        server_id = "848949680809574460"
                        account_management.donate(ctx.author.id, server_id, float(amount.content), "Donation to Server")

                        embed = Embed(
                            title=f"Thank you!",
                            description=f"Dear {ctx.author.mention},\nThank you for your generous gift to TriviaBot Server! We are thrilled to have your support. Through your donation we have been able to continue working towards facilitate Python knowledge to everyone. You truly make the difference for us, and we are extremely grateful!\nEnjoy our community!",
                            colour=0xED94F0
                        )
                        pic = "https://cdn.discordapp.com/attachments/849695979775328296/860861959011041280/gift_card_donation_thank_you_thumb.png"
                        embed.set_thumbnail(url=pic)
                        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                        await channel.send(embed=embed)

                        print("Donation to Server - done!")


                elif reaction.emoji == map_answers['5']:
                    print(50 * '*' + "\nOpt 5 - Generates account statement in pdf and send via email")
                    dict = diplomas.get_email(ctx.author.id)
                    if account_management.send_account_statements(dict['nickname'], dict['email'],
                                                                  account_management.generate_account_statements_pdf(
                                                                      ctx.author.id)):
                        embed = Embed(
                            title="You have 1 new e-mail message",
                            description=f"Hi there {ctx.author.mention}!\nCheck out your inbox! Your account statement was generated in pdf format and sent to you.\nHave a nice time on our server! 😉",
                            colour=0xED94F0
                        )
                        pic = "https://cdn.discordapp.com/attachments/849695979775328296/860836715403673600/shutterstock_119977678-700x467.png"
                        embed.set_thumbnail(url=pic)
                        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                        await channel.send(embed=embed)
                        print("Account statements was sent via email.")

                elif reaction.emoji == map_answers['6']:
                    print("Opt 6 - Exit")
                    embed = Embed(
                        title=f"Exit from menu",
                        description=f"Dear {ctx.author.mention},\nWe hope you enjoy our menu options!\nThank you!",
                        colour=0xED94F0
                    )
                    pic = "https://cdn.discordapp.com/attachments/849695979775328296/860864136187084860/emergency-exit.png"
                    embed.set_thumbnail(url=pic)
                    embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                    await channel.send(embed=embed)
                    break
                else:
                    break
            except asyncio.TimeoutError:
                embed = Embed(
                    title=f"Too SLOW!!!",
                    description=f"Be faster next time!",
                    colour=0xC8E538
                )
                slow_msg = await channel.send(embed=embed)
                await slow_msg.add_reaction("🐌")
                await msg.delete()

        # we delete the channel after break
        embed = Embed(
            title="Warning!!",
            description=f"This channel ({channel_name}) will be deleted in 30 seconds.",
            colour=0xCA1218
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860540162592211014/1200px-Gtk-dialog-warning.png")
        await channel.send(embed=embed)
        await asyncio.sleep(30)
        print('I waited 30 seconds. Channel deleted!')
        await channel.delete()


@client.command()
async def server_report(ctx):
    print(f"***********************\nThe user {ctx.author.nick} has used !server_report command.\n-----")

    server = client.get_guild(848949680809574460)
    admin = discord.utils.get(server.roles, name="Admin")
    premium_member = discord.utils.get(server.roles, name="PremiumMember")
    flag = admin in ctx.author.roles or premium_member in ctx.author.roles
    if flag == False:
        embed = Embed(
            title=f"Feature denied!",
            description=f"Sorry {ctx.author.mention}!\nThis feature is for Premium Members or Admin only.\nYou can buy Premium Member Title using !manage_account command.\nThank you for understanding!",
            colour=0xB9BDA3
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/861584178676236288/What-to-Do-When-YouE28099re-Denied-for-Life-Insurance.png")
        embed.set_footer(text=f"Date: {datetime.datetime.now()}")
        await ctx.send(embed=embed)
        print(f"Access denied to !server_report command. {ctx.author.name} doesn't have Admin or Premium Member Role.")
    else:
        channel_name = f"server_report_{ctx.author}_{datetime.datetime.now()}"

        embed = Embed(
            title=f"Let's keep it private!",
            description=f"For 'server_report' feature, please see our new private channel: #{channel_name}.\nSee you there!",
            colour=0xB9BDA3,
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860541113835978793/Private-877x432.png")
        embed.set_footer(text="❗ This message will be deleted in 10sec.")
        send = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await send.delete()

        guild = ctx.guild
        member = ctx.author
        admin_role = get(guild.roles, name="Admin")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            admin_role: discord.PermissionOverwrite(read_messages=True)
        }

        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        print("Private channel was created.")
        # we get server's info, using server's id
        server_id = ctx.message.guild.id

        #     return (no_transactions, total_sold, no_transactions_premium_member, sold_from_premium_member,
        #     no_transactions_donation_to_server, sold_from_donation_to_server, no_transactions_ads, sold_from_ads)
        list_server_report = account_management.server_account_report(server_id)
        # we generate the embed message:

        embed = Embed(
            title=f"TriviaBot server's financial report!",
            description=f"Dear {ctx.author.mention}!\nLet's take a look on the newest TriviaBot server's financial report!\nEnjoy!",
            colour=0xD9100A
        )
        embed.add_field(name="#️⃣ transactions:", value=f"{int(list_server_report[0])}")
        embed.add_field(name="💰 Total sold:", value=f"{float(list_server_report[1])} lei")
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="#️⃣ Premium Member:", value=f"{int(list_server_report[2])}")
        embed.add_field(name="💰 Premium Member:", value=f"{float(list_server_report[3])} lei")
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="#️⃣ Donations:", value=f"{int(list_server_report[4])}")
        embed.add_field(name="💰 Donations:", value=f"{float(list_server_report[5])} lei")
        embed.add_field(name="\u200b", value="\u200b")
        embed.add_field(name="#️⃣ Ads:", value=f"{int(list_server_report[6])}")
        embed.add_field(name="💰 Ads:", value=f"{float(list_server_report[7])} lei")
        embed.add_field(name="\u200b", value="\u200b")

        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png")
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/849695979775328296/863430935454023700/0KN5232szzqbT_NRvE4QD0E2ydq7bJb8Z30t9LLjh4RbXAD0wmOseygljl6a9HDQB6YwGFT0futQBOojHQzPhfR0gEGYwsTt3IWb.png")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)

        embed.set_footer(
            text=f"Legend: #️⃣=number of transactions | 💰=amount from\n❗ Feature available only for Admin and Premium Member Roles.")
        await channel.send(embed=embed)
        print(f"Server's financial report was listed in {channel_name}.")

        embed = Embed(
            title="Warning!!",
            description=f"This channel ({channel_name}) will be deleted in 2 minutes.",
            colour=0xCA1218
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860540162592211014/1200px-Gtk-dialog-warning.png")
        await channel.send(embed=embed)
        await asyncio.sleep(60 * 2)
        await channel.delete()
        print(f'I waited 2 minutes. Channel {channel_name} was deleted!')


@client.command()
async def myself(ctx):
    print(f"***********************\nThe user {ctx.author.nick} has used !myself command.\n-----")

    server = client.get_guild(848949680809574460)
    premium_member = discord.utils.get(server.roles, name="PremiumMember")

    if premium_member not in ctx.author.roles:
        embed = Embed(
            title=f"Feature denied!",
            description=f"Sorry {ctx.author.mention}!\nThis feature is for PremiumMembers only.\nYou can buy this title using !manage_account command.\nThank you for understanding!",
            colour=0xB9BDA3
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/861584178676236288/What-to-Do-When-YouE28099re-Denied-for-Life-Insurance.png")
        embed.set_footer(text=f"Date: {datetime.datetime.now()}")
        await ctx.send(embed=embed)
        print("Access denied to !myself command. Not a Premium Member.")
    else:
        channel_name = f"about_me_{ctx.author}_{datetime.datetime.now()}"

        embed = Embed(
            title=f"Let's keep it private!",
            description=f"For 'about yourself info' features, please see your new private channel: #{channel_name}.\nSee you there!",
            colour=0xB9BDA3
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860541113835978793/Private-877x432.png")
        embed.set_footer(text="❗ This message will be deleted in 10sec.")
        send = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await send.delete()

        guild = ctx.guild
        member = ctx.author
        admin_role = get(guild.roles, name="Admin")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            admin_role: discord.PermissionOverwrite(read_messages=True)
        }

        channel = await guild.create_text_channel(channel_name, overwrites=overwrites)

        dict_myself = account_management.about_myself(ctx.author.id)
        embed = Embed(
            title="Info about myself",
            description=f"Hello {ctx.author.mention}!\nCurious about your activity on TriviaBot Server?\nEnjoy your resume!\n\nP.S. This feature is available only for Premium Members. Thank your for your support!\n",
            colour=0xF4221F
        )
        embed.add_field(name=f"\u200b", value=f"\u200b")
        embed.add_field(name=f"MEMBER 🛈", value=f"\u200b")
        embed.add_field(name=f"\u200b", value=f"\u200b")
        # embed.add_field(name=f"Nickname:", value=f"{dict_myself['nickname']}")
        embed.add_field(name=f"Email:", value=f"{dict_myself['email']}")
        embed.add_field(name=f"Premium Player role?", value=f"{dict_myself['premium_player']}")
        embed.add_field(name=f"Premium Member role?", value=f"{dict_myself['premium_member']}")

        embed.add_field(name=f"\u200b", value=f"\u200b", inline=False)

        embed.add_field(name=f"\u200b", value=f"\u200b")
        embed.add_field(name=f"GAME 🛈", value=f"\u200b")
        embed.add_field(name=f"\u200b", value=f"\u200b")
        embed.add_field(name=f"Player ID:", value=f"{dict_myself['player_id']}")
        embed.add_field(name=f"Total #sessions:", value=f"{dict_myself['no_sessions']}")
        embed.add_field(name=f"Total time:", value=f"{dict_myself['total_time']} sec")
        embed.add_field(name=f"Total #questions:", value=f"{dict_myself['total_no_questions']}")
        embed.add_field(name=f"Total score:", value=f"{dict_myself['total_score']}")
        embed.add_field(name=f"Leaderboard place:", value=f"{dict_myself['leaderboard_place']}")

        embed.add_field(name=f"\u200b", value=f"\u200b", inline=False)

        embed.add_field(name=f"\u200b", value=f"\u200b")
        embed.add_field(name=f"ACCOUNT 🛈", value=f"\u200b")
        embed.add_field(name=f"\u200b", value=f"\u200b")
        # embed.add_field(name=f"Account ID:", value=f"{dict_myself['account_id']}")
        embed.add_field(name=f"Sold:", value=f"{dict_myself['sold']} lei")
        embed.add_field(name=f"Opening data:", value=f"{dict_myself['data_account']}")
        embed.add_field(name=f"Total #transactions:", value=f"{dict_myself['no_transactions']}")

        img = "https://cdn.discordapp.com/attachments/849695979775328296/861330549859418132/How-to-Write-an-Engaging-About-Me-Page-for-a-WordPress-Website.png"
        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
        embed.set_image(url=img)
        embed.set_thumbnail(url=trivia_logo_img)

        embed.set_author(
            name=ctx.author.nick,
            icon_url=ctx.author.avatar_url)

        # embed.timestamp = datetime.datetime.now()
        embed.set_footer(
            text=f"Legend: #=number of    |    Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%m-%S')}")
        await channel.send(embed=embed)

        print(f"Info about {ctx.author.nick} displayed.")

        embed = Embed(
            title="Warning!!",
            description=f"This channel ({channel_name}) will be deleted in 3 minutes.",
            colour=0xCA1218
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860540162592211014/1200px-Gtk-dialog-warning.png")
        await channel.send(embed=embed)
        await asyncio.sleep(60 * 3)
        await channel.delete()
        print('I waited 3 minutes. Channel deleted!')


@client.command()
async def friend_donation(ctx, user: discord.Member, amount):
    print(f"***********************\nThe user {ctx.author.nick} has used !friend_donation command.\n-----")

    server = client.get_guild(848949680809574460)
    premium_member = discord.utils.get(server.roles, name="PremiumMember")

    if premium_member not in ctx.author.roles:
        embed = Embed(
            title=f"Feature denied!",
            description=f"Sorry {ctx.author.mention}!\nThis feature is for Premium Members only.\nYou can buy this title using !manage_account command.\nThank you for understanding!",
            colour=0xB9BDA3
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/861584178676236288/What-to-Do-When-YouE28099re-Denied-for-Life-Insurance.png")
        embed.set_footer(text=f"Date: {datetime.datetime.now()}")
        await ctx.send(embed=embed)
        print("Access denied to !myself command. Not a Premium Member.")
    else:
        from_id = ctx.author.id
        to_id = user.id

        try:
            # first, we check if the amount is <= the sold of the premium member
            if int(amount) <= account_management.check_balance(from_id):
                print("There is enough sold for the transfer.")
                # then we check if the user has an account, and if not, we create one
                if account_management.check_balance(to_id) == "No bank account":
                    if account_management.create_account(to_id, 0):
                        embed = Embed(
                            title=f"New account created",
                            description=f"Dear {ctx.author.mention}!\nWe create a new account for {user.mention} in order to receive the donation.\nThank you!",
                            colour=0xB9BDA3
                        )
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/attachments/849695979775328296/860791093141700618/HK-Bank-account.png")
                        embed.set_footer(text=f"Date: {datetime.datetime.now()}")
                        await ctx.send(embed=embed)
                        print(f"The account for {user.mention} was created.")
                    else:
                        print("Error in creating the account.")
                else:
                    pass
                # then we make the transfers
                account_management.donate(from_id, to_id, int(amount), "Premium Member donation")
                embed = Embed(
                    title=f"What a big heart!",
                    description=f"Dear {user.mention}!\nThe donation is done. Your account is now {int(amount)}lei bigger.\nThank you for your generosity, {ctx.author.mention}!\n\nP.S.This feature is for Premium Members only.",
                    colour=0xB9BDA3
                )
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/849695979775328296/861593762806759444/making-a-donation-min-scaled.png")
                embed.set_footer(text=f"Date: {datetime.datetime.now()}")
                await ctx.send(embed=embed)
                print("Donation done")
            else:
                embed = Embed(
                    title=f"Not enough money",
                    description=f"Dear {ctx.author.mention}!\nYou don't have enough money to make this donation to {user.mention}. Please use !manage_account command to refund your account first!\nThank you for understanding!\n\nP.S.This feature is for Premium Members only.",
                    colour=0xB9BDA3
                )
                embed.set_thumbnail(
                    url="https://cdn.discordapp.com/attachments/849695979775328296/860830985347137536/Monopoly-Man-Broke-Broke-Ass-Stuart1.png")
                embed.set_footer(text=f"Date: {datetime.datetime.now()}")
                await ctx.send(embed=embed)
                print("Not enough money for the donation.")

        except ValueError:
            # else:
            embed = Embed(
                title=f"Invalid format for amount",
                description=f"Dear {ctx.author.mention}!\nPlease write a valid amount meaning integer number (e.g. 155)!\nThank you!\n\nP.S.This feature is for Premium Members only.",
                colour=0xB9BDA3
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/849695979775328296/861597940920877066/6a00d834525fff69e201bb08887fa8970d-600wi.png")
            await ctx.send(embed=embed)
            print("Please write a valid amount meaning integer number (e.g. 155)")


@client.command()
async def weather(ctx, *, city: str):
    print(f"***********************\nThe user {ctx.author.nick} has used !weather command.\n-----")
    server = client.get_guild(848949680809574460)
    premium_member = discord.utils.get(server.roles, name="PremiumMember")

    if premium_member not in ctx.author.roles:
        embed = Embed(
            title=f"Feature denied!",
            description=f"Sorry {ctx.author.mention}!\nThis feature is for Premium Members only.\nYou can buy this title using !manage_account command.\nThank you for understanding!",
            colour=0xB9BDA3
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/861584178676236288/What-to-Do-When-YouE28099re-Denied-for-Life-Insurance.png")
        embed.set_footer(text=f"Date: {datetime.datetime.now()}")
        await ctx.send(embed=embed)
        print("Access denied to !weather command. Not a Premium Member.")
    else:
        # the output is displayed in #support-premium-members-only channel
        channel = client.get_channel(861587063726669844)
        channel_name = channel.name

        embed = Embed(
            title=f"Feature only for Premium Members!",
            description=f"For weather info, please see the #{channel_name} channel.\nThank you!",
            colour=0xB9BDA3
        )
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/849695979775328296/860541113835978793/Private-877x432.png")
        embed.set_footer(
            text=f"❗ This message will be deleted in 10sec.    |   Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
        send = await ctx.send(embed=embed)
        await asyncio.sleep(10)
        await ctx.message.delete()
        await send.delete()

        # then we get the info from base_url = "http://api.openweathermap.org/data/2.5/weather?"
        city_name = city
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name
        response = requests.get(complete_url)
        x = response.json()

        # we check if the city_name is a valid city
        if x["cod"] != "404":
            # we show that the bot is typing till the time that it fetches the contents from the website
            async with channel.typing():
                # then we get the info about the weather
                y = x["main"]
                current_temperature = y["temp"]
                current_temperature_celsiuis = str(round(current_temperature - 273.15))
                current_feels_like = y['feels_like']
                current_feels_like_celsiuis = str(round(current_feels_like - 273.15))
                current_pressure = y["pressure"]
                current_humidity = y["humidity"]
                z = x["weather"]
                weather_description = z[0]["description"]

            # then we put the info inside a discord.Embed
            weather_description = z[0]["description"]
            embed = discord.Embed(title=f"Weather in {city_name.capitalize()}",
                                  color=0x4489D5,
                                  timestamp=ctx.message.created_at)
            embed.add_field(name="Description", value=f"**{weather_description}**", inline=False)
            embed.add_field(name="Temperature(°C)", value=f"**{current_temperature_celsiuis}°C**")
            embed.add_field(name="Feels like(°C)", value=f"**{current_feels_like_celsiuis}°C**")
            embed.add_field(name="\u200b", value="\u200b")
            embed.add_field(name="Humidity(%)", value=f"**{current_humidity}%**")
            embed.add_field(name="Atmospheric Pressure(hPa)", value=f"**{current_pressure}hPa**")
            embed.add_field(name="\u200b", value="\u200b")
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/attachments/849695979775328296/862666410098556928/icon.png")
            embed.set_image(
                url="https://cdn.discordapp.com/attachments/849695979775328296/862661663400525844/3d1ce3fb1985505ba88e01e525a8f841.png")
            embed.set_author(
                name=ctx.author.nick,
                icon_url=ctx.author.avatar_url
            )
            embed.set_footer(text=f"❗Requested by a Premium Member: {ctx.author.name}")
            await channel.send(embed=embed)
        else:
            await channel.send(f"City {city_name} not found.")


@client.command()
async def review(ctx):
    print(f"***********************\nThe user {ctx.author.nick} has used !review command.\n-----")

    # first we verify if the user already give a rating
    last_feedback = reviews.get_last_feedback(ctx.author.id)
    print("\n")
    if last_feedback != "No review":
        # if yes, we show him the last feedback and ask him/her if an update is desired:
        # last_feedback = [ID, NICK, DATA, NO_OF_STARS, FEEDBACK]
        last_feedback_date = last_feedback[2]
        last_feedback_no_of_stars = int(last_feedback[3])
        last_feedback_feedback = last_feedback[4]
        embed = Embed(
            title=f"Re-rate your experience with us?",
            description=f"Hi there {ctx.author.mention}!\n\nYou already rate your experience with us:\nLast date: {last_feedback_date}\nNumber of given stars: {last_feedback_no_of_stars * '⭐'}\nFeedback: {last_feedback_feedback}\n\nDo you want to update your rating?\n(Choose 👍 for yes or 👎 for no)",
            colour=0x3DD330
        )

        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
        embed.set_thumbnail(url=trivia_logo_img)
        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

        try:
            map_answers = {
                "1": "👍",
                "2": "👎",
            }

            def check_react(reaction, user):
                if reaction.message.id != msg.id:
                    return False
                if user != ctx.message.author:
                    return False
                if str(reaction.emoji) not in map_answers.values():
                    return False
                return True

            reaction, user = await client.wait_for('reaction_add', check=check_react, timeout=30)

            if reaction.emoji == map_answers['1']:
                # re-write us a review
                embed = Embed(
                    title=f"Thank your for re-rating your experience with us!",
                    description=f"How are you enjoying now our Trivia Bot?\nSelect the emoji corresponding to the number of stars you would use to re-rate us.",
                    colour=0xB9BDA3
                )

                trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                embed.set_thumbnail(url=trivia_logo_img)
                embed.set_image(
                    url="https://cdn.discordapp.com/attachments/849695979775328296/863022255369879552/78aoxwp9b088du4rrj9t.png")
                embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")

                # This will make sure that the response will only be registered if the following conditions are met:
                def check(msg):
                    return msg.author == ctx.author and msg.content != "" and msg.channel == ctx.channel

                msg = await ctx.send(embed=embed)

                await msg.add_reaction("1️⃣")
                await msg.add_reaction("2️⃣")
                await msg.add_reaction("3️⃣")
                await msg.add_reaction("4️⃣")
                await msg.add_reaction("5️⃣")

                no_stars = 0
                feedback = "NULL"
                try:
                    map_answers = {
                        "1": "1️⃣",
                        "2": "2️⃣",
                        "3": "3️⃣",
                        "4": "4️⃣",
                        "5": "5️⃣",
                    }

                    def check_react(reaction, user):
                        if reaction.message.id != msg.id:
                            return False
                        if user != ctx.message.author:
                            return False
                        if str(reaction.emoji) not in map_answers.values():
                            return False
                        return True

                    reaction, user = await client.wait_for('reaction_add', check=check_react, timeout=30)

                    # we set two different messages depending on the rating (<=4 or 5)
                    embed_to_improve = Embed(
                        title=f"We would love your feedback!",
                        description=f"Dear {ctx.author.mention},\nPlease let us know your suggestions and ideas so that we can improve the Trivia Bot.\nThank your in advanced for your time & thoughts!",
                        colour=0xC14BC5
                    )
                    trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                    embed_to_improve.set_thumbnail(url=trivia_logo_img)
                    embed_to_improve.set_image(
                        url="https://cdn.discordapp.com/attachments/849695979775328296/863022837233221632/images.png")
                    embed_to_improve.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")

                    # message for 5* rating
                    embed_5_stars = Embed(
                        title=f"We would love your feedback!",
                        description=f"Dear {ctx.author.mention},\nThank your for the ⭐⭐⭐⭐⭐ rating.\nStill, we would love to read your ideas so that we can make even more awesomeness the Trivia Bot.\nThank your in advanced for your time & thoughts!",
                        colour=0xC14BC5
                    )
                    trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                    embed_5_stars.set_thumbnail(url=trivia_logo_img)
                    embed_5_stars.set_image(
                        url="https://cdn.discordapp.com/attachments/849695979775328296/863022837233221632/images.png")
                    embed_5_stars.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")

                    if reaction.emoji == map_answers['1']:
                        no_stars = 1
                        await ctx.send(embed=embed_to_improve)
                    elif reaction.emoji == map_answers['2']:
                        no_stars = 2
                        await ctx.send(embed=embed_to_improve)
                    elif reaction.emoji == map_answers['3']:
                        no_stars = 3
                        await ctx.send(embed=embed_to_improve)
                    elif reaction.emoji == map_answers['4']:
                        no_stars = 4
                        await ctx.send(embed=embed_to_improve)
                    elif reaction.emoji == map_answers['5']:
                        no_stars = 5
                        await ctx.send(embed=embed_5_stars)
                    else:
                        ctx.send("Invalid emoji!")

                    if no_stars != 0:
                        print(f"No of stars from {ctx.author.nick}: {no_stars}")
                        msg_feedback = await client.wait_for("message", check=check, timeout=30)
                        if msg_feedback.content:
                            feedback = msg_feedback.content
                        print(f"Feedback from {ctx.author.nick}: {feedback}")

                        # now we save the new feedback
                        reviews.save_feedback(ctx.author.id, ctx.author.nick, no_stars, feedback)
                        # we update the TriviaBot rating
                        rating_list = reviews.update_rating()
                        # rating_list = [UPDATED_DATE	NO_UNIQUE_FEEDBACKS	NO_TOTAL_STARS	AVG_RATING	NO_FULL_STARS	NO_HALF_STARS	NO_EMPTY_STAR]
                        # we send an embed message with the new updated rating
                        embed = Embed(
                            title=f"Thank your for re-rating 🙏",
                            description=f"{ctx.author.mention}, take a look to our updated rating score!\nThank you for your input!",
                            colour=0xC4C849
                        )
                        embed.add_field(
                            name=f"    {float(rating_list[3])}        {int(rating_list[4]) * '★'}{int(rating_list[5]) * '✭'}{int(rating_list[6]) * '✰'}",
                            value=f"RATING")
                        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                        embed.set_thumbnail(url=trivia_logo_img)
                        embed.set_image(
                            url="https://cdn.discordapp.com/attachments/849695979775328296/863372550524502026/unknown.png")
                        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
                        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                        await ctx.send(embed=embed)

                except asyncio.TimeoutError:
                    # if timeout error is from not getting feedback
                    if no_stars != 0:
                        print(f"Feedback from {ctx.author.nick}: {feedback}")
                        embed = Embed(
                            title=f"To slow in giving feedback!",
                            description=f"Dear {ctx.author.mention}!\nYour updated rating will be stored with no feedback message.\nThank you!",
                            colour=0xC8E538
                        )
                        slow_msg = await ctx.send(embed=embed)
                        await slow_msg.add_reaction("🐌")

                        # now we save the new feedback
                        reviews.save_feedback(ctx.author.id, ctx.author.nick, no_stars, feedback)
                        # we update the TriviaBot rating
                        rating_list = reviews.update_rating()
                        # rating_list = [UPDATED_DATE	NO_UNIQUE_FEEDBACKS	NO_TOTAL_STARS	AVG_RATING	NO_FULL_STARS	NO_HALF_STARS	NO_EMPTY_STAR]
                        # we send an embed message with the new updated rating
                        embed = Embed(
                            title=f"Thank your for re-rating 🙏",
                            description=f"{ctx.author.mention}, take a look to our updated rating score!\nThank you for your input!",
                            colour=0xC4C849
                        )
                        embed.add_field(
                            name=f"    {float(rating_list[3])}        {int(rating_list[4]) * '★'}{int(rating_list[5]) * '✭'}{int(rating_list[6]) * '✰'}",
                            value=f"RATING")
                        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                        embed.set_thumbnail(url=trivia_logo_img)
                        embed.set_image(
                            url="https://cdn.discordapp.com/attachments/849695979775328296/863372550524502026/unknown.png")
                        embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
                        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                        await ctx.send(embed=embed)

                    else:
                        # meaning that the user didn't chose a 1-5 emoji
                        embed = Embed(
                            title=f"Too SLOW!!!",
                            description=f"Be faster next time!\nTo rate us, please use again the !review command!\nThank you!",
                            colour=0xC8E538
                        )
                        slow_msg = await ctx.send(embed=embed)
                        await slow_msg.add_reaction("🐌")
                        print(f"No of stars from {ctx.author.nick}: {no_stars}")
                        print(f"Feedback from {ctx.author.nick}: {feedback}")

            elif reaction.emoji == map_answers['2']:
                print("No re-rate desire!")
                embed = Embed(
                    title=f"No re-rate 😊",
                    description=f"That's ok {ctx.author.mention}!\nWe'll keep in mind your last feedback. 😉\n Thank you!",
                    colour=0xC4C849
                )

                trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                embed.set_thumbnail(url=trivia_logo_img)
                embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                await ctx.send(embed=embed)
            else:
                ctx.send("Invalid emoji!")
                print("Invalid emoji!")

        except asyncio.TimeoutError:
            embed = Embed(
                title=f"Too SLOW!!!",
                description=f"Be faster next time!\nTo rate us, please use again the !review command!\nThank you!",
                colour=0xC8E538
            )
            slow_msg = await ctx.send(embed=embed)
            await slow_msg.add_reaction("🐌")
            print(f"No yes or no reaction to re-rate question!")
    else:
        # we get the first review:
        # Write us a review
        embed = Embed(
            title=f"Rate your experience with us!",
            description=f"How are you enjoying our Trivia Bot?\nSelect the emoji corresponding to the number of stars you would use to rate us.",
            colour=0xB9BDA3
        )

        trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
        embed.set_thumbnail(url=trivia_logo_img)
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/849695979775328296/863022255369879552/78aoxwp9b088du4rrj9t.png")
        embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")

        # This will make sure that the response will only be registered if the following conditions are met:
        def check(msg):
            return msg.author == ctx.author and msg.content != "" and msg.channel == ctx.channel

        msg = await ctx.send(embed=embed)

        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        await msg.add_reaction("3️⃣")
        await msg.add_reaction("4️⃣")
        await msg.add_reaction("5️⃣")

        no_stars = 0
        feedback = "NULL"
        try:
            map_answers = {
                "1": "1️⃣",
                "2": "2️⃣",
                "3": "3️⃣",
                "4": "4️⃣",
                "5": "5️⃣",
            }

            def check_react(reaction, user):
                if reaction.message.id != msg.id:
                    return False
                if user != ctx.message.author:
                    return False
                if str(reaction.emoji) not in map_answers.values():
                    return False
                return True

            reaction, user = await client.wait_for('reaction_add', check=check_react, timeout=30)

            # we set two different messages depending on the rating (<=4 or 5)
            embed_to_improve = Embed(
                title=f"We would love your feedback!",
                description=f"Dear {ctx.author.mention},\nPlease let us know your suggestions and ideas so that we can improve the Trivia Bot.\nThank your in advanced for your time & thoughts!",
                colour=0xC14BC5
            )
            trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
            embed_to_improve.set_thumbnail(url=trivia_logo_img)
            embed_to_improve.set_image(
                url="https://cdn.discordapp.com/attachments/849695979775328296/863022837233221632/images.png")
            embed_to_improve.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")

            # message for 5* rating
            embed_5_stars = Embed(
                title=f"We would love your feedback!",
                description=f"Dear {ctx.author.mention},\nThank your for the ⭐⭐⭐⭐⭐ rating.\nStill, we would love to read your ideas so that we can make even more awesomeness the Trivia Bot.\nThank your in advanced for your time & thoughts!",
                colour=0xC14BC5
            )
            trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
            embed_5_stars.set_thumbnail(url=trivia_logo_img)
            embed_5_stars.set_image(
                url="https://cdn.discordapp.com/attachments/849695979775328296/863022837233221632/images.png")
            embed_5_stars.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")

            if reaction.emoji == map_answers['1']:
                no_stars = 1
                await ctx.send(embed=embed_to_improve)
            elif reaction.emoji == map_answers['2']:
                no_stars = 2
                await ctx.send(embed=embed_to_improve)
            elif reaction.emoji == map_answers['3']:
                no_stars = 3
                await ctx.send(embed=embed_to_improve)
            elif reaction.emoji == map_answers['4']:
                no_stars = 4
                await ctx.send(embed=embed_to_improve)
            elif reaction.emoji == map_answers['5']:
                no_stars = 5
                await ctx.send(embed=embed_5_stars)
            else:
                ctx.send("Invalid emoji!")

            if no_stars != 0:
                print(f"No of stars from {ctx.author.nick}: {no_stars}")
                msg_feedback = await client.wait_for("message", check=check, timeout=30)
                if msg_feedback.content:
                    feedback = msg_feedback.content
                print(f"Feedback from {ctx.author.nick}: {feedback}")

                # now we save the feedback
                reviews.save_feedback(ctx.author.id, ctx.author.nick, no_stars, feedback)
                # we update the TriviaBot rating
                rating_list = reviews.update_rating()
                # rating_list = [UPDATED_DATE	NO_UNIQUE_FEEDBACKS	NO_TOTAL_STARS	AVG_RATING	NO_FULL_STARS	NO_HALF_STARS	NO_EMPTY_STAR]
                # we send an embed message with the new updated rating
                embed = Embed(
                    title=f"Thank your for rating your experience with us! 🙏",
                    description=f"{ctx.author.mention}, take a look to our updated rating score!\nThank you for your input!",
                    colour=0xC4C849
                )
                embed.add_field(
                    name=f"    {float(rating_list[3])}        {int(rating_list[4]) * '★'}{int(rating_list[5]) * '✭'}{int(rating_list[6]) * '✰'}",
                    value=f"RATING")
                trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                embed.set_thumbnail(url=trivia_logo_img)
                embed.set_image(
                    url="https://cdn.discordapp.com/attachments/849695979775328296/863372550524502026/unknown.png")
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
                embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                await ctx.send(embed=embed)

        except asyncio.TimeoutError:
            # if timeout error is from not getting feedback
            if no_stars != 0:
                print(f"Feedback from {ctx.author.nick}: {feedback}")
                embed = Embed(
                    title=f"To slow in giving feedback!",
                    description=f"Dear {ctx.author.mention}!\nYour new rating will be stored with no feedback message.\nThank you!",
                    colour=0xC8E538
                )
                slow_msg = await ctx.send(embed=embed)
                await slow_msg.add_reaction("🐌")

                # now we save the new feedback
                reviews.save_feedback(ctx.author.id, ctx.author.nick, no_stars, feedback)
                # we update the TriviaBot rating
                rating_list = reviews.update_rating()
                # rating_list = [UPDATED_DATE	NO_UNIQUE_FEEDBACKS	NO_TOTAL_STARS	AVG_RATING	NO_FULL_STARS	NO_HALF_STARS	NO_EMPTY_STAR]
                # we send an embed message with the new updated rating
                embed = Embed(
                    title=f"Thank your for rating your experience with us! 🙏",
                    description=f"{ctx.author.mention}, take a look to our updated rating score!\nThank you for your input!",
                    colour=0xC4C849
                )
                embed.add_field(
                    name=f"    {float(rating_list[3])}        {int(rating_list[4]) * '★'}{int(rating_list[5]) * '✭'}{int(rating_list[6]) * '✰'}",
                    value=f"RATING")
                trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
                embed.set_thumbnail(url=trivia_logo_img)
                embed.set_image(
                    url="https://cdn.discordapp.com/attachments/849695979775328296/863372550524502026/unknown.png")
                embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
                embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
                await ctx.send(embed=embed)

            else:
                # meaning that the user didn't choose a 1-5 emoji
                embed = Embed(
                    title=f"Too SLOW!!!",
                    description=f"Be faster next time!\nTo rate us, please use again the !review command!\nThank you!",
                    colour=0xC8E538
                )
                slow_msg = await ctx.send(embed=embed)
                await slow_msg.add_reaction("🐌")
                print(f"No of stars from {ctx.author.nick}: {no_stars}")
                print(f"Feedback from {ctx.author.nick}: {feedback}")


@client.command()
async def rating(ctx):
    print(f"***********************\nThe user {ctx.author.nick} has used !rating command.\n-----")

    # we update the TriviaBot rating score
    rating_list = reviews.update_rating()
    # rating_list = [UPDATED_DATE	NO_UNIQUE_FEEDBACKS	NO_TOTAL_STARS	AVG_RATING	NO_FULL_STARS	NO_HALF_STARS	NO_EMPTY_STAR]
    # we send an embed message with the new updated rating score
    embed = Embed(
        title=f"Trivia Bot updated rating score:",
        description=f"{float(rating_list[3])}        {int(rating_list[4]) * '★'}{int(rating_list[5]) * '✭'}{int(rating_list[6]) * '✰'}\n",
        colour=0x49C8A9
    )

    trivia_logo_img = "https://cdn.discordapp.com/attachments/849695979775328296/860455206521143306/trivia_logo.png"
    embed.set_thumbnail(url=trivia_logo_img)
    embed.set_image(
        url="https://cdn.discordapp.com/attachments/849695979775328296/863372550524502026/unknown.png")
    embed.set_author(name=f"{ctx.author.name}", icon_url=ctx.author.avatar_url)
    embed.set_footer(text=f"Date: {datetime.datetime.now().strftime('%d/%m/%y %H-%M-%S')}")
    await ctx.send(embed=embed)


client.run(TOKEN)
