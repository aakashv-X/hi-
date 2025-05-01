from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from bs4 import BeautifulSoup
import time
import json
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def access_ixigo(url=None):
    driver = None
    try:
        # Set up Edge options for headless mode
        options = EdgeOptions()
        options.add_argument("--headless=new")  # Use new headless mode (Edge/Chrome >= 109)
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36")

        # Path to your Edge WebDriver executable
        # edge_driver_path = "D:/msedgedriver.exe"

        # Initialize the Edge service and driver
        # service = EdgeService(executable_path=edge_driver_path)
        driver = webdriver.Edge(options=options)
        print("Browser started successfully")

        # Use provided URL or default
        if not url:
            print("No URL provided for train scraping")
            return None
        
        print(f"Accessing URL: {url}")
        driver.get(url)
        time.sleep(5)

        # Wait for the page to load dynamically
        try:
            print("Waiting for train listings to load...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "train-listing-row"))
            )
            print("Train listings loaded successfully")
        except TimeoutException:
            print("Timed out waiting for train listings to load.")
            return None

        # Get the page source after dynamic content has loaded
        html = driver.page_source
        print("Page source retrieved successfully")

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        trains_data = []

        # Find all train listing rows
        train_listings = soup.find_all('li')
        print(f"Found {len(train_listings)} train listings")

        # Iterate through the train listings and extract data
        for train_listing in train_listings:
            try:
                train_number = train_listing.find('span', class_='train-number').text
                train_name = train_listing.find('span', class_='train-name').text
                origin_station = train_listing.find('div', class_='left-wing').find('a').text
                destination_station = train_listing.find('div', class_='right-wing').find('a').text
                departure_time = train_listing.find('div', class_='left-wing').find('div', class_='time').text
                arrival_time = train_listing.find('div', class_='right-wing').find('div', class_='time').text

                train_data = {
                    'train_number': train_number,
                    'train_name': train_name,
                    'origin_station': origin_station,
                    'destination_station': destination_station,
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'classes': []
                }

                # Find available classes and their fares
                train_class_wrapper = train_listing.find('div', class_='train-class-wrapper')
                if train_class_wrapper:
                    train_classes = train_class_wrapper.find_all('div', class_='train-class-item')
                    for train_class in train_classes:
                        class_name = train_class.find('span', class_='train-class').text
                        try:
                            fare = train_class.find('div', class_='c-price-display').text
                        except:
                            fare = "NA"

                        availability_class = train_class.find('div', class_='avail-class').text

                        class_data = {
                            'class_name': class_name,
                            'fare': fare,
                            'availability': availability_class
                        }
                        train_data['classes'].append(class_data)
                        train_data["url"] = url

                trains_data.append(train_data)

            except Exception as e:
                print(f"Error extracting data from a train listing: {e}")
                continue

        print(f"Successfully extracted data for {len(trains_data)} trains")
        return trains_data

    except Exception as e:
        print(f"Error during web scraping: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            print("Browser closed successfully")

if __name__ == "__main__":
    
    # Example usage
    url = "https://www.ixigo.com/search/result/train/LKO/LTT/18052025//1/0/0/0/ALL"
    train_data = access_ixigo(url=url)
    if train_data:
        # Save train data to JSON file
        output_file = os.path.join(DATA_DIR, 'ixigo_trains.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(train_data, f, indent=4, ensure_ascii=False)

        print(f"Train data saved to {output_file}")
    else:
        print("No train data scraped")
