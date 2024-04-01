import os                          
import requests                    
import time                        
from selenium import webdriver     
from selenium.webdriver.common.by import By     
import pandas as pd # for the csv

def save_image(url):
        folder_path = 'images'
        response = requests.get(url)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        ext = response.url.split("/")[-1]
        filename = os.path.join(folder_path, f'downloaded_image.{ext}')

        with open(filename, 'wb') as f:
            f.write(response.content)

def save_to_csv(data, filename):                                
    df = pd.DataFrame(data, columns=['Value'])
    df.to_csv(filename, index=True)
    print(f"Data saved to {filename}")


url = 'https://mastodon.social/explore'
options = webdriver.ChromeOptions()  # using chorme drivers
options.add_argument('headless')  # like without CSS in the webpage
driver = webdriver.Chrome(options=options)  # using driver to control
driver.get(url)

for _ in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    videos = []
    links = []
    texts = []

    for img in driver.find_elements(By.TAG_NAME, 'img'):
        img_url = img.get_attribute('src')
        save_image(img_url)

    for video in driver.find_elements(By.TAG_NAME, 'video'):
        video_url = video.get_attribute('src')
        videos.append(video_url)
    
    for iframe in driver.find_elements(By.TAG_NAME, 'iframe'):
        if iframe.get_attribute('src'):
            videos.append(iframe.get_attribute('src'))

    for link in driver.find_elements(By.TAG_NAME, 'a'):
        link_url = link.get_attribute('href')
        links.append(link_url)

    for tag in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'div']:
        for element in driver.find_elements(By.TAG_NAME, tag):
            texts.append(element.text)
    save_to_csv(videos, 'video_data.csv')
    save_to_csv(links, 'link_data.csv')
    save_to_csv(texts, 'text_data.csv')       

driver.quit()

