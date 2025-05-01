from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os
from urllib.parse import urlencode

# Update DATA_DIR to point to root data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_hotel_details(url=None):
    driver = None
    try:
        # Set up Edge WebDriver
        options = EdgeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Edge(options=options)
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds

        if not url:
            print("No URL provided for hotel scraping")
            return None
        
        driver.get(url)
        
        # Wait for first hotel card to appear instead of fixed delay
        wait.until(EC.presence_of_element_located((By.XPATH, "//a[@target='_blank' and @rel='nofollow']")))

        def scroll_to_bottom():
            old_position = 0
            new_position = None
            scroll_attempts = 0
            max_attempts = 20  # Limit maximum scrolls

            while new_position != old_position and scroll_attempts < max_attempts:
                old_position = driver.execute_script("return (window.pageYOffset || document.documentElement.scrollTop);")
                
                # Scroll in smaller increments
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(1)  # Reduced wait time
                
                new_position = driver.execute_script("return (window.pageYOffset || document.documentElement.scrollTop);")
                scroll_attempts += 1
                
                # Break if we're at the bottom
                if new_position == old_position:
                    break

        # Scroll to load content
        scroll_to_bottom()

        # Use WebDriverWait to find hotel cards
        hotel_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[@target='_blank' and @rel='nofollow']")))
        print("Hotel cards found:", len(hotel_cards))
        
        # Rest of the code remains same...
        hotel_data = []
        for card in hotel_cards:
            try:
                hotel_name = card.find_element(By.XPATH, ".//h2[@data-testid='hotel-name']").text
                location = card.find_element(By.XPATH, ".//p[@class='body-sm word-break   break-words text-secondary']").text
                try:
                    rating = card.find_element(By.XPATH, ".//div[@class='flex items-center justify-center rounded-5 bg-inverse mr-10']/p").text
                    num_ratings = card.find_element(By.XPATH, ".//p[@class='body-sm  text-secondary font-normal']").text
                except:
                    rating = "N/A"
                    num_ratings = "N/A"
                price = card.find_element(By.XPATH, ".//div[@class='h5 text-right text-primary font-medium']").text
                offering = [off.text for off in card.find_elements(By.XPATH, ".//p[@data-testid='offering']")]
                link = card.get_attribute("href")

                try:
                    discount= card.find_element(By.XPATH, ".//div[@class='bg-success-subtle text-success-subtle border-success-subtle min-h-30px icon-md body-sm inline-flex items-center font-normal rounded-full px-1 border border-solid mb-5']/span").text
                except:
                    discount = "N/A"

                try:
                    original_price = card.find_element(By.XPATH, ".//p[@class='body-xs mr-5  line-through decoration-neutral-600 text-secondary']").text
                except:
                    original_price = "N/A"

                # Extract stars (number of star icons)
                stars = len(card.find_elements(By.XPATH, ".//svg[@data-testid='starActive']"))

                 #Extract images src
                images = [img.get_attribute('src') for img in card.find_elements(By.XPATH,".//img[@loading='eager']")]

                try:
                    taxes = card.find_element(By.XPATH, ".//p[@class='body-xs  text-secondary']").text
                except:
                    taxes = "N/A"

                hotel_info = {
                    "name": hotel_name,
                    "location": location,
                    "rating": rating,
                    "number_of_ratings": num_ratings,
                    "price": price,
                    "offering": offering,
                    "link": link,
                    "discount": discount,
                    "original_price": original_price,
                    "stars": stars,
                    "images": images,
                    "taxes": taxes,
                    "per_night_per_room": "per night, per room"
                }
                hotel_data.append(hotel_info)

            except Exception as e:
                print(f"Error extracting data from a card: {e}")

        # Save hotel data to JSON file
        output_file = os.path.join(DATA_DIR, 'ixigo_hotel.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(hotel_data, f, indent=4, ensure_ascii=False)

        print(f"Hotel data saved to {output_file}")

        return hotel_data

    except Exception as e:
        print(f"Error during hotel scraping: {e}")
        return None
    finally:
        if driver:
            driver.quit()
            print("Browser closed successfully")


# # Example usage
# location_id = 32
# location_name = "Mumbai"
# checkin_date = "17042025"
# checkout_date = "22042025"
# adult_count = 2
# room_count = 1
# child_count = 0
# msedgedriver_path = 'D:/msedgedriver.exe'  # Replace with the actual path to your msedgedriver.exe
# headless = False # set True to run without browser

# hotel_details = get_hotel_details(location_id, location_name, checkin_date, checkout_date, adult_count, room_count, child_count, msedgedriver_path, headless)

# # Save the hotel data to a JSON file
# filename = "ixigo_hotel_details.json"
# try:
#     with open(filename, 'w', encoding='utf-8') as f:
#         json.dump(hotel_details, f, indent=4)
#     print(f"Hotel details saved to {filename}")
# except Exception as e:
#     print(f"Error saving to JSON: {e}")