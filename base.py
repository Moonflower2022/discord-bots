import discord
from discord.ext.commands import Bot
import random

# Create a Discord bot instance and set the command prefix
intents = discord.Intents.all()
bot = Bot(command_prefix=".", intents=intents)


# Set the confirmation message when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

# Set the commands for your bot
@bot.command()
async def greet(ctx):
    """say hi!"""
    responses = [
        f"Hello {ctx.message.author}, I am an inconspicuous discord bot.",
        "Hi!",
        "One, two, three, uh! \nMy ba",
        "by don't mess around\nBecause she loves m",
        "e so\nAnd this I know this fo sho (uh)",
        "Greetings traveller: what business do you bring here?",
        "Bro whass good",
        "Hi Herbert",
        "ars",
        "hey bro hows it going",
        "Hello there!",
        "Hey! How's it going?",
        "Howdy",
        "Yo",
        "Heyo",
        "Hey! Long time no see my chummy chum chum pal friendo amigo bestie chum!",
        "Ahoy!",
        "Hi, how's everything?",
        "Hey there! Need help?",
        "Greetings and salutations!",
        "Hi, what's going on?",
        "Good day!",
        "Good morning!",
        "Good afternoon!",
        "Good evening!",
        "honk *im a dogcow*",
    ]

    response = random.choice(responses)
    await ctx.send(response)