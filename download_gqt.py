from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import chromedriver_autoinstaller
import os
import requests
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

chromedriver_autoinstaller.install()
# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)
total_pages = 80
all_urls = []
try:
    for page_num in range(total_pages):
        if page_num == 0:
            driver.get("https://www.bbc.co.uk/programmes/b006qp2f/episodes/player")
        else:
            driver.get(
                f"https://www.bbc.co.uk/programmes/b006qp2f/episodes/player?page={page_num+1}"
            )

        elements = driver.find_elements(
            "css selector", "a.br-blocklink__link.block-link__target"
        )

        # Extract the href attribute
        all_urls.extend([element.get_attribute("href") for element in elements])
except NoSuchElementException:
    print("An element was not found on one of the pages.")

# Print the href link
print(len(all_urls))
print(all_urls[:5])
mp3_dir = "audio"
for url in all_urls:
    # Locate the anchor tag containing the .mp3 link using an appropriate selector
    driver.get(url)
    try:
        mp3_element = driver.find_element(
            "css selector", "a[data-bbc-title='cta_download']"
        )

        # Extract the .mp3 link
        mp3_link = mp3_element.get_attribute("href")

        file_name = mp3_link.split("/")[-1] + ".mp3"
        file_path = os.path.join(mp3_dir, file_name)
        try:
            # Send a GET request to download the file
            response = requests.get(mp3_link)
            response.raise_for_status()  # Check if the request was successful

            # Save the file
            with open(file_path, "wb") as file:
                file.write(response.content)

            print(f"Downloaded {file_name}")

        except requests.exceptions.RequestException as e:
            print(f"Failed to download {file_name}: {e}")
    except:
        print(f"{url} is not parsing mp3 links correctly")

driver.quit()
