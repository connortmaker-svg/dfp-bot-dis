module.exports = {
  apps : [{
    name   : "time-tracker-bot",
    script : "./bot.py",
    interpreter: "python", // You can change this to "python3" or the path to your virtual env's python executeable if needed.
    watch  : false,
    autorestart: true,
    max_memory_restart: "1G"
  }]
}
