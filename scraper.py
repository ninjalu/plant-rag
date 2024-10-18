from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import time

chromedriver_autoinstaller.install()
# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)
url = "https://www.rhs.org.uk/plants/search-results?droughtResistant=true"

driver.get(url)


def scroll_and_load():
    # Get all the initial elements (anchors with specific attributes)
    initial_elements = driver.find_elements(
        By.CSS_SELECTOR,
        'a[data-ga-component-name="app-plants-search-list-item"].u-faux-block-link__overlay',
    )
    counter = 0

    while True:
        # Scroll down 80% of the page height
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Use WebDriverWait to wait for new elements to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "li.gl-view__col.ng-star-inserted")
                )
            )
        except Exception as e:
            print("No new content loaded after waiting:", e)
            break

        # Get the number of elements after scrolling
        new_elements = driver.find_elements(
            By.CSS_SELECTOR, "li.gl-view__col.ng-star-inserted"
        )
        print(f"New elements detected: {len(new_elements)}")

        # Scroll to each new element to trigger lazy loading
        for element in new_elements[-1:]:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            time.sleep(1)  # Wait a bit to ensure content is loaded

        # Check if new elements have been loaded
        if len(new_elements) == len(initial_elements):
            counter += 1
            if counter > 10:
                print(
                    "No new elements detected. Reached the bottom or no more content is loading."
                )
                break
        else:
            initial_elements = (
                new_elements  # Update the count of elements for the next iteration
            )

        # Optional: Wait a bit to ensure content is fully loaded before scrolling again
        time.sleep(1)


