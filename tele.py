from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import cloudscraper
import requests
from io import BytesIO
from pyrogram import Client

# Initialize the Pyrogram client
app = Client("my_bot")

# Define the /dl command handler
def dl(update, context):
    url = ' '.join(context.args)
    if url:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Send the file via Telegram without saving it to disk
                file_bytes = BytesIO(response.content)
                context.bot.send_document(chat_id=update.message.chat_id, document=file_bytes, filename=url.split("/")[-1])
                update.message.reply_text(f'Downloaded content from {url}')
            else:
                update.message.reply_text(f'Failed to download content from {url}')
        except Exception as e:
            update.message.reply_text(f'Failed to download content from {url}: {e}')
    else:
        update.message.reply_text('Please provide a URL.')

def main():
    # Replace 'YOUR_TOKEN' with the token you received from BotFather
    updater = Updater('YOUR_TOKEN', use_context=True)
    dp = updater.dispatcher

    # Add the /dl command handler
    dp.add_handler(CommandHandler('dl', dl))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
