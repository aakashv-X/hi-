from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
from utils.scrape_data import start_scraping

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session

# Create data directory if not exists
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/plan-trip')
def plan_trip():
    return render_template('plan_trip.html')

@app.route('/destinations')
def destinations():
    return render_template('destinations.html')

@app.route('/generate-trip', methods=['POST'])
def generate_trip():
    try:
        data = request.json
        
        # Extract form data
        from_city = data.get('from_city')
        to_city = data.get('destination')
        from_date = data.get('start_date')
        to_date = data.get('end_date')
        num_adults = int(data.get('travelers', 1))
        num_children = 0  # Default to 0 children since it's not in the form
        budget = float(data.get('budget', 25000))
        
        # Calculate number of days from date range
        if from_date and to_date:
            start = datetime.strptime(from_date, '%Y-%m-%d')
            end = datetime.strptime(to_date, '%Y-%m-%d')
            num_days = (end - start).days + 1
        else:
            num_days = 3  # Default if no dates provided

        # Convert dates to required format (DD-MM-YYYY)
        if from_date:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%m-%Y')
        if to_date:
            to_date = datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%m-%Y')

        # Start scraping process
        start_scraping(
            from_city=from_city,
            to_city=to_city,
            from_date=from_date,
            to_date=to_date,
            num_adults=num_adults,
            num_children=num_children,
            budget=budget,
            num_days=num_days
        )

        # Check if packages were generated
        packages_file = os.path.join(DATA_DIR, 'travel_packages.json')
        if os.path.exists(packages_file):
            # Store only the search parameters in session, not the full packages
            session['last_search'] = {
                'from_city': from_city,
                'to_city': to_city,
                'from_date': from_date,
                'to_date': to_date,
                'num_adults': num_adults,
                'num_children': num_children,
                'budget': budget,
                'num_days': num_days
            }
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'No packages generated'})
    
    except Exception as e:
        print(f"Error generating trip: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/packages')
def packages():
    # Read packages directly from file instead of session
    packages_file = os.path.join(DATA_DIR, 'travel_packages.json')
    packages_data = {}
    
    if os.path.exists(packages_file):
        try:
            with open(packages_file, 'r', encoding='utf-8') as f:
                packages_data = json.load(f)
        except json.JSONDecodeError:
            print("Error reading packages file")
    
    # Get search parameters from session if they exist
    search_params = session.get('last_search', {})
    
    return render_template('travel-package.html', 
                         packages=packages_data,
                         search_params=search_params)

if __name__ == '__main__':
    app.run(debug=False)