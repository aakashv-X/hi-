import threading
import json
import time
import os
from queue import Queue
from .flight_scrape import access_ixigo as scrape_flights
from .trains_scrape import access_ixigo as scrape_trains
from .hotels_scrape import get_hotel_details
from .package_creator import main as create_packages
from .scrape_func import generate_travel_links

# Define data directory - point to root data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Shared data queues and completion flags
flight_data_queue = Queue()
train_data_queue = Queue()
hotel_data_queue = Queue()
scraping_complete = threading.Event()
package_creation_complete = threading.Event()

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def retry_scraper(scrape_func, **kwargs):
    """Helper function to implement retry logic for scrapers"""
    for attempt in range(MAX_RETRIES):
        try:
            data = scrape_func(**kwargs)
            if data:
                return data
            print(f"Attempt {attempt + 1} failed to get data, retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}, retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
    return None

def flight_scraper_thread(url, from_airport, to_airport):
    """Thread function to scrape flight data"""
    print(f"Starting flight scraping thread with URL: {url}")
    data = retry_scraper(scrape_flights, url=url, from_airport=from_airport, to_airport=to_airport)
    
    if data:
        with open(os.path.join(DATA_DIR, "ixigo_flights.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        flight_data_queue.put(data)
        print("Flight data scraped successfully")
    else:
        print("All flight scraping attempts failed")
        flight_data_queue.put(None)

def train_scraper_thread(url):
    """Thread function to scrape train data"""
    print(f"Starting train scraping thread with URL: {url}")
    data = retry_scraper(scrape_trains, url=url)
    
    if data:
        with open(os.path.join(DATA_DIR, "ixigo_trains.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        train_data_queue.put(data)
        print("Train data scraped successfully")
    else:
        print("All train scraping attempts failed")
        train_data_queue.put(None)

def hotel_scraper_thread(url):
    """Thread function to scrape hotel data"""
    print(f"Starting hotel scraping thread with URL: {url}")
    data = retry_scraper(get_hotel_details, url=url)
    
    if data:
        with open(os.path.join(DATA_DIR, "ixigo_hotel.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        hotel_data_queue.put(data)
        print("Hotel data scraped successfully")
    else:
        print("All hotel scraping attempts failed")
        hotel_data_queue.put(None)

def package_creator_thread(budget, num_adults, num_children, num_days):
    """Thread function to create packages when data becomes available"""
    print("Starting package creator thread")
    max_wait_time = 600  # 10 minutes maximum wait time
    start_time = time.time()
    
    # Store data outside the loop
    flights_data = None
    trains_data = None
    hotels_data = None
    
    while time.time() - start_time < max_wait_time:
        try:
            # Only get data if we haven't received it yet
            if flights_data is None and not flight_data_queue.empty():
                flights_data = flight_data_queue.get()
            if trains_data is None and not train_data_queue.empty():
                trains_data = train_data_queue.get()
            if hotels_data is None and not hotel_data_queue.empty():
                hotels_data = hotel_data_queue.get()
            
            print("Checking for available data...")
            try:
                if flights_data:
                    print(f"Flight data: {len(flights_data)} flights found")    
                if trains_data:
                    print(f"Train data: {len(trains_data)} trains found")
                if hotels_data:
                    print(f"Hotel data: {len(hotels_data)} hotels found")
            except:
                pass

            # If we have hotel data and at least one transportation option
            if hotels_data and (flights_data and trains_data):
                print("\nCreating packages with available data...")
                flights_json = json.dumps(flights_data) if flights_data else None
                trains_json = json.dumps(trains_data) if trains_data else None
                hotels_json = json.dumps(hotels_data)

                result = create_packages(
                    flights_json, hotels_json, trains_json,
                    budget, num_adults, num_children, num_days
                )
                print(f"Package creation result: {result}")
                package_creation_complete.set()
                break
            
            # Wait a bit before checking again
            time.sleep(5)
            print("Waiting for more data...")

        except Exception as e:
            print(f"Error in package creation: {e}")
            break

    if not package_creation_complete.is_set():
        print("Package creation timed out or failed")

def start_scraping(from_city, to_city, from_date, to_date, num_adults, num_children, num_infants, budget, num_days):
    """Main function to start all scraping threads"""
    print(f"\nStarting scraping process for {from_city} to {to_city}")
    print(f"Date range: {from_date} to {to_date}")
    
    # Reset events
    scraping_complete.clear()
    package_creation_complete.clear()
    
    # Generate travel links
    links = generate_travel_links(
        from_city=from_city,
        to_city=to_city,
        from_date=from_date,
        to_date=to_date,
        no_adults=num_adults,
        no_childrens=num_children,
        no_infants=num_infants
    )

    print("\nGenerated URLs:")
    print(f"Flight URL: {links['flight_url']}")
    print(f"Train URL: {links['train_url']}")
    print(f"Hotel URL: {links['hotel_url']}\n")

    # Create and start threads
    threads = []

    # Flight scraper thread
    if links['flight_url']:
        flight_thread = threading.Thread(
            target=flight_scraper_thread,
            args=(links['flight_url'],links['from_airport'], links['to_airport'])
        )
        threads.append(flight_thread)
        flight_thread.start()

    # Train scraper thread
    if links['train_url']:
        train_thread = threading.Thread(
            target=train_scraper_thread,
            args=(links['train_url'],)
        )
        threads.append(train_thread)
        train_thread.start()

    # Hotel scraper thread
    if links['hotel_url']:
        hotel_thread = threading.Thread(
            target=hotel_scraper_thread,
            args=(
                links['hotel_url'],
            )
        )
        threads.append(hotel_thread)
        hotel_thread.start()

    # Start the package creator thread after a short delay
    time.sleep(2)  # Give scrapers a head start
    package_thread = threading.Thread(
        target=package_creator_thread,
        args=(budget, num_adults, num_children, num_days)
    )
    threads.append(package_thread)
    package_thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    if package_creation_complete.is_set():
        print("\nAll scraping and package creation completed successfully!")
    else:
        print("\nProcess completed but package creation may have failed.")

if __name__ == "__main__":
    start_scraping(
        from_city="Lucknow",
        to_city="Kolkata",
        from_date="26-06-2025",
        to_date="30-06-2025",
        num_adults=2,
        num_children=1,
        num_infants=0,
        budget=40000,
        num_days=4
    )