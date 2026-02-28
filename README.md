# Discord Time Tracker Bot

A simple, easy-to-deploy Discord bot that allows users to track their time using interactive buttons. It calculates time spent in active sessions and total time tracked per week (resetting on Fridays).

## Features
- **Interactive UI**: Login and Logout buttons attached to a persistent embed.
- **Weekly Tracking**: Automatically tracks and lists the current week's logged hours.
- **Local Database**: Uses SQLite for lightweight, zero-configuration data storage.
- **PM2 Support**: Includes scripts to easily PM2 daemonize the bot on Linux environments so it runs continuously in the background.

---

## 🚀 Setup Guide

### 1. Discord Developer Portal
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a **New Application**.
3. Go to the **Bot** tab on the left menu and grab your **Token** (keep this secret!).
4. Scroll down on the Bot tab and turn **ON** the `Message Content Intent` and save changes.
5. Go to the **OAuth2 -> URL Generator** tab.
6. Select `bot` under Scopes.
7. Under Bot Permissions, select `Send Messages` and `Read Messages/View Channels`.
8. Copy the generated URL at the bottom and paste it into your browser to invite the bot to your server.

### 2. Linux Server Installation

1. Clone or pull this repository to your Linux server.
2. Create the environment file:
   ```bash
   nano .env
   ```
3. Paste in your bot token:
   ```ini
   DISCORD_TOKEN=your_token_here
   ```
4. Make the startup script executable:
   ```bash
   chmod +x start_bot.sh
   ```
5. Run the startup script. This script automatically creates a Virtual Environment, installs required dependencies, and sets the bot up in PM2 so it runs indefinitely:
   ```bash
   ./start_bot.sh
   ```

### 3. Usage in Discord
Once your bot is online, go to any text channel in your Discord server and type:
```
!setup
```
The bot will send an embed message with Green and Red buttons to log in and log out. Users simply click the buttons to track their time!

---

## Troubleshooting

If the bot won't come online or crashes:
- **Check PM2 Logs**: Run `pm2 logs time-tracker-bot` to see the exact python errors.
- **Bot Intents**: Double check that `Message Content Intent` is toggled on in the Discord portal.
- **Environment Details**: Ensure your `.env` file exists in the same folder as `bot.py` and contains the correct token format.
