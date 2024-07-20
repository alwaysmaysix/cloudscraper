import os
import logging
import subprocess
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telethon import TelegramClient, errors
from time import sleep

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load API credentials from environment variables
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')

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
                
                # Save content to a temporary file
                temp_filename = 'output_temp.txt'
                with open(temp_filename, 'wb') as temp_file:
                    temp_file.write(content)
                
                # Upload the file to Telegram using telegram-upload
                upload_to_telegram(temp_filename)
                
                # Inform user about the download process
                update.message.reply_text(f'Downloaded content from {url}. Processing complete.')
                
                # Delete the temporary file
                os.remove(temp_filename)
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

def upload_to_telegram(file_path, retries=3, timeout=200):
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
    session_name = 'session'

    client = TelegramClient(session_name, api_id, api_hash, timeout=timeout)
    client.connect()

    if not client.is_user_authorized():
        client.send_code_request(phone_number)
        client.sign_in(phone_number, input('Enter the code: '))

    for attempt in range(retries):
        try:
            client.send_file('me', file_path)
            break
        except errors.FloodWaitError as e:
            logger.warning(f'Flood wait error: Waiting for {e.seconds} seconds before retrying.')
            sleep(e.seconds)
        except (errors.TimeoutError, errors.NetworkMigrateError, errors.PhoneMigrateError) as e:
            logger.warning(f'Error occurred: {e}. Retrying {attempt + 1}/{retries}...')
            sleep(5)
        except Exception as e:
            logger.error(f'Failed to upload file: {e}')
            break

    client.disconnect()

def main():
    # Use the token provided for the Telegram bot, but only for command handling
    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'))
    
    # Log bot start
    logger.info('Starting the bot...')
    
    dp = updater.dispatcher

    # Add the /dl command handler
    dp.add_handler(CommandHandler('dl', dl))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
