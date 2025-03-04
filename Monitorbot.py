import os
import time
import logging
import requests
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Configuration
TELEGRAM_BOT_TOKEN = "7714425793:AAEmGC7o7ULDIbEyfyzjKAhrgGIN530tiwI"
GROUP_CHAT_ID = "-1002200859431"
OWNER_ID = 7361622601  # Replace with the actual Telegram user ID of the bot owner
BOTS_TO_MONITOR = {
    "Bot1": {"token": "7781287725:AAEGW1u0kt6e9rLBQUBMGlU9L2GN3CxG9jI"},
    "Bot2": {"token": "8195465392:AAFU0ViPHc0LEaSPVHFWme5v7cxlUn9kIRo"},
    "bot3": {"token": "7801213482:AAEoQ98jWCDxpUlAj0xGfKqFwdmnE7h0UD4"},
}
CHECK_INTERVAL = 3600  # Check every 1 hour (3600 seconds)

def check_bot_status(bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

async def send_notification(bot, message):
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=message, parse_mode="HTML")

async def monitor_bots():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    while True:
        status_message = "<b>📊 Bot Status Update:</b>\n"
        for bot_name, bot_data in BOTS_TO_MONITOR.items():
            is_online = check_bot_status(bot_data["token"])
            status_message += f"<b>🔹 {bot_name}:</b> {'<b>✅ Online</b>' if is_online else '<b>❌ Offline</b>'}\n"
        await send_notification(bot, status_message)
        await asyncio.sleep(CHECK_INTERVAL)

async def uptime_command(update: Update, context: CallbackContext):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("⚠️ You are not authorized to use this command.")
        return
    
    status_message = "<b>📊 Bot Status:</b>\n"
    for bot_name, bot_data in BOTS_TO_MONITOR.items():
        is_online = check_bot_status(bot_data["token"])
        status_message += f"<b>🔹 {bot_name}:</b> {'<b>✅ Online</b>' if is_online else '<b>❌ Offline</b>'}\n"
    await update.message.reply_text(status_message, parse_mode="HTML")

async def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("uptime", uptime_command))
    
    # Start monitoring bots in the background
    asyncio.create_task(monitor_bots())
    
    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(main())  # Schedule main() instead of blocking
        loop.run_forever()  # Keep the event loop running
    except RuntimeError:
        asyncio.run(main())  # If no loop is running, start a new one
