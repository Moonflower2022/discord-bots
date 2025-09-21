#!/Library/Frameworks/Python.framework/Versions/3.13/bin/python3

from base import bot, on_ready
import re
import random
import setproctitle
import time

setproctitle.setproctitle("memer_bot")

meme_reviews = [
    "This meme cleverly plays with current events and is quite relatable. I appreciate the creativity behind it. 8/10",
    "While the concept is good, it feels a bit overdone. A fresh take would elevate it further. 7/10",
    "The humor in this meme is spot on! It really captures the absurdity of the situation. 9/10",
    "The image choice is excellent, but the caption could use some work. Still, it's a solid meme. 8/10",
    "This meme is hilarious and perfectly timed! It made me laugh out loud. 10/10",
    "A nice blend of humor and social commentary, though it might not resonate with everyone. 8/10",
    "I found the punchline a bit predictable. A twist would have made it more engaging. 7/10",
    "Visually appealing and very relatable! This one is definitely a keeper. 9/10",
    "The execution is good, but it lacks the edge that makes a meme truly memorable. 7/10",
    "This meme hits hard with its humor and relevance. Well done! 9/10",
    "The use of pop culture references works well here. I enjoyed it! 8/10",
    "Funny and impactful, but it could have been even better with a different format. 8/10",
    "This is a classic example of meme magic! It made my day. 10/10",
    "While the idea is interesting, the delivery feels a bit flat. 7/10",
    "An excellent example of clever wordplay combined with visuals. Very entertaining! 9/10",
    "The meme is relatable and well-structured, but I’ve seen similar themes recently. 8/10",
    "This one really speaks to the current generation! Great job! 10/10",
    "I appreciate the effort, but the humor didn't quite land for me. 7/10",
    "A bold statement wrapped in humor, and it works well! 9/10",
    "While it’s funny, I feel like it’s missing that extra punch. 8/10",
    "This meme resonates with many and captures the essence of the moment beautifully. 9/10",
    "A clever twist on a common theme. Very well executed! 8/10",
    "Not the funniest meme I've seen, but it has its charm. 7/10",
    "This meme brings a smile and a bit of wisdom. Well done! 9/10",
    "A good attempt at humor, but it feels a bit forced. 7/10",
    "I love the creativity in the visuals! It adds a lot to the humor. 10/10",
    "This meme is a perfect blend of irony and comedy. Great work! 9/10",
    "A bit cliché, but it still made me chuckle. 8/10",
    "The concept is fresh and the execution is fantastic! 10/10",
    "I didn’t find it particularly funny, but the effort is clear. 7/10",
    "A solid entry with clever references and good humor. 8/10",
    "This meme perfectly captures the struggle we all face. I love it! 9/10",
    "While the punchline is weak, the meme itself is visually appealing. 7/10",
    "I really like the angle you took with this one. Very unique! 10/10",
    "It’s okay, but it feels like it’s trying too hard. 7/10",
    "The message is clear, and the humor is very relatable. 9/10",
    "Great timing and execution! This meme made me laugh. 10/10",
    "While it’s funny, I feel like it’s not quite original enough. 8/10",
    "This one made me think and laugh at the same time. A great combo! 9/10",
    "The humor didn't resonate with me, but I can see why others might enjoy it. 7/10",
    "A delightful take on a well-known theme. Very enjoyable! 8/10",
    "This meme is a work of art! The creativity shines through. 10/10",
    "The execution could be better, but it's still an enjoyable meme. 8/10",
    "I love the unexpected twist at the end! Great job! 9/10",
    "This one didn't hit the mark for me, but I appreciate the effort. 7/10"
]

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "modern" in message.content or "Modern" in message.content:
        await message.reply("modern :fire:", mention_author=True)
    
    print(f"{message.author} in '{message.channel.guild}':", message.content)

    daily_meme_pattern = r"^[Dd]aily [Mm]eme.*$"
    if re.match(daily_meme_pattern, str(message.content)):
        await message.reply(random.choice(meme_reviews), mention_author=True)

    await bot.process_commands(message)

from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("MEMER_TOKEN")

time.sleep(60)

bot.run(TOKEN)