#!/Library/Frameworks/Python.framework/Versions/3.13/bin/python3

import random
from utils import get_regional_indicator_emoji, temp_message
from datetime import timedelta
from base import bot
from voice import speak, leave, play
from count import count, count_emojis, plot
from chains_bot import created_chain, broke_chain, attempt_timeout
import re

# def ars(string):
#     new_string = ""
#     last_char = ""
#     for i, char in enumerate(string):
#         if char == "a" and (last_char != "a" or i == 0):
#             new_string += "*"
#         if last_char == "a" and char != "a":
#             new_string += "*"
#         new_string += char if char != "a" else "ars"
#         if char == "a" and i == len(string) - 1:
#             new_string += "*"
#         last_char = char
#     return new_string

# def ars(string):
#     return string.replace("a", "*ars*").replace("**", "")

def ars(string):
    parts = re.split(r'(?<!\\)\*', string)  # Split on * unless preceded by \
    for i in range(len(parts)):
        parts[i] = parts[i].replace("a", "ars" if i % 2 else "*ars*")
    return "*".join(parts).replace("**", "")

def highlight_ars(string):
    parts = re.split(r'(?<!\\)\*', string)  # Split on * unless preceded by \
    for i in range(len(parts)):
        parts[i] = parts[i].replace("ars", "ars" if i % 2 else "*ars*")
    return "*".join(parts).replace("**", "")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def arsify(ctx, *, string):
    if "a" in string:
        await ctx.reply(ars("translated: " + string))
    else:
        error_message = "not reallll your message did not have any a's"
        await ctx.reply(error_message)
        await ctx.send(ars(error_message))

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

    black_list = ["Goozy Twozy Electric Boogaloozy", "Baked Beans on Toast"]

    if (
        not str(message.channel.guild) in black_list 
        and (
            not str(message.channel.guild) == "jj" 
            or str(message.channel) == "bot-testing"
        )
        and not str(message.channel) == "the-inconspicuous-channel"
    ):
        await handle_chains(message, bot)

    if message.author != bot.user:
        if str(message.channel.guild) == "ars" and "a" in message.content and random.random() < 0.2:
            await message.reply(ars("translated: " + message.content), mention_author=True)
        if "ars" in message.content and "ars" != message.content:
            await message.reply("no wya did you just say " + highlight_ars(message.content), mention_author=True)

    await bot.process_commands(message)

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("INCONSPICUOUS_TOKEN")

# Retrieve token from the .env file
bot.run(TOKEN)
