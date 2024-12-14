import discord
from base import bot
from utils import (
    temp_message,
    generate_robot_voice,
    handle_string_check
)
import os
import asyncio

# Command to join the voice channel and play the TTS audio
@bot.command()
async def speak(ctx, *, text):
    """joins your voice chat and tts' the input text"""

    await ctx.message.delete()

    if await handle_string_check(ctx, text) == -1:
        return

    if ctx.author.voice:  # Check if the user is in a voice channel
        channel = ctx.author.voice.channel

        # Connect to the voice channel
        if not ctx.voice_client:  # If bot is not already in a voice channel
            voice_client = await channel.connect()
        else:
            voice_client = ctx.voice_client

        # Generate the MP3 file from the input text
        filename = "robot_voice.mp3"
        generate_robot_voice(text, filename)

        # Manually load Opus if not already loaded
        if not discord.opus.is_loaded():
            discord.opus.load_opus(
                "/opt/homebrew/lib/libopus.dylib"
            )  # Path to Opus library

        if voice_client.is_playing():
            await temp_message(
                ctx, "I am already speaking! Please wait until I finish.", 1
            )
            return

        # Play the MP3 file in the voice channel
        if os.path.isfile(filename):
            voice_client.play(
                discord.FFmpegPCMAudio(executable="ffmpeg", source=filename)
            )
            await temp_message(ctx, f"Playing '{text}' in the voice channel.", 1)

        # Wait for the audio to finish before disconnecting
        while voice_client.is_playing():
            await asyncio.sleep(1)  # Wait 1 second between checks

        # Disconnect from the voice channel after finishing
        await voice_client.disconnect()
    else:
        await temp_message(
            ctx, "You need to be in a voice channel for me to join and speak!", 1
        )


# Command to join a voice channel and play an uploaded MP3 file
@bot.command()
async def play(ctx):
    """plays attached mp3 file"""
    if ctx.author.voice:  # Check if the user is in a voice channel
        channel = ctx.author.voice.channel

        # Connect to the voice channel
        if not ctx.voice_client:  # If bot is not already in a voice channel
            voice_client = await channel.connect()
        else:
            voice_client = ctx.voice_client

        # Check if the bot is already playing audio
        if voice_client.is_playing():
            await temp_message(
                ctx, "I am already speaking! Please wait until I finish.", 0
            )
            return

        # Check if the user has attached a file
        if len(ctx.message.attachments) > 0:
            # Get the first attachment (assuming one file is uploaded)
            attachment = ctx.message.attachments[0]

            # Save the file locally
            file_path = f"temp_{attachment.filename}"
            await attachment.save(file_path)

            # Check if the uploaded file is an MP3
            if not file_path.endswith(".mp3"):
                os.remove(file_path)
                await temp_message(ctx, "Please upload an MP3 file.", 1)
                return

            # Play the MP3 file in the voice channel
            if os.path.isfile(file_path):
                voice_client.play(
                    discord.FFmpegPCMAudio(executable="ffmpeg", source=file_path)
                )
                await temp_message(
                    ctx, f"Playing '{attachment.filename}' in the voice channel.", 1
                )

                # Wait for the audio to finish before disconnecting
                while voice_client.is_playing():
                    await asyncio.sleep(1)  # Wait 1 second between checks

                # Disconnect from the voice channel after finishing
                await voice_client.disconnect()

                # Clean up the local file
                os.remove(file_path)
        else:
            await temp_message(ctx, "Please upload an MP3 file with your command.", 1)
    else:
        await temp_message(
            ctx, "You need to be in a voice channel for me to join and play!", 1
        )


# Command to make the bot leave the voice channel
@bot.command()
async def leave(ctx):
    """makes the me leave all voice channels"""
    await ctx.message.delete()
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await temp_message(ctx, "Disconnected from the voice channel.", 1)
    else:
        await temp_message(ctx, "I'm not in a voice channel.", 1)