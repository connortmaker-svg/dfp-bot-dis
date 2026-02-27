#!/bin/bash
echo "Starting Discord Time Tracker in PM2..."
pm2 start ecosystem.config.js
pm2 save
echo "Bot is now running in the background!"
