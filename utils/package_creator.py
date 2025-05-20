import json
import os

# Update DATA_DIR to point to root data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Global configuration
HOTEL_FACTOR = 0.3  # Minimum ratio of hotel cost to total package cost
DEFAULT_BUDGET_INCREASE = 0.2  # 20% budget increase if no packages found

def find_affordable_hotels(hotels_data, hotel_budget_per_night, num_adults, num_children=0):
    """
    Finds affordable hotels that can accommodate the given number of adults and children,
    prioritizing costlier options and considering the number of rooms needed.
    """

    def calculate_rooms(adults, children):
        """
        Calculate the number of rooms needed based on the rules:
        - A maximum of 2 adults per room.
        - A maximum of 3 children per room.
        - If adults exceed 2 in a room, a new room is required.
        - If children exceed 3 in a room, a new room is required.
        """
        rooms = 0

        # Allocate rooms for adults (2 per room)
        adult_rooms = (adults + 1) // 2  
        remaining_adult_capacity = (adult_rooms * 2) - adults  

        # Allocate children to available space in adult rooms
        if children <= (adult_rooms * 3):  
            rooms = adult_rooms  # Children fit within the allocated adult rooms
        else:
            extra_children = children - (adult_rooms * 3)  
            child_only_rooms = (extra_children + 2) // 3  # Each room can fit 3 children
            rooms = adult_rooms + child_only_rooms  

        return rooms

    rooms_needed = calculate_rooms(num_adults, num_children)
    affordable_hotels = []

    for hotel in hotels_data:
        try:
            hotel_price = float(hotel["price"].replace("₹", "").replace(",", ""))
            total_hotel_cost_per_night = hotel_price * rooms_needed

            if total_hotel_cost_per_night <= hotel_budget_per_night:
                affordable_hotels.append((hotel, rooms_needed))
        except (KeyError, ValueError) as e:
            print(f"Error processing hotel data: {e}. Skipping hotel.")

    # Sort by the base price of the hotel in descending order (costlier first)
    if affordable_hotels:
        affordable_hotels.sort(key=lambda x: float(x[0]["price"].replace("₹", "").replace(",", "")), reverse=True)

    return affordable_hotels


def find_affordable_flights(flights_data, budget, num_adults, num_children, num_days):
    """Finds affordable flights based on the provided budget, prioritizing costlier options."""
    total_persons = num_adults + num_children  # Added to calculate per-person cost correctly
    affordable_flights = [
        flight for flight in flights_data if float(flight["price"].replace("₹", "").replace(",", "")) <= budget / (total_persons * num_days)
    ]
    if affordable_flights:
        affordable_flights.sort(key=lambda x: float(x["price"].replace("₹", "").replace(",", "")), reverse=True)
    return affordable_flights


def find_affordable_trains(trains_data):
    """Finds affordable trains with available seats, prioritizing costlier classes."""
    affordable_trains = []
    for train in trains_data:
        classes = sorted(train["classes"], key=lambda x: float(x["fare"]), reverse=True)
        for class_info in classes:
            try:
                fare = float(class_info["fare"])
                if "WL" not in class_info["availability"] or int(class_info["availability"].replace("WL", "")) < 50:
                    affordable_trains.append((train, class_info))
                    #break  # Take the most expensive available class
            except ValueError:
                pass
    return affordable_trains

