import cloudscraper
from bs4 import BeautifulSoup
import os
import re
import sys
import platform
import json

# Setup configuration and folders
config_path = 'config.txt'
if not os.path.exists(config_path):
    if platform.system() == 'Windows':
        folder_path = os.path.join(os.environ['APPDATA'], 'CB_DL')
    else:
        folder_path = os.path.join(os.path.expanduser("~"), 'Library/Application Support/CB_DL')
    os.makedirs(folder_path, exist_ok=True)
    config_path = os.path.join(folder_path, 'config.txt')
    with open(config_path, 'w') as config_file:
        if platform.system() == 'Windows':
            config_file.write("ALREADY_DL_TXT: %APPDATA%\\CB_DL\\already_dl.txt")
        else:
            config_file.write("ALREADY_DL_TXT: ~/Library/Application Support/CB_DL/already_dl.txt")

# Retrieve path for already downloaded URLs
already_dl_path = None
with open(config_path, 'r') as config_file:
    for line in config_file:
        if line.startswith('ALREADY_DL_TXT:'):
            already_dl_path = line.split(':', 1)[1].strip()
            if platform.system() == 'Windows':
                already_dl_path = already_dl_path.replace('%APPDATA%', os.environ['APPDATA'])
            else:
                already_dl_path = already_dl_path.replace('~/Library/Application Support', os.path.expanduser("~") + '/Library/Application Support')
            break

if already_dl_path is None:
    print("Could not find the path to already_dl.txt in the config.txt file.")
if not os.path.exists(already_dl_path):
    os.makedirs(os.path.dirname(already_dl_path), exist_ok=True)
    with open(already_dl_path, 'w'):
        pass

# Function to normalize and remove country-specific subdomains from URLs
def remove_country_subdomain(url):
    return re.sub(r'https?://(\w+\.)?spankbang\.com/', 'https://spankbang.com/', url)

# Function to scrape and print URLs from the given webpage
def scrape_page(url):
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        video_links = soup.select('a[href*="/video"]')  # Example selector for video links
        for link in video_links:
            video_url = 'https://spankbang.com' + link['href']
            if video_url not in already_dl_urls:
                print(video_url)

# Interactive URL input
try:
    while True:
        user_input = input("Enter a URL (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        user_input = remove_country_subdomain(user_input.strip())
        scrape_page(user_input)
except KeyboardInterrupt:
    print("\nProcess was interrupted by user.")
