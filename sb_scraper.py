import cloudscraper
import requests
from bs4 import BeautifulSoup
import time
from tqdm import tqdm

line_num = 0

with open("input.txt", "r") as input_file:
    lines = input_file.readlines()
for line in lines:
    line = line.strip()
    line_num+=1
    url = line
    if 'https://spankbang.com/' not in line and 'http://spankbang.com/' not in line:
        print("SpankBang is not in line " + str(line_num))
        print(line)
        continue
    for attempt in range(5):
        
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
                uploader_name = a_tag['href'].replace('/profile/', '')
                if '/kc/channel/' in uploader_name:
                    uploader_name = uploader_name.replace('/kc/channel/', '')
                if '/' in uploader_name:
                    uploader_name = uploader_name.replace('/', '')

                # Store the uploader name in a variable
                print("Uploader name:", uploader_name)
                if uploader_name:
                    break
                else:
                    time.sleep(5)
            else:
                print("Failed to find the a tag or href attribute.")
        else:
            print("Failed to find the ul element with class 'video_toolbar'.")
        time.sleep(1)
    else:
        print("Failed to find uploader name")
        uploader_name = "_"

    # Find the video tag with the id "main_video_player" and get the source tag within it
    video_tag = soup.find('video', {'id': 'main_video_player'})
    source_tag = video_tag.find('source') if video_tag else None

    if source_tag:
        # Get the video URL from the source tag
        video_url = source_tag['src']
        if "720p.mp4" in video_url:
            video_url_1080p = video_url.replace("720p.mp4", "1080p.mp4")
            video_url_720p = video_url
            
        if "480p.mp4" in video_url:
            video_url_1080p = video_url.replace("480p.mp4", "1080p.mp4")
            video_url_720p = video_url.replace("480p.mp4", "720p.mp4")

        if requests.head(video_url_1080p).status_code != 404:
            video_url = video_url_1080p
            
        #if not, go down to 720p
        if requests.head(video_url_720p).status_code != 404:
            video_url = video_url_720p
            print(video_url)
        print("Video URL:", video_url)
        
    else:
        print("Failed to find the source tag.")


    video_title_tag = soup.find('title')
    if video_title_tag:
        video_title_text = video_title_tag.text
        video_title_text, _, _ = video_title_text.rpartition('-')
        image_title_text, _, _ = video_title_text.rpartition('-')
        
        #remove trailing space
        video_title_text = video_title_text.rstrip()
        video_title_text = video_title_text.replace("Watch ", "", 1)

        image_title_text = image_title_text.rstrip()
        
        print(video_title_text)
    else:
        print("Failed to find title.")




    # find and dl image
    img_tag = soup.find('div', class_='play_cover').find('img')
    img_url = img_tag['src'].replace('w:300', 'w:1600')


    img_response = requests.get(img_url)

    # Check if the request was successful
    if img_response.status_code == 200:
        # Save the image to a file
        with open(f'{uploader_name} - {image_title_text}.jpg', 'wb') as f:
            f.write(img_response.content)
        print("Image downloaded successfully.")
    else:
        print("Failed to download the image.")


    #dl vid
    response = requests.get(video_url, stream=True)

    total_size = int(response.headers.get('Content-Length', 0))

    # Check if the request was successful
    if response.status_code == 200:
        # Save the video to a file
        with open(f'{uploader_name} - {video_title_text}.mp4', 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="Downloading video") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    # Update the progress bar
                    pbar.update(len(chunk))
        print("Video downloaded successfully.")
    else:
        print("Failed to download the video.")

    time.sleep(2)
