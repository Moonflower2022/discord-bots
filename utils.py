import asyncio
from gtts import gTTS
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable, get_cmap
import io
import numpy as np

async def handle_string_check(ctx, string):
    if string == "":
        await temp_message(ctx, "Input is nothing!", 1)
        return -1
    else:
        return 0
    
async def temp_message(ctx, message_text, time=1):
    # Send the message
    message = await ctx.send(message_text)

    # Wait for 0.5 seconds
    await asyncio.sleep(time)

    # Delete the message
    await message.delete()

def get_count_summary(count, string, limit):
    # Send a summary
    summary = f"Found {count} occurences of '{string}' in the last {limit} messages.\n"
    return summary


def get_emoji_summary(count, string, limit, emoji_data):
    summary = get_count_summary(count, string, limit)
    if emoji_data:
        summary += "Emoji reactions on these messages:\n"
        for emoji, count in emoji_data.items():
            summary += f"{emoji} - {count} times\n"
    else:
        summary += "Unfortunately, there were no emojis found on the messages.\n"
    return summary


# Function to generate a robotic voice from text and save it as an MP3
def generate_robot_voice(text, filename="robot_voice.mp3"):
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(filename)


def get_regional_indicator_emoji(letter):
    if len(letter) != 1 or not letter.isalpha():
        raise ValueError("Input must be a single alphabetic character.")

    letter = letter.upper()

    unicode_offset = ord("A")
    regional_indicator_offset = 0x1F1E6

    regional_indicator_code = regional_indicator_offset + (ord(letter) - unicode_offset)

    return chr(regional_indicator_code)  # fr"\U{regional_indicator_code:08x}".upper()


def plot_histogram(hourly_frequency, string):
    fig, ax = plt.subplots(figsize=(12, 6))  # Explicitly create a figure and axes
    
    # Convert hour keys to sorted list of (hour, count) tuples
    hour_counts = sorted(hourly_frequency.items())
    x = [entry[0] for entry in hour_counts]  # Extract hours (date + hour)
    y = [entry[1] for entry in hour_counts]  # Extract counts

    # Normalize counts for color mapping
    norm = Normalize(vmin=min(y), vmax=max(y))  # Normalize based on the counts
    cmap = get_cmap('coolwarm')  # Choose a colormap (can be changed as desired)
    colors = cmap(norm(y))  # Map counts to colors

    # Formatting x-axis labels for readability
    x_labels = [f'{dt.strftime("%Y-%m-%d %H:00")}' for dt in x]

    # Plot the bars with varying colors
    ax.bar(x_labels, y, color=colors, edgecolor='black')
    ax.set_xlabel('Date and Hour')
    ax.set_ylabel(f'Number of messages containing "{string}"')
    ax.set_title(f'Chat frequency for "{string}" by hour')
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=45, ha='right')
    plt.tight_layout()

    # Add a color bar to show the range of counts
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # Only needed for color bar
    plt.colorbar(sm, ax=ax, label='Message Count')  # Associate colorbar with `ax`

    # Save plot to a file-like object
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    return buffer
