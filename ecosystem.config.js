module.exports = {
  apps: [{
    name: "time-tracker-bot",
    script: "./bot.py",
    interpreter: "./venv/bin/python", // Using the virtual environment's python
    watch: false,
    autorestart: true,
    max_memory_restart: "1G"
  }]
}
