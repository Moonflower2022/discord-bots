#!/Library/Frameworks/Python.framework/Versions/3.13/bin/python3

from base import bot
import discord
from discord.ext import commands, tasks

# Remove the default help command so we can use our custom one
bot.remove_command('help')

import setproctitle
import time
import json
import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Set

setproctitle.setproctitle("connector")

# Configuration
GROUPING_INTERVAL_DAYS = 7  # Weekly groupings (configurable)
GROUPING_TIME_HOUR = 10     # 10 AM (configurable)
DATA_FILE = "connector_data.json"
PAST_GROUPINGS_DIR = "past_groupings"

# Ensure past_groupings directory exists
os.makedirs(PAST_GROUPINGS_DIR, exist_ok=True)

class OneOnOneManager:
    def __init__(self):
        self.signups: Set[int] = set()  # User IDs who signed up
        self.load_data()
    
    def load_data(self):
        """Load signup data from JSON file"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.signups = set(data.get('signups', []))
        except Exception as e:
            print(f"Error loading data: {e}")
            self.signups = set()
    
    async def save_data(self, bot_instance=None):
        """Save signup data to JSON file with user details"""
        try:
            # Create user details if bot instance is available
            user_details = {}
            if bot_instance:
                for user_id in self.signups:
                    try:
                        user = await bot_instance.fetch_user(user_id)
                        user_details[str(user_id)] = {
                            'username': user.name,
                            'display_name': user.display_name,
                            'global_name': user.global_name
                        }
                    except Exception as e:
                        print(f"Could not fetch user {user_id}: {e}")
                        user_details[str(user_id)] = {
                            'username': 'Unknown',
                            'display_name': 'Unknown',
                            'global_name': 'Unknown'
                        }
            
            data = {
                'signups': list(self.signups),
                'user_details': user_details,
                'last_updated': datetime.now().isoformat()
            }
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    async def add_user(self, user_id: int, bot_instance=None) -> bool:
        """Add user to signup list. Returns True if newly added, False if already signed up"""
        if user_id in self.signups:
            return False
        self.signups.add(user_id)
        await self.save_data(bot_instance)
        return True
    
    async def remove_user(self, user_id: int, bot_instance=None) -> bool:
        """Remove user from signup list. Returns True if removed, False if not in list"""
        if user_id not in self.signups:
            return False
        self.signups.remove(user_id)
        await self.save_data(bot_instance)
        return True
    
    def get_signups(self) -> List[int]:
        """Get list of signed up user IDs"""
        return list(self.signups)
    
    def create_groupings(self) -> List[List[int]]:
        """Create random groupings from signup list"""
        if len(self.signups) < 2:
            return []
        
        users = list(self.signups)
        random.shuffle(users)
        
        groupings = []
        
        # Create pairs
        for i in range(0, len(users) - 1, 2):
            groupings.append([users[i], users[i + 1]])
        
        # If odd number, add the last person to the last group (making it a group of 3)
        if len(users) % 2 == 1:
            if groupings:
                groupings[-1].append(users[-1])
            else:
                # Edge case: only 1 person signed up
                groupings.append([users[-1]])
        
        return groupings
    
    async def save_groupings(self, groupings: List[List[int]], guild_id: int, bot_instance=None):
        """Save groupings to past_groupings directory with user details"""
        timestamp = datetime.now()
        filename = f"groupings_{guild_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(PAST_GROUPINGS_DIR, filename)
        
        # Create user details for all participants
        user_details = {}
        all_participants = [user_id for group in groupings for user_id in group]
        
        if bot_instance:
            for user_id in all_participants:
                try:
                    user = await bot_instance.fetch_user(user_id)
                    user_details[str(user_id)] = {
                        'username': user.name,
                        'display_name': user.display_name,
                        'global_name': user.global_name
                    }
                except Exception as e:
                    print(f"Could not fetch user {user_id}: {e}")
                    user_details[str(user_id)] = {
                        'username': 'Unknown',
                        'display_name': 'Unknown',
                        'global_name': 'Unknown'
                    }
        
        grouping_data = {
            'timestamp': timestamp.isoformat(),
            'guild_id': guild_id,
            'groupings': groupings,
            'user_details': user_details,
            'total_participants': sum(len(group) for group in groupings)
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(grouping_data, f, indent=2)
            return filepath
        except Exception as e:
            print(f"Error saving groupings: {e}")
            return None

# Initialize the manager
one_on_one_manager = OneOnOneManager()

def get_next_grouping_time():
    """Calculate the next automatic grouping time"""
    now = datetime.now()
    
    # Find next sunday at the specified hour
    days_until_sunday = (7 - now.weekday()) % 7
    if days_until_sunday == 1:  # Today is sunday
        # Check if we've already passed the grouping hour today
        if now.hour >= GROUPING_TIME_HOUR:
            days_until_sunday = 7  # Next sunday
    
    next_grouping = now.replace(hour=GROUPING_TIME_HOUR, minute=0, second=0, microsecond=0)
    next_grouping += timedelta(days=days_until_sunday)
    
    return next_grouping

@bot.event
async def on_message(message):
    print(f"{message.author} in '{message.channel.guild}':", message.content)
    await bot.process_commands(message)

@bot.command(name='signup_1on1')
async def signup_one_on_one(ctx):
    """Sign up for weekly 1-on-1 groupings"""
    user_id = ctx.author.id
    
    if await one_on_one_manager.add_user(user_id, bot):
        embed = discord.Embed(
            title="✅ Signed Up!",
            description=f"{ctx.author.mention} has been added to the 1-on-1 grouping list!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="What's Next?",
            value=f"You'll be randomly grouped with someone at {GROUPING_TIME_HOUR}:00 every sunday.",
            inline=False
        )
    else:
        embed = discord.Embed(
            title="ℹ️ Already Signed Up",
            description=f"{ctx.author.mention}, you're already on the 1-on-1 grouping list!",
            color=discord.Color.blue()
        )
    
    total_signups = len(one_on_one_manager.get_signups())
    embed.add_field(name="Total Participants", value=str(total_signups), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='leave_1on1')
async def remove_one_on_one(ctx):
    """Remove yourself from weekly 1-on-1 groupings"""
    user_id = ctx.author.id
    
    if await one_on_one_manager.remove_user(user_id, bot):
        embed = discord.Embed(
            title="❌ Removed",
            description=f"{ctx.author.mention} has been removed from the 1-on-1 grouping list.",
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="ℹ️ Not Found",
            description=f"{ctx.author.mention}, you weren't on the 1-on-1 grouping list.",
            color=discord.Color.blue()
        )
    
    total_signups = len(one_on_one_manager.get_signups())
    embed.add_field(name="Total Participants", value=str(total_signups), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='list_1on1')
async def list_one_on_one(ctx):
    """List all users signed up for 1-on-1 groupings"""
    signups = one_on_one_manager.get_signups()
    
    if not signups:
        embed = discord.Embed(
            title="📝 1-on-1 Signup List",
            description="No one has signed up yet!",
            color=discord.Color.orange()
        )
    else:
        user_mentions = []
        for user_id in signups:
            try:
                user = await bot.fetch_user(user_id)
                user_mentions.append(user.mention)
            except:
                user_mentions.append(f"<@{user_id}>")  # Fallback mention
        
        embed = discord.Embed(
            title="📝 1-on-1 Signup List",
            description=f"**{len(signups)} participants:**\n" + "\n".join(user_mentions),
            color=discord.Color.blue()
        )
    
    await ctx.send(embed=embed)

@bot.command(name='create_groupings')
@commands.has_permissions(administrator=True)
async def create_groupings_manual(ctx):
    """Manually create 1-on-1 groupings (Admin only)"""
    groupings = one_on_one_manager.create_groupings()
    
    if not groupings:
        embed = discord.Embed(
            title="❌ No Groupings Created",
            description="Need at least 2 people signed up to create groupings!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    # Save groupings
    filepath = await one_on_one_manager.save_groupings(groupings, ctx.guild.id, bot)
    
    # Create embed with groupings
    embed = discord.Embed(
        title="🎯 New 1-on-1 Groupings!",
        description="Here are this week's random groupings:",
        color=discord.Color.purple()
    )
    
    for i, group in enumerate(groupings, 1):
        user_mentions = []
        for user_id in group:
            try:
                user = await bot.fetch_user(user_id)
                user_mentions.append(user.mention)
            except:
                user_mentions.append(f"<@{user_id}>")
        
        group_type = "Trio" if len(group) == 3 else "Pair"
        embed.add_field(
            name=f"{group_type} {i}",
            value=" & ".join(user_mentions),
            inline=False
        )
    
    if filepath:
        embed.set_footer(text=f"Groupings saved to: {os.path.basename(filepath)}")
    
    await ctx.send(embed=embed)

@bot.command(name='1on1_config')
@commands.has_permissions(administrator=True)
async def one_on_one_config(ctx, interval_days: int = None, grouping_hour: int = None):
    """Configure 1-on-1 grouping settings (Admin only)"""
    global GROUPING_INTERVAL_DAYS, GROUPING_TIME_HOUR
    
    if interval_days is None and grouping_hour is None:
        # Show current config
        next_grouping = get_next_grouping_time()
        time_until = next_grouping - datetime.now()
        
        embed = discord.Embed(
            title="⚙️ 1-on-1 Configuration",
            color=discord.Color.blue()
        )
        embed.add_field(name="Grouping Interval", value=f"{GROUPING_INTERVAL_DAYS} days", inline=True)
        embed.add_field(name="Grouping Time", value=f"{GROUPING_TIME_HOUR}:00", inline=True)
        embed.add_field(name="Total Signups", value=str(len(one_on_one_manager.get_signups())), inline=True)
        
        # Format next grouping time
        next_grouping_str = next_grouping.strftime("%A, %B %d at %I:%M %p")
        embed.add_field(
            name="🕒 Next Automatic Grouping",
            value=f"{next_grouping_str}\n*({int(time_until.total_seconds() // 3600)} hours, {int((time_until.total_seconds() % 3600) // 60)} minutes)*",
            inline=False
        )
        
        await ctx.send(embed=embed)
        return
    
    # Update config
    if interval_days is not None:
        if 1 <= interval_days <= 30:
            GROUPING_INTERVAL_DAYS = interval_days
        else:
            await ctx.send("❌ Interval must be between 1 and 30 days!")
            return
    
    if grouping_hour is not None:
        if 0 <= grouping_hour <= 23:
            GROUPING_TIME_HOUR = grouping_hour
        else:
            await ctx.send("❌ Hour must be between 0 and 23!")
            return
    
    # Show updated config with next grouping time
    next_grouping = get_next_grouping_time()
    time_until = next_grouping - datetime.now()
    
    embed = discord.Embed(
        title="✅ Configuration Updated",
        color=discord.Color.green()
    )
    embed.add_field(name="Grouping Interval", value=f"{GROUPING_INTERVAL_DAYS} days", inline=True)
    embed.add_field(name="Grouping Time", value=f"{GROUPING_TIME_HOUR}:00", inline=True)
    
    next_grouping_str = next_grouping.strftime("%A, %B %d at %I:%M %p")
    embed.add_field(
        name="🕒 Next Automatic Grouping",
        value=f"{next_grouping_str}\n*({int(time_until.total_seconds() // 3600)} hours, {int((time_until.total_seconds() % 3600) // 60)} minutes)*",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='add_1on1')
@commands.has_permissions(administrator=True)
async def add_one_on_one(ctx, user: discord.Member):
    """Add a user to the 1-on-1 grouping list (Admin only)"""
    user_id = user.id
    
    if await one_on_one_manager.add_user(user_id, bot):
        embed = discord.Embed(
            title="✅ User Added!",
            description=f"{user.mention} has been added to the 1-on-1 grouping list by an admin!",
            color=discord.Color.green()
        )
        embed.add_field(
            name="What's Next?",
            value=f"They'll be randomly grouped with someone at {GROUPING_TIME_HOUR}:00 every sunday.",
            inline=False
        )
    else:
        embed = discord.Embed(
            title="ℹ️ Already Signed Up",
            description=f"{user.mention} is already on the 1-on-1 grouping list!",
            color=discord.Color.blue()
        )
    
    total_signups = len(one_on_one_manager.get_signups())
    embed.add_field(name="Total Participants", value=str(total_signups), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='remove_1on1')
@commands.has_permissions(administrator=True)
async def remove_one_on_one_admin(ctx, user: discord.Member):
    """Remove a user from the 1-on-1 grouping list (Admin only)"""
    user_id = user.id
    
    if await one_on_one_manager.remove_user(user_id, bot):
        embed = discord.Embed(
            title="❌ User Removed",
            description=f"{user.mention} has been removed from the 1-on-1 grouping list by an admin.",
            color=discord.Color.red()
        )
    else:
        embed = discord.Embed(
            title="ℹ️ Not Found",
            description=f"{user.mention} wasn't on the 1-on-1 grouping list.",
            color=discord.Color.blue()
        )
    
    total_signups = len(one_on_one_manager.get_signups())
    embed.add_field(name="Total Participants", value=str(total_signups), inline=True)
    
    await ctx.send(embed=embed)

# Custom help command
@bot.command(name='help')
async def custom_help(ctx):
    """Show help for all commands with separate sections for admins and users"""
    # Check if user has admin permissions
    is_admin = ctx.author.guild_permissions.administrator
    
    embed = discord.Embed(
        title="🤖 Connector Bot Help",
        description="Available commands:",
        color=discord.Color.blue()
    )
    
    # User Commands Section
    embed.add_field(
        name="👥 **User Commands**",
        value=(
            "`.signup_1on1` - Sign up for weekly 1-on-1 groupings\n"
            "`.leave_1on1` - Remove yourself from the grouping list\n"
            "`.list_1on1` - View all users signed up for groupings\n"
            "`.greet` - Get a friendly greeting from the bot\n"
            "`.help` - Show this help message"
        ),
        inline=False
    )
    
    # Admin Commands Section (only show if user is admin)
    if is_admin:
        embed.add_field(
            name="🔧 **Admin Commands**",
            value=(
                "`.create_groupings` - Manually create groupings\n"
                "`.1on1_config [days] [hour]` - Configure timing\n"
                "`.add_1on1 @user` - Add user to grouping list\n"
                "`.remove_1on1 @user` - Remove user from list"
            ),
            inline=False
        )
    
    # How it works section
    embed.add_field(
        name="ℹ️ **How 1-on-1 Groupings Work:**",
        value=(
            f"• Groupings are created every Sunday at {GROUPING_TIME_HOUR}:00\n"
            "• If there's an odd number of people, one group will have 3 people\n"
            "• All groupings are saved to the `past_groupings` directory\n"
            "• Automatic groupings happen every Sunday (configurable by admins)"
        ),
        inline=False
    )
    
    # Add footer based on user permissions
    if is_admin:
        embed.set_footer(text="💡 You have admin permissions - you can see all commands!")
    else:
        embed.set_footer(text="💡 Contact an admin if you need help with advanced features")
    
    await ctx.send(embed=embed)

# Automatic grouping task
@tasks.loop(hours=24)  # Check daily
async def check_for_grouping_time():
    """Check if it's time to create automatic groupings"""
    now = datetime.now()
    
    # Check if it's the right hour
    if now.hour != GROUPING_TIME_HOUR:
        return
    
    # Check if it's been enough days since last grouping
    # For simplicity, we'll check if it's the right day of the week
    # You can modify this logic based on your needs
    if now.weekday() != 0:  # 0 = sunday, adjust as needed
        return
    
    # Get all guilds the bot is in
    for guild in bot.guilds:
        try:
            # Find a general channel to send the groupings to
            channel = None
            for ch in guild.text_channels:
                if ch.name.lower() in ['general', 'random', 'main', 'chat']:
                    channel = ch
                    break
            
            if not channel:
                # Use the first available text channel
                channel = guild.text_channels[0] if guild.text_channels else None
            
            if not channel:
                print(f"No suitable channel found in guild {guild.name}")
                continue
            
            # Create groupings
            groupings = one_on_one_manager.create_groupings()
            
            if not groupings:
                continue  # Skip if no one signed up
            
            # Save groupings
            filepath = await one_on_one_manager.save_groupings(groupings, guild.id, bot)
            
            # Create embed with groupings
            embed = discord.Embed(
                title="🎯 Weekly 1-on-1 Groupings!",
                description="Here are this week's automatic random groupings:",
                color=discord.Color.purple()
            )
            
            for i, group in enumerate(groupings, 1):
                user_mentions = []
                for user_id in group:
                    try:
                        user = await bot.fetch_user(user_id)
                        user_mentions.append(user.mention)
                    except:
                        user_mentions.append(f"<@{user_id}>")
                
                group_type = "Trio" if len(group) == 3 else "Pair"
                embed.add_field(
                    name=f"{group_type} {i}",
                    value=" & ".join(user_mentions),
                    inline=False
                )
            
            if filepath:
                embed.set_footer(text=f"Groupings saved automatically • {os.path.basename(filepath)}")
            
            await channel.send(embed=embed)
            print(f"Automatic groupings created for guild {guild.name}")
            
        except Exception as e:
            print(f"Error creating automatic groupings for guild {guild.name}: {e}")

@check_for_grouping_time.before_loop
async def before_grouping_check():
    """Wait until the bot is ready before starting the task"""
    await bot.wait_until_ready()

@bot.event
async def on_ready():
    """Start the automatic grouping task when bot is ready"""
    print(f"Connector bot logged in as {bot.user.name}")
    if not check_for_grouping_time.is_running():
        check_for_grouping_time.start()

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("CONNECTOR_TOKEN")

bot.run(TOKEN)
