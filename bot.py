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
        
        # Calculate weekly time
        week_start = get_week_start(end_time)
        
        c.execute("SELECT start_time, duration_seconds FROM sessions WHERE user_id=? AND end_time IS NOT NULL", (user_id,))
        all_sessions = c.fetchall()
        
        weekly_seconds = 0
        for s_str, d_sec in all_sessions:
            s_time = datetime.fromisoformat(s_str)
            if s_time >= week_start:
                weekly_seconds += d_sec
                
        hours = weekly_seconds / 3600
        
        await interaction.response.send_message(f"Logged out. Session duration: {duration/3600:.2f} hours. Total this week: {hours:.2f} hours.", ephemeral=True)

@bot.event
async def on_ready():
    bot.add_view(TimeTrackingView())
    print(f'Logged in as {bot.user}')

@bot.command()
async def setup(ctx):
    embed = discord.Embed(title="Time Tracking", description="Click the buttons below to log in or log out.", color=discord.Color.blue())
    await ctx.send(embed=embed, view=TimeTrackingView())

if __name__ == '__main__':
    if not TOKEN or TOKEN == 'your_token_here':
        print("Please set your Discord bot token in the .env file")
    else:
        bot.run(TOKEN)
