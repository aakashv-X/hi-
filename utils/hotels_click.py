import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

def search_hotels(destination_city):
    # --- Configuration ---
    PAGE_URL = "https://www.ixigo.com/hotels"

    # --- WebDriver Setup ---
    options = webdriver.EdgeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Edge(options=options)
    driver.maximize_window()

    try:
        print(f"Navigating to {PAGE_URL}...")
        driver.get(PAGE_URL)

        wait = WebDriverWait(driver, 10)

        # --- 1. Handle Destination Input ---
        print(f"Locating and updating Destination input...")

        # Retry logic for StaleElementReferenceException
        for attempt in range(3):  # Try up to 3 times
            try:
                destination_input_locator = (By.XPATH, "//p[text()='Destination']/following-sibling::input")
                destination_input = wait.until(EC.element_to_be_clickable(destination_input_locator))

                destination_input.click()
                print("Clicked on the Destination input field.")

                destination_input.clear()
                destination_input.send_keys(destination_city)
                print(f"Entered '{destination_city}' into Destination input.")
                break
            except StaleElementReferenceException:
                print(f"StaleElementReferenceException occurred (attempt {attempt + 1}). Retrying...")
                time.sleep(1)
        else:
            print("Failed to locate and update Destination input after multiple attempts.")
            raise

        try:
            mumbai_option_locator = (By.XPATH, f"//div[@data-testid='{destination_city}' and @role='button']")
            mumbai_option = wait.until(EC.element_to_be_clickable(mumbai_option_locator))
            mumbai_option.click()
        except TimeoutException:
            print(f"Error: Timed out waiting for the '{destination_city}' dropdown item to be clickable.")
            raise
        except Exception as e:
            print(f"Error occurred while selecting '{destination_city}' from dropdown: {e}")
            raise

        # --- 3. Handle Search Button ---
        print("Locating Search button...")
        search_button_locator = (By.CSS_SELECTOR, 'button[data-testid="search-hotels"]')
        search_button = wait.until(EC.element_to_be_clickable(search_button_locator))
        print("Clicking Search button...")
        search_button.click()
        print("Search initiated successfully!")

        time.sleep(5)
        
        new_url = driver.current_url
        print(f"New URL: {new_url}")
        return new_url

    except TimeoutException:
        print("Error: Timed out waiting for one or more elements to load or become interactive.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()

# Example usage
if __name__ == "__main__":
    result_url = search_hotels("Srinagar")
    if result_url:
        print("Search completed successfully")
    else:
        print("Search failed")