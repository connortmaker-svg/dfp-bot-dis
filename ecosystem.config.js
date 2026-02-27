module.exports = {
  apps: [{
    name: "time-tracker-bot",
    script: "./bot.py",
    interpreter: "python3", // Using python3 which is default for most linux distributions
    watch: false,
    autorestart: true,
    max_memory_restart: "1G"
  }]
}
