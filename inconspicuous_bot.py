import random
from utils import get_regional_indicator_emoji, temp_message
from datetime import timedelta
from base import bot, on_ready
from voice import speak, leave, play
from count import count, count_emojis, plot
from chains import created_chain, broke_chain, attempt_timeout


async def handle_chains(message, bot):
    channel = message.channel
    messages = [message async for message in channel.history(limit=3)]

    timeout_duration = timedelta(minutes=5)

    if str(message.channel) == "sra":
        if created_chain(messages, bot):
            reason = "bad! started chain"
            await attempt_timeout(message.author, timeout_duration, reason)
            await temp_message(message.channel, reason)
    else:
        if broke_chain(messages, bot):
            reason = "bad! broke chain"
            await attempt_timeout(message.author, timeout_duration, reason)
            await temp_message(message.channel, reason)
        elif created_chain(messages, bot, only_self=True):
            reason = "bad! created self chain"
            await attempt_timeout(message.author, timeout_duration, reason)
            await temp_message(message.channel, reason)


@bot.event
async def on_message(message):
    print(f"{message.author} in '{message.channel.guild}':", message.content)

    sra_chance = 0.1

    if message.content == "ars":
        word = "sra" if random.random() < sra_chance else "ars"
        for letter in list(word):
            await message.add_reaction(get_regional_indicator_emoji(letter))

    white_list = ["Goozy Twozy Electric Boogaloozy", "Baked Beans on Toast"]

    if (
        not str(message.channel.guild) in white_list 
        and (
            not str(message.channel.guild) == "jj" 
            or str(message.channel) == "bot-testing"
        )
        and not str(message.channel) == "the-inconspicuous-channel"
    ):
        await handle_chains(message, bot)

    await bot.process_commands(message)

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("INCONSPICUOUS_TOKEN")

# Retrieve token from the .env file
bot.run(TOKEN)
