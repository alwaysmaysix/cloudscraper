import cloudscraper
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
import os
import re
import sys
import platform

filename = "input.txt"
if len(sys.argv) > 1:
    filename = sys.argv[1]

config_path = 'config.txt'
if not os.path.exists(config_path):
    # Create the folder if it doesn't exist
    if platform.system() == 'Windows':
        folder_path = os.path.join(os.environ['APPDATA'], 'CB_DL')
    else:
        folder_path = os.path.join(os.path.expanduser("~"), 'Library/Application Support/CB_DL')
    os.makedirs(folder_path, exist_ok=True)

    # Set the config_path to the new location
    config_path = os.path.join(folder_path, 'config.txt')
    
    # Create the config file with the default content
    with open(config_path, 'w') as config_file:
        if platform.system() == 'Windows':
            config_file.write("ALREADY_DL_TXT: %APPDATA%\\CB_DL\\already_dl.txt")
        else:
            config_file.write("ALREADY_DL_TXT: ~/Library/Application Support/CB_DL/already_dl.txt")

# Set the path for failed_dl.txt in the current directory
failed_dl_path = 'failed_dl.txt'

# Read the config.txt file and get the path to already_dl.txt

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

# Check if the path was found
if already_dl_path is None:
    print("Could not find the path to already_dl.txt in the config.txt file.")

# Check if the folder for already_dl.txt exists, and if not, create it
folder_path = os.path.dirname(already_dl_path)
os.makedirs(folder_path, exist_ok=True)

# Check if the already_dl.txt file exists, and if not, create it
if not os.path.exists(already_dl_path):
    print("Creating already_dl.txt file at the specified path.")
    with open(already_dl_path, 'w'):
        pass

with open(already_dl_path, 'r') as al_dl_file:
    al_dl_urls = al_dl_file.readlines()

line_num = 0
    
with open(filename, "r") as input_file:
    lines = input_file.readlines()
    
for i, line in enumerate(lines):
    if 'www.' in line:
        lines[i] = line.replace('www.', '')

def remove_country_subdomain(url):
    return re.sub(r'https?://(\w+\.)?spankbang\.com/', 'https://spankbang.com/', url)

for line in lines:
    incaseofplaylist = line
    line = remove_country_subdomain(line)
    if any(line[:32] == url[:32] for url in al_dl_urls):
        print(f"The URL {line.strip()} already exists in already_dl.txt")

al_dl_urls = [remove_country_subdomain(url) for url in al_dl_urls]

# Now clean the new URLs and check against al_dl_urls
lines = [remove_country_subdomain(line.strip()) for line in lines]

# Filter out URLs that already exist in al_dl_urls
lines = [line for line in lines if not any(line[:32] == url[:32] for url in al_dl_urls)]

def page_exists(url):
    for _ in range(7):
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.head(url, timeout=5)
            return response.status_code < 400
        except (scraper.ConnectionError, scraper.Timeout):
            pass
        time.sleep(1)
    return False
def scrape_profile(url):
    username = re.search(r'/profile/(\w+)', url).group(1)
    profile_urls = []
    
    # Check if a specific page number is already in the URL
    page_match = re.search(r'[?&]page=(\d+)', url)
    if page_match:
        print("page specified")
        start_page = int(page_match.group(1))
        end_page = start_page + 1
    else:
        start_page = 1
        end_page = float('inf')  # Continue indefinitely

    page = start_page
    max_retries = 3  # Number of retries per page

    while page < end_page:
        retry_count = 0
        videos_found = False

        while retry_count < max_retries and not videos_found:
            page_url = f"https://spankbang.com/profile/{username}?o=new&page={page}"
            #print(page_url)  # Debug: print the page URL

            scraper = cloudscraper.create_scraper()
            html = scraper.get(page_url).text

            soup = BeautifulSoup(html, 'html.parser')
            video_items = soup.select('div.video-list-with-ads div.video-item > a.thumb')

            if video_items:
                videos_found = True
                for item in video_items:
                    if 'href' in item.attrs:
                        video_url = 'https://spankbang.com' + item['href']
                        profile_urls.append(video_url)

            else:
                #print(f"No video items found on page {page}, retry {retry_count + 1}/{max_retries}.")
                retry_count += 1
                time.sleep(1)  # Pause between retries

        if not videos_found:
            #print(f"No videos found on page {page} after {max_retries} retries.")
            print(f"Collected URLs from {username}")
            break

        page += 1

    username = username.rstrip()
    username = username.replace("Watch ", "")
    username = username.replace(": ", "- ")
    username = username.replace(" :", " -")
    username = username.replace(":", "-")
    username = username.replace("/", "-")
    username = username.replace("?", "-")
    username = username.replace("|", "-")
    username = username.replace("<", "-")
    username = username.replace(">", "-")
    username = username.replace("*", "")
    username = username.replace("\\", "")
    username = username.replace("\"", "")
    username = username.replace("\t", " ")
    username = username.replace("\x08", "")

    with open(f"{username}_profile_videos.txt", 'w') as file:
        for url in profile_urls:
            file.write(url + '\n')



