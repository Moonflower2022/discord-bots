import discord
from base import bot
from utils import (
    handle_string_check,
    get_count_summary,
    get_emoji_summary,
    plot_histogram
)
from collections import defaultdict

@bot.command()
async def count(ctx, *, string):
    """count string"""

    if await handle_string_check(ctx, string) == -1:
        return

    count = 0
    checked_messages = 0

    async for message in ctx.channel.history(limit=None):
        checked_messages += 1
        # Check if the message contains the string
        if string in message.content.lower():
            count += 1

    await ctx.send(get_count_summary(count, string, checked_messages))

@bot.command()
async def count_emojis(ctx, *, string):
    """count string and generate reactions summary"""

    if await handle_string_check(ctx, string) == -1:
        return

    count = 0
    emoji_data = {}
    checked_messages = 0

    async for message in ctx.channel.history(limit=None):
        checked_messages += 1
        # Check if the message contains the string
        if string in message.content.lower():
            count += 1

            # Check reactions on this message
            for reaction in message.reactions:
                if reaction.emoji in emoji_data:
                    emoji_data[reaction.emoji] += reaction.count
                else:
                    emoji_data[reaction.emoji] = reaction.count

    # Generate summary
    summary = get_emoji_summary(count, string, checked_messages, emoji_data)

    # Send the summary
    await ctx.send(summary)

@bot.command()
async def plot(ctx, *, string):
    if await handle_string_check(ctx, string) == -1:
        return

    """count string and generate chat frequency histogram by hour."""
    count = 0
    hourly_frequency = defaultdict(int)  # Track message counts by hour
    checked_messages = 0
    async for message in ctx.channel.history(limit=None):
        checked_messages += 1
        # Check if the message contains the string
        if string in message.content.lower():
            count += 1

            # Track message frequency by date and hour
            message_time = message.created_at.replace(minute=0, second=0, microsecond=0)  # Round to the nearest hour
            hourly_frequency[message_time] += 1
    print(f"checked {checked_messages} messages")
    # Plot histogram by hour
    buffer = plot_histogram(hourly_frequency, string)

    # Send the histogram as an image
    file = discord.File(fp=buffer, filename='chat_frequency_by_hour.png')
    await ctx.send(file=file)