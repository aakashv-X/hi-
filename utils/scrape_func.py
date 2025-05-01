import pandas as pd
from datetime import datetime
from .hotels_click import search_hotels

# Load the data
airports_df = pd.read_csv('data/airports_data.csv')
railways_df = pd.read_csv('data/railways_data.csv')

# Utility to get airport code from city name
def get_airport_code(city):
    result = airports_df[airports_df['City'].str.lower() == city.lower()]
    result = result[result['IATA Code'].notna()]
    if not result.empty:

        return result.iloc[-1]['IATA Code']
    
    result = airports_df[airports_df['State'].str.lower() == city.lower()]
    result = result[result['IATA Code'].notna()]
    if not result.empty:
        return result.iloc[-1]['IATA Code']
    return None

# Utility to get railway station code from city name
def get_station_code(city):
    result = railways_df[railways_df['District'].str.lower().str.contains(city.lower(), na=False)]
    # Convert 'Trains passing through' to numeric if it's not already
    result['Trains passing through'] = pd.to_numeric(result['Trains passing through'], errors='coerce')
    result = result.dropna(subset=['Trains passing through'])
    
    if not result.empty:
        # Sort and pick station with the highest train count
        result = result.sort_values(by='Trains passing through', ascending=False)
        return result.iloc[0]['Station Code']
    return None

# Main function
def generate_travel_links(from_city, to_city, from_date, to_date, no_adults, no_childrens):
    """
    Generates travel links for flights, trains and hotels.
    Returns a dictionary with URLs for each mode of transport.
    """
    # Convert date to required format
    from_date_str = datetime.strptime(from_date, "%d-%m-%Y").strftime("%d%m%Y")
    to_date_str = datetime.strptime(to_date, "%d-%m-%Y").strftime("%d%m%Y")
    
    # Get codes
    from_airport = get_airport_code(from_city)
    to_airport = get_airport_code(to_city)
    from_station = get_station_code(from_city)
    to_station = get_station_code(to_city)

    # Create links
    flight_url = None
    train_url = None
    hotel_url = None
    
    if from_airport and to_airport:
        flight_url = (
            f"https://www.ixigo.com/search/result/flight?"
            f"from={from_airport}&to={to_airport}&date={from_date_str}&returnDate={to_date_str}"
            f"&adults={no_adults}&children={no_childrens}&infants=0&class=e&source=Search+Form&hbs=true"
        )
    
    if from_station and to_station:
        train_url = (
            f"https://www.ixigo.com/search/result/train/"
            f"{from_station}/{to_station}/{from_date_str}//1/0/0/0/ALL"
        )
        
    hotel_url = search_hotels(destination_city=to_city)

    return {
        "flight_url": flight_url,
        "train_url": train_url,
        "hotel_url": hotel_url,
        "from_airport": from_airport,
        "to_airport": to_airport,
        "from_station": from_station,
        "to_station": to_station,
    }

if __name__ == "__main__":
  
# Example usage:
    links = generate_travel_links(
        from_city="Lucknow",
        to_city="Bangalore",
        from_date="27-04-2025",
        to_date="29-04-2025",
        no_adults=2,
        no_childrens=0
    )

    print("Flight URL:", links['flight_url'])
    print("Train URL:", links['train_url'])
    print("Hotel URL:", links['hotel_url'])
