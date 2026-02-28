import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Database setup
conn = sqlite3.connect('time_tracking.sqlite3')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS sessions
             (user_id INTEGER, start_time TEXT, end_time TEXT, duration_seconds REAL)''')
conn.commit()

# Current day of week (Monday is 0, Sunday is 6)
# Today is Friday (weekday 4). Setting this to 4 so every week starts on Friday.
WEEK_START_DAY = 4

def get_week_start(dt):
    # Calculate the most recent day that matches WEEK_START_DAY
    # If today is WEEK_START_DAY, it's today at 00:00:00
    days_since_start = (dt.weekday() - WEEK_START_DAY) % 7
    week_start = dt.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_start)
    return week_start

def get_all_time_stats():
    c.execute("SELECT user_id, start_time, duration_seconds FROM sessions WHERE end_time IS NOT NULL")
    all_sessions = c.fetchall()
    
    now = datetime.now()
    
    # week_start -> { user_id: total_seconds }
    weekly_totals = {}
    # user_id -> total_seconds
    overall_totals = {}
    
    for uid, s_str, d_sec in all_sessions:
        s_time = datetime.fromisoformat(s_str)
        w_start = get_week_start(s_time)
        
        if w_start not in weekly_totals:
            weekly_totals[w_start] = {}
        if uid not in weekly_totals[w_start]:
            weekly_totals[w_start][uid] = 0
        weekly_totals[w_start][uid] += d_sec
        
        if uid not in overall_totals:
            overall_totals[uid] = 0
        overall_totals[uid] += d_sec
            
    # Also add current active session times
    c.execute("SELECT user_id, start_time FROM sessions WHERE end_time IS NULL")
    active_sessions = c.fetchall()
    for uid, s_str in active_sessions:
        s_time = datetime.fromisoformat(s_str)
        w_start = get_week_start(s_time)
        current_duration = (now - s_time).total_seconds()
        
        if w_start not in weekly_totals:
            weekly_totals[w_start] = {}
        if uid not in weekly_totals[w_start]:
            weekly_totals[w_start][uid] = 0
        weekly_totals[w_start][uid] += current_duration
        
        if uid not in overall_totals:
            overall_totals[uid] = 0
        overall_totals[uid] += current_duration
            
    return overall_totals, weekly_totals

def create_tracking_embed(stats=None):
    if stats is None:
        stats = get_all_time_stats()
        
    overall_totals, weekly_totals = stats
    
    embed = discord.Embed(title="Project Time Tracking (Ends April 30th)", description="Click the buttons below to log in or log out.", color=discord.Color.blue())
    
    if not overall_totals:
        embed.add_field(name="Logged Data", value="No time logged yet.", inline=False)
    else:
        # Total overall time
        overall_text = ""
        for uid, total_sec in overall_totals.items():
            hours = total_sec / 3600
            overall_text += f"<@{uid}>: **{hours:.2f} hours**\n"
        embed.add_field(name="Total Overall Time", value=overall_text, inline=False)
        
        # Weekly breakdown
        # Sort weeks chronologically
        sorted_weeks = sorted(weekly_totals.keys())
        for w_start in sorted_weeks:
            w_end = w_start + timedelta(days=6)
            week_label = f"Week of {w_start.strftime('%b %d')} - {w_end.strftime('%b %d')}"
            
            # List users for this week
            week_text = ""
            for uid, total_sec in weekly_totals[w_start].items():
                hours = total_sec / 3600
                week_text += f"<@{uid}>: {hours:.2f} hours\n"
                
            embed.add_field(name=week_label, value=week_text, inline=False)
            
    embed.set_footer(text="Totals reset every Friday!")
    return embed

class TimeTrackingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Login', style=discord.ButtonStyle.green, custom_id='login_button')
    async def login(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        now = datetime.now().isoformat()
        
        # Check if already logged in
        c.execute("SELECT * FROM sessions WHERE user_id=? AND end_time IS NULL", (user_id,))
        if c.fetchone():
            await interaction.response.send_message("You are already logged in!", ephemeral=True)
            return
            
        c.execute("INSERT INTO sessions (user_id, start_time, end_time, duration_seconds) VALUES (?, ?, NULL, 0)", (user_id, now))
        conn.commit()
        
        # Update the embed message
        new_embed = create_tracking_embed()
        await interaction.message.edit(embed=new_embed)
        
        await interaction.response.send_message("Logged in successfully!", ephemeral=True)

    @discord.ui.button(label='Logout', style=discord.ButtonStyle.red, custom_id='logout_button')
    async def logout(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        end_time = datetime.now()
        
        c.execute("SELECT rowid, start_time FROM sessions WHERE user_id=? AND end_time IS NULL", (user_id,))
        row = c.fetchone()
        
        if not row:
            await interaction.response.send_message("You are not logged in!", ephemeral=True)
            return
            
        rowid, start_time_str = row
        start_time = datetime.fromisoformat(start_time_str)
        duration = (end_time - start_time).total_seconds()
        
        c.execute("UPDATE sessions SET end_time=?, duration_seconds=? WHERE rowid=?", (end_time.isoformat(), duration, rowid))
        conn.commit()
        
        # Update the embed message
        new_embed = create_tracking_embed()
        await interaction.message.edit(embed=new_embed)
        
        await interaction.response.send_message(f"Logged out. Added {duration/3600:.2f} hours to your tracking logs.", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(TimeTrackingView())
    print(f'Logged in as {bot.user}')

@bot.command()
async def setup(ctx):
    embed = create_tracking_embed()
    await ctx.send(embed=embed, view=TimeTrackingView())

if __name__ == '__main__':
    if not TOKEN or TOKEN == 'your_token_here':
        print("Please set your Discord bot token in the .env file")
    else:
        bot.run(TOKEN)