scroll_and_load()
# Extract links
links = driver.find_elements(
    By.XPATH,
    '//a[@data-ga-link-type="image-and-text" and @data-ga-component-name="app-plants-search-list-item"]',
)
urls = [link.get_attribute("href") for link in links]
for url in urls:
    driver.get(url.strip())
    name = url.split("/")[-2]
    with open(f"corpus/{name}.txt", "w") as f:
        # Using XPath to find the element
        try:
            h1_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[@class='h1--alt']"))
            )
            botanical_name = h1_element.text
            f.write(f"Botanical Name: {botanical_name}\n")

            # Split the botanical name into genus_species and cultivar
            genus_species = botanical_name.split("'")[0]
            f.write(f"Genus and Species: {genus_species}")
            if len(botanical_name.split("'")) > 1:
                cultivar = botanical_name.split("'")[1]
                f.write(f"Cultivar: {cultivar}")
        except Exception as e:
            print("Names not found:", e)

        try:
            p_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//p[@class='ng-star-inserted']")
                )
            )
            description = p_element.text
            f.write(f"Description: {description}")
        except Exception as e:
            print("Description not found:", e)

        try:
            div_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='flag__body' and .//h6[text()='Ultimate height']]",
                    )
                )
            )
            ultimate_height_value = div_element.text.split("\n")[1]
            f.write(f"Ultimate Height: {ultimate_height_value}")
        except Exception as e:
            print("Ultimate height not found:", e)

        try:
            div_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='flag__body' and .//h6[text()='Time to ultimate height']]",
                    )
                )
            )
            ultimate_height_time = div_element.text.split("\n")[1]
            f.write(f"Time to ultimate height: {ultimate_height_time}")
        except Exception as e:
            print("Time to height not found:", e)

        try:
            div_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='flag__body' and .//h6[text()='Ultimate spread']]",
                    )
                )
            )
            ultimate_spread = div_element.text.split("\n")[1]
            f.write(f"Ultimate spread: {ultimate_spread}")
        except Exception as e:
            print("Ultimate spread not found:", e)

        try:
            parent_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='l-row l-row--space l-row--compact l-row--auto-clear ng-star-inserted']",
                    )
                )
            )
            soil_types = parent_div.find_elements(
                By.XPATH, ".//div[@class='flag__body']"
            )
            soil_types_text = [soil.text for soil in soil_types]
            f.write(f"Soil Types: {', '.join(soil_types_text)}")
        except Exception as e:
            print("Soil types not found:", e)

        # Using XPath to find moisture levels
        try:
            moisture_parent_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='l-col-xs-6 l-col-sm-6 l-col-md-6 l-col-lg-6 ng-star-inserted' and .//h6[text()='Moisture']]",
                    )
                )
            )
            moisture_spans = moisture_parent_div.find_elements(
                By.XPATH, ".//span[@class='ng-star-inserted']"
            )
            moisture_levels = [span.text for span in moisture_spans]
            f.write(f"Moisture Levels: {', '.join(moisture_levels)}")
        except Exception as e:
            print("Moisture levels not found:", e)

        try:
            moisture_parent_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='l-col-xs-6 l-col-sm-6 l-col-md-6 l-col-lg-6 ng-star-inserted' and .//h6[text()='pH']]",
                    )
                )
            )
            moisture_spans = moisture_parent_div.find_elements(
                By.XPATH, ".//span[@class='ng-star-inserted']"
            )
            moisture_levels = [span.text for span in moisture_spans]
            f.write(f"pH: {' '.join(moisture_levels)}")
        except Exception as e:
            print("Moisture levels not found:", e)

        try:
            table_rows = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//table[@class='table table--plant-details']/tr")
                )
            )

            seasons = ["Spring", "Summer", "Autumn", "Winter"]
            attributes = ["Stem", "Flower", "Foliage", "Fruit"]
            colors = {season: {attr: [] for attr in attributes} for season in seasons}

            for row in table_rows[1:]:  # Skip the header row
                season = row.find_element(By.XPATH, "./th").text
                cells = row.find_elements(By.XPATH, "./td")
                for i, cell in enumerate(cells):
                    color_spans = cell.find_elements(
                        By.XPATH, ".//span[@class='tooltip-v2__content']"
                    )
                    colors[season][attributes[i]] = [
                        span.get_attribute("innerHTML").strip() for span in color_spans
                    ]
            color_str = ""
            for season, attrs in colors.items():
                color_str += f"In {season},"
                for attr, color_list in attrs.items():
                    if color_list:
                        color_str += f" {attr.lower()} colour is {' and '.join(color_list).lower()},"
                if color_str.endswith(f"In {season},"):
                    color_str = color_str.rstrip(f"In {season},")
                color_str += "\n"
            f.write(color_str)

        except Exception as e:
            print("Error extracting colors:", e)

        try:
            sun_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='flag__body u-w-auto']")
                )
            )
            f.write(f"Sun Exposure: {sun_element.text}")
        except Exception as e:
            print("Error extracting sun exposure:", e)

        try:
            # Wait for the parent container to be present
            parent_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='panel__body']")
                )
            )

            # Locate the "Family" span element and extract its text
            family_span = parent_container.find_element(
                By.XPATH, ".//span[dt[text()='Family']]"
            )
            family_dt = family_span.find_element(By.XPATH, ".//dt").text
            family_dd = family_span.find_element(By.XPATH, ".//dd").text
            f.write(f"{family_dt}: {family_dd}")

            # Locate the "Genus" span element and extract its text
            genus_span = parent_container.find_element(
                By.XPATH, ".//span[dt[text()='Genus']]"
            )
            genus_dt = genus_span.find_element(By.XPATH, ".//dt").text
            genus_dd = genus_span.find_element(By.XPATH, ".//dd").text

            # Check if <dd> contains a <p> element and extract its text
            try:
                p_element = genus_span.find_element(By.XPATH, ".//dd//p")
                genus_dd = p_element.text  # Update genus_dd to include the <p> text
            except:
                pass  # If no <p> element is found, continue with the existing genus_dd

            f.write(f"{genus_dt}: {genus_dd}")

        except Exception as e:
            print("Error extracting text:", e)

driver.quit()
