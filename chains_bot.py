# Import the required modules
from base import bot
import discord
from discord.ext.commands import Bot
import asyncio
from utils import get_regional_indicator_emoji

# Set the confirmation message when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

def created_chain(messages, bot, only_self=False):
    if len(messages) < 2:
        return False

    if messages[0].content == messages[1].content and messages[1].author != bot.user and messages[0].author != bot.user:
        return not only_self or messages[0].author == messages[1].author
    
    if len(messages) >= 3 and messages[0].content == messages[2].content and messages[1].author == bot.user:
        return not only_self or messages[0].author == messages[2].author
    
    return False


def broke_chain(messages, bot):
    if len(messages) < 2:
        return False
    
    if messages[0].content != messages[1].content and messages[1].author != bot.user and messages[0].author != bot.user:
        return True
    
    if len(messages) >= 3 and messages[0].content != messages[2].content and messages[1].author == bot.user:
        return True
    
    return False


async def attempt_timeout(user, duration, reason):
    try:
        await user.timeout(duration, reason=reason)
    except:
        print(f"something went wrong when timeouting '{user}' for reason '{reason}'")

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()
    TOKEN = os.getenv("INCONSPICUOUS_TOKEN")

    bot.run(TOKEN)