def create_packages(transport_type, transport_data, hotels_data, budget, num_adults, num_children, num_infants, num_days):
    """Creates travel packages for a specific transport type (flight or train)."""
    total_persons = num_adults + num_children
    total_travelers = num_adults + num_children + num_infants
    packages = []
    
    if not transport_data:
        return packages

    if transport_type == "flight":
        for flight in transport_data:
            try:
                transportation_cost = float(flight["price"].replace("₹", "").replace(",", ""))
                transportation = flight
                transportation["type"] = "flight"
                remaining_budget = budget - (transportation_cost * total_persons)
                hotel_budget_per_night = (remaining_budget * 0.6) / num_days

                affordable_hotels = find_affordable_hotels(hotels_data, hotel_budget_per_night, num_adults, num_children)
                for hotel_tuple in affordable_hotels:
                    hotel, rooms_needed = hotel_tuple
                    hotel_cost_per_night = float(hotel["price"].replace("₹", "").replace(",", ""))
                    total_hotel_cost_per_night = hotel_cost_per_night * rooms_needed
                    estimated_activities_meals_cost = remaining_budget * 0.4
                    activities_meals_cost_per_day_per_person = estimated_activities_meals_cost / num_days / total_persons
                    total_estimated_cost = (transportation_cost * total_persons) + (total_hotel_cost_per_night * num_days) + estimated_activities_meals_cost
                    
                    min_threshold = 0.7 * budget
                    if total_estimated_cost < min_threshold:
                        continue  # Skip this package as it's too cheap
                    if (total_hotel_cost_per_night * num_days) < (HOTEL_FACTOR * total_estimated_cost):
                        continue  # Skip if hotel cost is too low

                    package = {
                        "transportation": transportation,
                        "hotel": hotel,
                        "rooms_needed": rooms_needed,
                        "num_adults": num_adults,
                        "num_children": num_children,
                        "num_infants": num_infants,
                        "total_travelers": total_travelers,
                        "num_days": num_days,
                        "total_transportation_cost": transportation_cost * total_persons,
                        "total_hotel_cost": total_hotel_cost_per_night * num_days,
                        "estimated_activities_meals_cost": estimated_activities_meals_cost,
                        "activities_meals_cost_per_day_per_person": activities_meals_cost_per_day_per_person,
                        "total_estimated_cost": total_estimated_cost,
                        "budget": budget
                    }
                    if package["total_estimated_cost"] <= budget:
                        packages.append(package)
            except Exception as e:
                print(f"Error creating flight package: {e}")
                continue

    elif transport_type == "train":
        for train, class_info in transport_data:
            try:
                transportation_cost = float(class_info["fare"])
                transportation = {
                    "train_number": train["train_number"],
                    "train_name": train["train_name"],
                    "origin_station": train["origin_station"],
                    "destination_station": train["destination_station"],
                    "departure_time": train["departure_time"],
                    "arrival_time": train["arrival_time"],
                    "class_name": class_info["class_name"],
                    "fare": class_info["fare"],
                    "availability": class_info["availability"],
                    "type": "train",
                    "url": train["url"]
                }
                remaining_budget = budget - (transportation_cost * total_persons)
                hotel_budget_per_night = (remaining_budget * 0.6) / num_days

                affordable_hotels = find_affordable_hotels(hotels_data, hotel_budget_per_night, num_adults, num_children)
                for hotel_tuple in affordable_hotels:
                    hotel, rooms_needed = hotel_tuple
                    hotel_cost_per_night = float(hotel["price"].replace("₹", "").replace(",", ""))
                    total_hotel_cost_per_night = hotel_cost_per_night * rooms_needed

                    estimated_activities_meals_cost = remaining_budget * 0.6
                    activities_meals_cost_per_day_per_person = estimated_activities_meals_cost / num_days / total_persons
                    total_estimated_cost = (transportation_cost * total_persons) + (total_hotel_cost_per_night * num_days) + estimated_activities_meals_cost
                    
                    min_threshold = 0.7 * budget
                    if total_estimated_cost < min_threshold:
                        continue  # Skip this package as it's too cheap
                    if (total_hotel_cost_per_night * num_days) < (HOTEL_FACTOR * total_estimated_cost):
                        continue

                    package = {
                        "transportation": transportation,
                        "hotel": hotel,
                        "rooms_needed": rooms_needed,
                        "num_adults": num_adults,
                        "num_children": num_children,
                        "num_infants": num_infants,
                        "total_travelers": total_travelers,
                        "num_days": num_days,
                        "total_transportation_cost": transportation_cost * total_persons,
                        "total_hotel_cost": total_hotel_cost_per_night * num_days,
                        "estimated_activities_meals_cost": estimated_activities_meals_cost,
                        "activities_meals_cost_per_day_per_person": activities_meals_cost_per_day_per_person,
                        "total_estimated_cost": total_estimated_cost,
                        "budget": budget
                    }
                    if package["total_estimated_cost"] <= budget:
                        packages.append(package)
            except Exception as e:
                print(f"Error creating train package: {e}")
                continue

    return packages


