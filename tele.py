import os
import subprocess
from io import BytesIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

def create_input_file(url):
    with open('input.txt', 'w') as f:
        f.write(url)

def delete_input_file():
    if os.path.exists('input.txt'):
        os.remove('input.txt')

def dl(update: Update, context: CallbackContext):
    url = ' '.join(context.args)
    if url:
        try:
            # Create input.txt with the URL
            create_input_file(url)
            
            # Call sb_scraper.py as a separate process
            result = subprocess.run(['python', 'sb_scraper.py'], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Read the output file produced by sb_scraper.py
                with open('output.txt', 'rb') as f:
                    content = f.read()
                
                # Send the processed content as a file via Telegram
                file_bytes = BytesIO(content)
                file_bytes.name = url.split("/")[-1]
                context.bot.send_document(chat_id=update.message.chat.id, document=file_bytes, filename=url.split("/")[-1])
                update.message.reply_text(f'Downloaded content from {url}')
            else:
                update.message.reply_text(f'Failed to process content from {url}: {result.stderr}')
            
            # Delete input.txt after processing
            delete_input_file()
        except Exception as e:
            update.message.reply_text(f'Failed to download content from {url}: {e}')
            # Ensure input.txt is deleted even if there's an error
            delete_input_file()
    else:
        update.message.reply_text('Please provide a URL.')

def main():
    updater = Updater('7267061537:AAHJ1t0VYcddMG0e4xHi2m77HIuaH8MqD7U')
    dp = updater.dispatcher

    # Add the /dl command handler
    dp.add_handler(CommandHandler('dl', dl))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
