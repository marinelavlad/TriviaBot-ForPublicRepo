import gspread
from oauth2client.service_account import ServiceAccountCredentials
from discord.ext import commands
import discord

# google sheet creds
scope = ['https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name("botpackage/client_secrets.json", scope)
google_client = gspread.authorize(creds)


# bot token
token_file = open("bot_secrets", "r")
TOKEN = token_file.read()
token_file.close()
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix="!", case_insensitive=True, intents=intents)

def login(user, password):
    auth_bot = google_client.open("TriviaBot").worksheet("auth")
    users_list = auth_bot.col_values(1)

    if user in users_list:
        # getting the user's row:
        for i in range(0, len(users_list)):
            if user == users_list[i]:
                row = i + 1
                break

        # verifying the password:
        if password == auth_bot.cell(row, 2).value:
            print(f"Welcome back {user}!")
            return f"Welcome back {user}!"
        else:
            print("Incorrect password! Try again.")
            return "Incorrect password!"

    else:
        print(f"Wrong user {user}! Try again.")
        return "Wrong user!"



def sign_up(user, password, email, nickname):
    auth_bot = google_client.open("TriviaBot").worksheet("auth")
    users_list = auth_bot.col_values(1)

    # verifying if the user is unique
    if user in users_list:
        print(f"The user {user} already exists! Try login function!")
        return "The user already exists! Try login function!"
    else:
        # verifying that the password has minimum 3 characters and no spaces
        if len(password) < 3 and " " in password:
            print("The password must have minimum 3 characters and no spaces!")
            return "The password must have minimum 3 characters and no spaces!"
        elif len(password) < 3:
            print("The password must have minimum 3 characters!")
            return "The password must have minimum 3 characters!"
        elif " " in password:
            print("The password must have no spaces!")
            return "The password must have no spaces!"
        else:
            #if the password has minimum 3 characters and no spaces, the new user is saved in data_base(g spread)
            auth_bot.insert_row([user, password, "Player", email, nickname, "no", "no"], len(users_list) + 1)
            print(f"The new account for the user {user} was successfully created!\nThe 'Player' role was assigned.")
            return f"The new account for the user {user} was successfully created!\nThe 'Player' role was assigned."