def main(flights_data_json, hotels_data_json, trains_data_json, budget, num_adults, num_children, num_infants, num_days, budget_increase_percentage=DEFAULT_BUDGET_INCREASE):
    """
    Orchestrates package creation, handling both flights and trains, and saves the result to a JSON file.
    If no packages are found, tries increasing the budget.
    """
    try:
        print("Starting package creation...")
        flights_data = json.loads(flights_data_json) if flights_data_json else None
        hotels_data = json.loads(hotels_data_json) if hotels_data_json else None
        trains_data = json.loads(trains_data_json) if trains_data_json else None

        if not hotels_data:
            print("No hotel data available")
            return "Error: No hotel data available"

        print("Finding affordable transportation options...")
        affordable_flights = find_affordable_flights(flights_data, budget, num_adults, num_children, num_days) if flights_data else []
        affordable_trains = find_affordable_trains(trains_data) if trains_data else []

        print(f"Found {len(affordable_flights)} affordable flights and {len(affordable_trains)} affordable trains")
        
        print("Creating packages...")
        flight_packages = create_packages("flight", affordable_flights, hotels_data, budget, num_adults, num_children, num_infants, num_days)
        train_packages = create_packages("train", affordable_trains, hotels_data, budget, num_adults, num_children, num_infants, num_days)

        all_packages = {
            "flight_packages": flight_packages,
            "train_packages": train_packages
        }

        if not flight_packages and not train_packages:
            print("No packages found with initial budget, trying with increased budget...")
            increased_budget = budget * (1 + budget_increase_percentage)
            affordable_flights = find_affordable_flights(flights_data, increased_budget, num_adults, num_children, num_days) if flights_data else []
            affordable_trains = find_affordable_trains(trains_data) if trains_data else []

            flight_packages = create_packages("flight", affordable_flights, hotels_data, increased_budget, num_adults, num_children, num_infants, num_days)
            train_packages = create_packages("train", affordable_trains, hotels_data, increased_budget, num_adults, num_children, num_infants, num_days)

            all_packages = {
                "flight_packages": flight_packages,
                "train_packages": train_packages
            }
            
            if not flight_packages and not train_packages:
                print("No suitable packages found even with increased budget.")
                return "No suitable flight or train packages found even with increased budget."

            increase_amount = increased_budget - budget
            print(f"Increased budget to ₹{increased_budget:.2f} (by ₹{increase_amount:.2f})")

        # Save results
        filename = os.path.join(DATA_DIR, "travel_packages.json")
        with open(filename, "w", encoding="utf-8") as outfile:
            json.dump(all_packages, outfile, indent=4, ensure_ascii=False)

        # Print summary
        print("\nPackage Creation Summary:")
        print(f"Flight Packages: {len(flight_packages)}")
        print(f"Train Packages: {len(train_packages)}")
        print(f"Saved all packages to {filename}")
        
        return "Successfully created and saved packages"

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Example usage
    try:
        with open(os.path.join(DATA_DIR, "ixigo_trains.json"), "r", encoding="utf-8") as f:
            trains_data_json = f.read()
        with open(os.path.join(DATA_DIR, "ixigo_flights.json"), "r", encoding="utf-8") as f:
            flights_data_json = f.read()
        with open(os.path.join(DATA_DIR, "ixigo_hotel.json"), "r", encoding="utf-8") as f:
            hotels_data_json = f.read()

        result = main(
            flights_data_json,
            hotels_data_json, 
            trains_data_json,
            budget=50000,
            num_adults=2,
            num_children=1,
            num_infants=0,
            num_days=4
        )
        print(result)
    except FileNotFoundError as e:
        print(f"Error: Could not find required JSON files. {e}")
    except Exception as e:
        print(f"Error: {e}")