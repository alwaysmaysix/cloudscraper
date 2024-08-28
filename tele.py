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

# Set the path to the repository directory
repo_path = os.path.dirname(os.path.abspath(__file__))

# Create a Pyrogram Client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command("dl"))
def dl(client: Client, message: Message):
    url = ' '.join(message.command[1:])
    if url:
        try:
            # Create input.txt with the URL in the repo path
            create_input_file(url, repo_path)
            
            # Call sb_scraper.py as a separate process with the repo path
            result = subprocess.run(['python', os.path.join(repo_path, 'sb_scraper.py')], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Upload video files from the downloads directory in the repo path
                upload_and_delete_videos(client, message.chat.id, os.path.join(repo_path))
                
                # Inform user about the download process
                message.reply_text(f'Downloaded content from {url}. Processing complete.')
            else:
                message.reply_text(f'Failed to process content from {url}: {result.stderr}')
            
            # Delete input.txt after processing
            delete_input_file(repo_path)
        except Exception as e:
            message.reply_text(f'Failed to download content from {url}: {e}')
            # Ensure input.txt is deleted even if there's an error
            delete_input_file(repo_path)
    else:
        message.reply_text('Please provide a URL.')

def create_input_file(url, path):
    with open(os.path.join(path, 'input.txt'), 'w') as f:
        f.write(url)

def delete_input_file(path):
    input_file_path = os.path.join(path, 'input.txt')
    if os.path.exists(input_file_path):
        os.remove(input_file_path)

def upload_and_delete_videos(client: Client, chat_id: int, directory: str, retries=3):
    for filename in os.listdir(directory):
        if filename.endswith('.mp4'):
            base_filename = os.path.splitext(filename)[0]  # Get the base filename without extension
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                for attempt in range(retries):
                    try:
                        # Send the video file with the base filename as the caption
                        client.send_video(chat_id, file_path, height=1280, width=720, caption=f"{base_filename}.mp4", parse_mode=enums.ParseMode.MARKDOWN)
                        
                        # Delete the file after successful upload
                        os.remove(file_path)
                        logger.info(f'Successfully uploaded and deleted {file_path}')
                        break
                    except Exception as e:
                        logger.error(f'Failed to upload file on attempt {attempt + 1}/{retries}: {e}')
                        sleep(5)

def main():
    # Start the Pyrogram client
    app.run()

if __name__ == '__main__':
    main()
