import json
import os
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from urllib.parse import quote
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import deque

# Update DATA_DIR to point to root data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# edge_driver_path = r"D:\msedgedriver.exe"  # Replace with your path
options = EdgeOptions()
options.add_argument("--headless=new")  # Use new headless mode (Edge/Chrome >= 109)
options.add_argument("--disable-gpu")
options.add_argument("--force-device-scale-factor=0.05")
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36")


def access_ixigo(url=None, from_airport=None, to_airport=None):
    """
    Accesses the Ixigo flight search website and extracts flight information.
    If URL is provided, uses that instead of constructing one from parameters.
    """
    try:
        # service = EdgeService(executable_path=edge_driver_path)
        driver = webdriver.Edge(options=options)

        if url:
            driver.get(url)
        else:
            print("No URL provided for flight scraping")
            return None

        time.sleep(5)  # Allow time for page to load and flights to populate
        

        print("Page Title:", driver.title)

        flight_data = extract_ixigo_flight_data(driver, from_airport, to_airport, url)

        # Save flight data to JSON file
        output_file = os.path.join(DATA_DIR, 'ixigo_flights.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(flight_data, f, indent=4, ensure_ascii=False)

        print(f"Flight data saved to {output_file}")

        driver.quit()
        return flight_data

    except Exception as e:
        print(f"An error occurred in flight scraping: {e}")
        if 'driver' in locals():
            driver.quit()
        return None


def extract_ixigo_flight_data(driver, from_airport, to_airport, url=None):
    """
    Extracts flight data from the Ixigo search results page,
    extracting both structured data and using BeautifulSoup to parse the HTML.

    Args:
        driver: Selenium WebDriver instance.

    Returns:
        A list of dictionaries, where each dictionary represents a flight.
    """
    # WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="shadow-[0px_2px_5px_0px_rgba(0,0,0,0.10)] p-15 mb-20  rounded-10 relative cursor-pointer bg-white border border-white transition-all duration-300 ease-in hover:scale-[1.01] hover:shadow-300 hover:duration-300 hover:ease-out"]'))
    #     )

    flight_data = []  # Use deque for efficient appending
    flight_cards_data = []
    flight_cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'cursor-pointer')]")
    # for  flight_card in flight_cards:
    #     print(flight_card)
    print(len(flight_cards))
    for card in flight_cards:
        try:
            # **Scroll to the element before extracting**
            # driver.execute_script("arguments[0].scrollIntoView();", card)
            time.sleep(0.5)  # Give it a brief pause to fully load after scrolling

            # **Extract the HTML**
            html_string = card.get_attribute('outerHTML')

            # **Parse the HTML with BeautifulSoup**
            flight = extract_flight_data_from_html(html_string,from_airport,to_airport,url)  # Use the parsing function

            flight_data.append(flight)

        except Exception as e:
            print(f"Error extracting data from a flight card: {e}")
            continue

    return flight_data


def extract_flight_data_from_html(html_string,from_airport=None,to_airport=None,url=None):
    """
    Extracts specific flight data from the HTML of a flight card using BeautifulSoup.
    This function extracts:
    - Fastest flight indicator
    - Airline
    - Departure Time
    - Arrival Time
    - Flight Duration
    - Stops
    - Price
    """
    soup = BeautifulSoup(html_string, 'html.parser')

    flight = {}
    flight['url'] = soup.find('a')['href'] if soup.find('a') else url
    
    loc = soup.find("div",class_="flex items-center justify-between")
    
    flight['from_airport'] = loc.find_all("p",class_="body-sm")[0].text.strip() if loc and len(loc.find_all("p")) > 0 else None #get the first element
    flight['to_airport'] = loc.find_all("p",class_="body-sm")[-1].text.strip() if loc and len(loc.find_all("p")) > 1 else None #get the second element

    # Fastest flight indicator
    fastest_element = soup.find('div', class_='text-selection-outline border-selection-outline min-h-20 icon-sm body-xs inline-flex items-center font-normal rounded-full px-px border border-solid bg-white')
    flight['fastest'] = True if fastest_element else False

    # Airline
    airline_element = soup.find('p', class_='body-sm body-sm')
    flight['airline'] = airline_element.text.strip() if airline_element else None

    # Departure Time
    departure_time_element = soup.find('h5', class_='h5 text-primary font-medium')
    flight['departure_time'] = departure_time_element.text.strip() if departure_time_element else None

    # Arrival Time (look for the element with GOX as destination which is now generic GOI)
    arrival_time_element = soup.find_all('h5', class_='h5 text-primary font-medium')[1]
    flight['arrival_time'] = arrival_time_element.text.strip() if len(soup.find_all('h5', class_='h5 text-primary font-medium')) > 1 and arrival_time_element else None #get the second element

    # Flight Duration
    duration_element = soup.find('div', class_='text-center')
    flight['duration'] = duration_element.find_all('p')[0].text.strip() if duration_element and len(duration_element.find_all('p')) > 0 else None #get the second element
    flight['stop'] = duration_element.find_all('p')[1].text.strip() if duration_element and len(duration_element.find_all('p')) > 1 else None #get the first element
    # Stops
    # stops_element = soup.find_all('p', class_='body-sm text-secondary')
    # flight['stops'] = stops_element[1].text.strip() if len(stops_element) > 1 and stops_element[1] else None #get the second element


    # Price
    price_element = soup.find('h5', {'data-testid': 'pricing'})
    flight['price'] = price_element.text.strip() if price_element else None

    return flight

# Example usage:
if __name__ == "__main__":
    access_ixigo()