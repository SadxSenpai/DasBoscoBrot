from email import message
from lib2to3.pgen2.literals import simple_escapes
import pathlib
import shutil
from telnetlib import theNULL
from tkinter import FIRST
import pdf2image
import requests
import json
import inspect
import sys
import discord
import re
import io
import datetime
import os
import gdown
import time
import tempfile
import asyncio
import datetime

from pathlib import Path
from discord.ext import tasks, commands
from PIL import Image
from colorama import Fore, Style
from pdf2image import convert_from_path, convert_from_bytes

# Make sure that the user is running Python 3.8 or higher
if sys.version_info < (3, 8):
    exit("Python 3.8 or higher is required to run this bot!")

# Now make sure that the discord.py library is installed or/and is up to date
try:
    from discord import app_commands, Intents, Client, Interaction
except ImportError:
    exit(
        "Either discord.py is not installed or you are running an older and unsupported version of it."
        "Please make sure to check that you have the latest version of discord.py! (try reinstalling the requirements?)"
    )

# inspect.cleandoc() is used to remove the indentation from the message
# when using triple quotes (makes the code much cleaner)
# Typicly developers woudln't use cleandoc rather they move the text
# all the way to the left
print(inspect.cleandoc(f"""
    Hey, welcome to the active developer badge bot.
    Please enter your bot's token below to continue.

    {Style.DIM}Don't close this application after entering the token
    You may close it after the bot has been invited and the command has been ran{Style.RESET_ALL}
"""))

# Try except block is useful for when you'd like to capture errors
try:
    with open("config.json") as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # You can in theory also do "except:" or "except Exception:", but it is not recommended
    # unless you want to suppress all errors
    config = {}


while True:
    # If no token is stored in "config" the value defaults to None
    token = config.get("token", None)
    if token:
        print(f"\n--- Detected token in {Fore.GREEN}./config.json{Fore.RESET} (saved from a previous run). Using stored token. ---\n")
    else:
        # Take input from the user if no token is detected
        token = input("> ")

    # Validates if the token you provided was correct or not
    # There is also another one called aiohttp.ClientSession() which is asynchronous
    # However for such simplicity, it is not worth playing around with async
    # and await keywords outside of the event loop
    try:
        data = requests.get("https://discord.com/api/v10/users/@me", headers={
            "Authorization": f"Bot {token}"
        }).json()
    except requests.exceptions.RequestException as e:
        if e.__class__ == requests.exceptions.ConnectionError:
            exit(f"{Fore.RED}ConnectionError{Fore.RESET}: Discord is commonly blocked on public networks, please make sure discord.com is reachable!")

        elif e.__class__ == requests.exceptions.Timeout:
            exit(f"{Fore.RED}Timeout{Fore.RESET}: Connection to Discord's API has timed out (possibly being rate limited?)")

        # Tells python to quit, along with printing some info on the error that occured
        exit(f"Unknown error has occurred! Additional info:\n{e}")

    # If the token is correct, it will continue the code
    if data.get("id", None):
        break  # Breaks out of the while loop

    # If the token is incorrect, an error will be printed
    # You will then be asked to enter a token again (while Loop)
    print(f"\nSeems like you entered an {Fore.RED}invalid token{Fore.RESET}. Please enter a valid token (see Github repo for help).")

    # Resets the config so that it doesn't use the previous token again
    config.clear()


# This is used to save the token for the next time you run the bot
with open("config.json", "w") as f:
    # Check if 'token' key exists in the config.json file
    config["token"] = token

    # This dumps our working setting to the config.json file
    # Indent is used to make the file look nice and clean
    # If you don't want to indent, you can remove the indent=2 from code
    json.dump(config, f, indent=2)


class BoscoBot(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """ This is called when the bot boots, to setup the global commands """
        await self.tree.sync()

# Variable to store the bot class and interact with it
client = BoscoBot(intents=Intents.default())
    
#when the bot is ready, print a message in the console
@client.event
async def on_ready():
    """ This is called when the bot is ready and has a connection with Discord
        It also prints out the bot's invite URL that automatically uses your
        Client ID to make sure you invite the correct bot with correct scopes.
    """
    print(inspect.cleandoc(f"""
        Logged in as {client.user} (ID: {client.user.id})

        Use this URL to invite {client.user} to your server:
        {Fore.LIGHTBLUE_EX}https://discord.com/api/oauth2/authorize?client_id={client.user.id}&scope=applications.commands%20bot{Fore.RESET}
    """), end="\n\n")
    
    print("Ready!")
    pdf_loop.start()
    
@tasks.loop(hours=168)
async def pdf_loop():

    #delte exiting the contents of the folder Speiseplan
    folder = 'Speiseplan'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path) 
                print(f"> {Style.BRIGHT}{filename}{Style.RESET_ALL} deleted")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    
    #download the pdf from google drive with gdown
    print(f"> downloading pdfs from google drive")
    url = "https://drive.google.com/drive/folders/1WB5lNSE901jWigIAk0dgxKIG-ljaSzQO"
    gdown.download_folder(url, quiet=True, use_cookies=False)
    print(f"> pdfs downloaded")
    
    #wait 5 seconds
    print(f"> waiting 5 seconds")
    time.sleep(5)

    #rename the pdf files inside the folder Speiseplan
    counter = 1
    for filename in os.listdir('Speiseplan'):
        if filename.endswith('.pdf'):
            os.rename(f'Speiseplan/{filename}', f'Speiseplan/file' + str(counter) + '.pdf')
            counter += 1
            print(f"> {Style.BRIGHT}{filename}{Style.RESET_ALL} renamed")
    
    #convert all pdf files  to an image
    popplerpath = r'C:\Program Files\poppler-23.08.0\Library\bin'
    
    counter = 1
    for filename in os.listdir('Speiseplan'):
        if filename.endswith('.pdf'):
            pages = convert_from_path(f'Speiseplan/{filename}', 500, poppler_path=popplerpath,first_page=1, last_page=1)
            for page in pages:
                page.save('Speiseplan/essen' + str(counter) +'.jpg', 'JPEG')
                counter += 1
                print(f"> {Style.BRIGHT}{filename}{Style.RESET_ALL} converted to image")
                time.sleep(2)
                
    print('sending weekly message...')
    channel = client.get_channel(902414002980782110)
    
    #send all .jpg files in the folder Speiseplan
    for filename in os.listdir('Speiseplan'):
        if filename.endswith('.jpg'):
            file = discord.File(f'Speiseplan/{filename}')
            await channel.send(file=file)
            print(f"> {Style.BRIGHT}{filename}{Style.RESET_ALL} sent")
            time.sleep(2)

@client.tree.command()
async def hello(interaction: Interaction):
    # Responds in the console that the command has been ran
    print(f"> {Style.BRIGHT}{interaction.user}{Style.RESET_ALL} used the command.")

    # Then responds in the channel with this message
    await interaction.response.send_message(inspect.cleandoc(f"""
        Hi **{interaction.user}**, thank you for saying hello to me.
    """))


# Runs the bot with the token you provided
client.run(token)

