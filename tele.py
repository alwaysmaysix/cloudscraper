import os
import logging
import subprocess
from pyrogram import Client, filters, enums
from pyrogram.types import Message
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
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

# Create a Pyrogram Client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

def create_input_file(url):
    with open('input.txt', 'w') as f:
        f.write(url)

def delete_input_file():
    if os.path.exists('input.txt'):
        os.remove('input.txt')

@app.on_message(filters.command("dl"))
def dl(client: Client, message: Message):
    url = ' '.join(message.command[1:])
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
                temp_filename = 'output_temp.mp4'
                with open(temp_filename, 'wb') as temp_file:
                    temp_file.write(content)
                
                # Upload the video file to Telegram
                upload_to_telegram(client, message.chat.id, temp_filename)
                
                # Inform user about the download process
                message.reply_text(f'Downloaded content from {url}. Processing complete.')
                
                # Delete the temporary file
                os.remove(temp_filename)
            else:
                message.reply_text(f'Failed to process content from {url}: {result.stderr}')
            
            # Delete input.txt after processing
            delete_input_file()
        except Exception as e:
            message.reply_text(f'Failed to download content from {url}: {e}')
            # Ensure input.txt is deleted even if there's an error
            delete_input_file()
    else:
        message.reply_text('Please provide a URL.')

def upload_to_telegram(client: Client, chat_id: int, file_path: str, retries=3):
    fname = os.path.basename(file_path)
    for attempt in range(retries):
        try:
            client.send_video(chat_id, file_path, height=1280, width=720, caption=fname, parse_mode=enums.ParseMode.MARKDOWN)
            break
        except Exception as e:
            logger.error(f'Failed to upload file on attempt {attempt + 1}/{retries}: {e}')
            sleep(5)

def main():
    # Start the Pyrogram client
    app.run()

if __name__ == '__main__':
    main()
