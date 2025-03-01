import os
import time
import logging
import paramiko
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

# Configuration
TELEGRAM_BOT_TOKEN = "7714425793:AAEmGC7o7ULDIbEyfyzjKAhrgGIN530tiwI"
GROUP_CHAT_ID = "-1002200859431"  # Your Telegram group where logs will be sent
BOTS_TO_MONITOR = {
    "Bot1": {"token": "8195465392:AAEMEnNNEwdJZ5x4cDwdhytyNVAf_cWwNss", "restart_cmd": "screen -X -S musicxdrag quit; cd /home/user/bots/bot1 && screen -dmS bot1 python3 -m AnonXMusic"},
    "Bot2": {"token": "7799980150:AAFUzttHyEXxYfXDOWLnpT6FGC_ePCspSlw", "restart_cmd": "screen -X -S test quit; cd /home/user/bots/bot2 && screen -dmS bot2 python3 -m AnonXMusic"},
    # Add more bots here
}
CHECK_INTERVAL = 60  # Check every 60 seconds

def check_bot_status(bot_name, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        return False
    return False

def restart_bot(bot_name, restart_cmd):
    try:
        os.system(restart_cmd)
        return True
    except Exception as e:
        logging.error(f"Failed to restart {bot_name}: {e}")
        return False

def send_notification(bot, message):
    bot.send_message(chat_id=GROUP_CHAT_ID, text=message)

def monitor_bots():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    while True:
        for bot_name, bot_data in BOTS_TO_MONITOR.items():
            if not check_bot_status(bot_name, bot_data["token"]):
                send_notification(bot, f"⚠️ {bot_name} is down! Attempting restart...")
                
                if restart_bot(bot_name, bot_data["restart_cmd"]):
                    send_notification(bot, f"✅ {bot_name} restarted successfully!")
                else:
                    send_notification(bot, f"❌ Failed to restart {bot_name}, manual intervention needed!")
        time.sleep(CHECK_INTERVAL)

def uptime_command(update: Update, context: CallbackContext):
    status_message = "📊 Bot Status:\n"
    for bot_name, bot_data in BOTS_TO_MONITOR.items():
        is_online = check_bot_status(bot_name, bot_data["token"])
        status_message += f"🔹 {bot_name}: {'✅ Online' if is_online else '❌ Offline'}\n"
    update.message.reply_text(status_message)

def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("uptime", uptime_command))
    
    updater.start_polling()
    monitor_bots()
    updater.idle()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