def scrape_channel(url):
    match = re.search(r'/(\d+)/channel/(\w+)', url)
    channel_number = match.group(1)
    channel_name = match.group(2)
    channel_urls = []
    page = 1

    while True:
        page_url = f"https://spankbang.com/{channel_number}/channel/{channel_name}/{page}/"
        scraper = cloudscraper.create_scraper()
        html = scraper.get(page_url).text

        soup = BeautifulSoup(html, 'html.parser')
        video_items = soup.select('div.video-item > a.thumb')

        if not video_items:
            print(f"Finished collecting urls from {channel_name}")
            #print(f"No video items found on page {page}.")
            break

        for item in video_items:
            if 'href' in item.attrs:
                video_url = 'https://spankbang.com' + item['href']
                channel_urls.append(video_url)
            else:
                print(f"No 'href' attribute found in item: {item}")

        page += 1

    channel_name = channel_name.rstrip()
    channel_name = channel_name.replace("Watch ", "")
    channel_name = channel_name.replace(": ", "- ")
    channel_name = channel_name.replace(" :", " -")
    channel_name = channel_name.replace(":", "-")
    channel_name = channel_name.replace("/", "-")
    channel_name = channel_name.replace("?", "-")
    channel_name = channel_name.replace("|", "-")
    channel_name = channel_name.replace("<", "-")
    channel_name = channel_name.replace(">", "-")
    channel_name = channel_name.replace("*", "")
    channel_name = channel_name.replace("\\", "")
    channel_name = channel_name.replace("\"", "")
    channel_name = channel_name.replace("\t", " ")
    channel_name = channel_name.replace("\x08", "")

    with open(f"{channel_name}_channel_videos.txt", 'w') as file:
        for url in channel_urls:
            file.write(url + '\n')


illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
for line in lines:
    line = line.strip()
    line_num+=1
    url = remove_country_subdomain(line)
    if 'https://spankbang.com/' not in url and 'http://spankbang.com/' not in url:
        print("SpankBang is not in line " + str(line_num))
        print(url)
        continue
    # Check for Channel URL
    if re.search(r"/\d+/channel/\S+", url):
        scrape_channel(url)
        continue
    # Check for Profile URL
    if re.search("/profile/\\S+", url):
        scrape_profile(url)
        continue
    match = re.search("/playlist/\\S+", url)
    if match:
        genesisURL = url
        page_number = 1
        last_part = url.rsplit('/', 1)[-1] # Check if the last part of url after the last forward slash is a number
        if re.match(r"^\d+$", last_part):
            page_number = int(last_part)  # set page_number to the number
        while True:
            url = genesisURL + '/' + str(page_number)
            if not page_exists(url):
                break
            scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
            html = scraper.get(url).text  # return html
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.title.string if soup.title else None
            title = title.replace(' Playlist - HD Porn Videos - SpankBang', '')
            
            for char in illegal_chars:
                title = title.replace(char, '-')
            curator_span = soup.find('span', {'class': 'parent'})  # find span tag with class 'parent'. curator name is within a span
            if curator_span is not None:
                curator_link = curator_span.find('a')  # find a tag within that span
                if curator_link is not None:
                    curator = curator_link.text  # get the text within the a tag
                for char in illegal_chars:
                    curator = curator.replace(char, '')
            else:
                print('Curator not found')
                curator = "Anon"

            html_lines = html.split('\n') #split HTML into lines
            
            html_filtered = [line for line in html_lines if "\" class=\"n\"" in line] #titles are included at this point
            html_filtered = [line.replace('<a href="', '') for line in html_filtered] #remove <a href="
            for i, line in enumerate(html_filtered):
                html_filtered[i] = line.split('\" class=\"n\"', 1)[0]
            html_filtered = ['https://spankbang.com' + line.replace(' ', '') for line in html_filtered]
            # Write html_filtered lines to a txt file named after title
            with open(title + " - " + curator + '.txt', 'a') as f:
                for line in html_filtered:
                    f.write(line + '\n')
            html_filtered = '\n'.join(html_filtered)
            print("Page " + str(page_number))
            print(html_filtered)
            if html_filtered == "":
                page_number = page_number
            else:
                page_number += 1
        time.sleep(1)
        with open(title + " - " + curator + '.txt', "r") as urls_file:
            urls_lines = urls_file.readlines()
        with open(title + " - " + curator + '.txt', "w") as urls_file:
            for i, url in enumerate(urls_lines):
                print(str(i))
                html = scraper.get(url.strip()).text #return html
                soup = BeautifulSoup(html, 'html.parser')
                og_url_tag = soup.select_one('meta[property="og:url"]') #find og:url
                if og_url_tag is not None:
                    og_url = og_url_tag['content'] # get the url from the content attribute
                    print(og_url)
                    urls_lines[i] = og_url + '\n' # replace the original url with og_url
            urls_file.writelines(urls_lines)  # write all lines back to the file
        continue
    
    for attempt in range(7):
        
        scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        html = scraper.get(url).text  # return html

        soup = BeautifulSoup(html, 'html.parser')


        # Find the ul element with class "video_toolbar"
        ul_video_toolbar = soup.find('ul', class_='video_toolbar')
        if ul_video_toolbar:
            # Find the a tag inside the ul element
            a_tag = soup.find('a', class_='ul')

            if a_tag and 'href' in a_tag.attrs:
                # Extract the uploader name from the href attribute
                uploader_name = a_tag['href'].replace('/profile/', '') #/profile/ is in basic user names
                if '/' in uploader_name:
                    uploader_name = uploader_name.replace('/', '')
                    
                #remove the string "channel" from uploader's name
                if "channel" in uploader_name and "mychannel" not in uploader_name:
                    index = uploader_name.find("channel")
                    if index == 2:
                        uploader_name = uploader_name.replace(uploader_name[:index + len("channel")], "")
                print("Uploader name:", uploader_name)
                if uploader_name:
                    for char in illegal_chars:
                        uploader_name = uploader_name.replace(char, '-')
                    break
                else:
                    time.sleep(4)
            else:
                print("Hmm...")
        else:
            print("Hold...")
        time.sleep(1)
    else:
        print("Failed to find uploader name")
        uploader_name = "_"

    # Find the video tag with the id "main_video_player" and get the source tag within it
    video_tag = soup.find('video', {'id': 'main_video_player'})
    source_tag = video_tag.find('source') if video_tag else None
    fk_possible = True
    if source_tag:
        # Get the video URL from the source tag
        video_url = source_tag['src']
        if "720p.mp4" in video_url:
            video_url_4k = video_url.replace("720p.mp4", "4k.mp4")
            video_url_1080p = video_url.replace("720p.mp4", "1080p.mp4")
            video_url_720p = video_url
        if "480p.mp4" in video_url:
            video_url_4k = video_url.replace("480p.mp4", "4k.mp4")
            video_url_1080p = video_url.replace("480p.mp4", "1080p.mp4")
            video_url_720p = video_url.replace("480p.mp4", "720p.mp4")
            video_url_480p = video_url
        if "320p.mp4" in video_url:
            fk_possible = False
            video_url_1080p = video_url.replace("320p.mp4", "1080p.mp4")
            video_url_720p = video_url.replace("320p.mp4", "720p.mp4")
            video_url_480p = video_url.replace("320p.mp4", "480p.mp4")
            video_url_320p = video_url
        if "240p.mp4" in video_url:
            fk_possible = False
            video_url_1080p = video_url.replace("240p.mp4", "1080p.mp4")
            video_url_720p = video_url.replace("240p.mp4", "720p.mp4")
            video_url_480p = video_url.replace("240p.mp4", "480p.mp4")
            video_url_320p = video_url.replace("240p.mp4", "320p.mp4")
            video_url_240p = video_url
        #if 4k is available
        if fk_possible == True and scraper.head(video_url_4k).status_code != 404:
            video_url = video_url_4k
        elif scraper.head(video_url_1080p).status_code != 404:
            video_url = video_url_1080p
        #if not, go down to 720p
        elif scraper.head(video_url_720p).status_code != 404:
            video_url = video_url_720p
        elif scraper.head(video_url_480p).status_code != 404:
            video_url = video_url_480p
        elif scraper.head(video_url_320p).status_code != 404:
            video_url = video_url_320p
        elif scraper.head(video_url_240p).status_code != 404:
            print("240p :(")
            video_url = video_url_240p
        print("Video URL:", video_url)
    else:
        print("Failed to find the source tag.")
        continue


    video_title_tag = soup.find('title')
    if video_title_tag:
        video_title_text = video_title_tag.text
        video_title_text, _, _ = video_title_text.rpartition('-')
        image_title_text, _, _ = video_title_text.rpartition('-')
        #remove trailing space
        video_title_text = video_title_text.rstrip()
        video_title_text = video_title_text.replace("Watch ", "", 1)
        
        image_title_text = image_title_text.rstrip()
        image_title_text = image_title_text.replace("Watch ", "")
        image_title_text = image_title_text.replace(": ", "- ")
        image_title_text = image_title_text.replace(" :", " -")
        image_title_text = image_title_text.replace(":", "-")
        image_title_text = image_title_text.replace("/", "-")
        image_title_text = image_title_text.replace("?", "-")
        image_title_text = image_title_text.replace("|", "-")
        image_title_text = image_title_text.replace("<", "-")
        image_title_text = image_title_text.replace(">", "-")
        image_title_text = image_title_text.replace("*", "")
        image_title_text = image_title_text.replace("\\", "")
        image_title_text = image_title_text.replace("\"", "")
        image_title_text = image_title_text.replace("\t", " ")
        image_title_text = image_title_text.replace("\x08", "")
        image_title_text = image_title_text[:127]
        video_title_text = video_title_text.rstrip()
        video_title_text = video_title_text.replace("Watch ", "")
        video_title_text = video_title_text.replace(": ", "- ")
        video_title_text = video_title_text.replace(" :", " -")
        video_title_text = video_title_text.replace(":", "-")
        video_title_text = video_title_text.replace("/", "-")
        video_title_text = video_title_text.replace("?", "-")
        video_title_text = video_title_text.replace("|", "-")
        video_title_text = video_title_text.replace("<", "-")
        video_title_text = video_title_text.replace(">", "-")
        video_title_text = video_title_text.replace("*", "")
        video_title_text = video_title_text.replace("\\", "")
        video_title_text = video_title_text.replace("\"", "")
        video_title_text = video_title_text.replace("\t", " ")
        video_title_text = video_title_text.replace("\x08", "")
        video_title_text = video_title_text[:127]
        if video_title_text != 'Free Porn Videos and Movies':
            print(video_title_text)
        else:
            print('Failed to find title.')
    else:
        print("Failed to find title.")



    # find and dl image
    img_tag = soup.find('div', class_='play_cover').find('img')
    img_url = img_tag['src'].replace('w:300', 'w:1600')


    img_response = scraper.get(img_url)

    # Check if the request was successful
    if img_response.status_code == 200:
        in_counter = 1 #image number counter

        base_image_filename = f'{uploader_name} - {image_title_text}'
        
        image_filename = f'{base_image_filename}.jpg'
        # Check if the file already exists and increment
        while os.path.exists(image_filename):
            image_filename = f'{base_image_filename} ({in_counter}).jpg'
            in_counter += 1
        with open(image_filename, 'wb') as f:
            f.write(img_response.content)
            print("Image downloaded successfully.")
    else:
        print("Failed to download the image.")


    #dl vid
    response = scraper.get(video_url, stream=True)

    total_size = int(response.headers.get('Content-Length', 0))

    # Check if the request was successful
    if response.status_code == 200:
        counter = 1
        base_filename = f'{uploader_name} - {video_title_text}'
        # Check if the file already exists and increment until a unique name is found
        video_filename = f'{base_filename}.mp4'
        while os.path.exists(video_filename):
            video_filename = f'{base_filename} ({counter}).mp4'
            counter += 1
        # Save the video to a file
        with open(video_filename, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading video") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    # Update the progress bar
                    pbar.update(len(chunk))

        # Verify if the download reached 100%
        if pbar.n == total_size:
            print(f'Video downloaded successfully.' )
            with open(already_dl_path, 'a') as al_dl_file:
                al_dl_file.write('\n' + line)
        else:
            # Create failed_dl.txt in the current directory if it doesn't exist
            if not os.path.exists(failed_dl_path):
                with open(failed_dl_path, 'w') as failed_dl_file:
                    pass
    
            print(f'Download incomplete. pbar: {pbar.n} total_size: {total_size}')
            with open(failed_dl_path, 'a') as failed_dl_file:
                failed_dl_file.write('\n' + line)
