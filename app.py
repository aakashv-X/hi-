from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
import os
from datetime import datetime, timedelta
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from models import db, User, Trip, SavedDestination
from utils.scrape_data import start_scraping

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for session
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travellexdb.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create data directory if not exists
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Create database tables
with app.app_context():
    db.create_all() 
    # Create admin user if it doesn't exist
    if not User.query.filter_by(email='aakashv065@gmail.com').first():
        admin = User(
            name='Admin',
            email='aakashv065@gmail.com',
            is_admin=True
        )
        admin.password = '@aakashV065'
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.verify_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
            
    return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('home'))
        
        user = User(
            name=name,
            email=email
        )
        user.password = password
        
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('home'))
        
    return redirect(url_for('home'))

@app.route('/plan-trip')
@login_required
def plan_trip():
    return render_template('plan_trip.html')

@app.route('/destinations')
def destinations():
    return render_template('destinations.html')

@app.route('/profile')
@login_required
def profile():
    # Get all trips for the current user
    user_trips = Trip.query.filter_by(user_id=current_user.id).all()
    # Get all saved destinations for the current user
    saved_destinations = SavedDestination.query.filter_by(user_id=current_user.id).all()
    
    # Convert SQLAlchemy objects to dictionaries
    trips = []
    for trip in user_trips:
        trips.append({
            'id': trip.id,
            'destination': trip.destination,
            'start_date': trip.start_date,
            'end_date': trip.end_date,
            'travelers': trip.travelers,
            'status': trip.status
        })
    
    destinations = []
    for dest in saved_destinations:
        destinations.append({
            'id': dest.id,
            'name': dest.name,
            'location': dest.location,
            'price': dest.price,
            'rating': dest.rating
        })
    
    # Create user data dictionary
    user_data = {
        'id': current_user.id,
        'name': current_user.name,
        'email': current_user.email,
        'phone': current_user.phone,
        'dob': current_user.dob,
        'address': current_user.address,
        'city': current_user.city,
        'state': current_user.state,
        'zip': current_user.zip_code,
        'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
        'trips': trips,
        'saved_destinations': destinations
    }
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(user_data)
    
    # Otherwise render the profile template
    return render_template('profile.html', user=user_data)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.verify_password(password):
        login_user(user)
        return jsonify({
            'success': True,
            'redirect': url_for('home')
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid email or password'
    })

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({
            'success': False,
            'message': 'Email already registered'
        })
    
    user = User(
        name=name,
        email=email
    )
    user.password = password
    
    db.session.add(user)
    db.session.commit()
    
    login_user(user)
    return jsonify({
        'success': True,
        'redirect': url_for('home')
    })

@app.route('/generate-trip', methods=['POST'])
def generate_trip():
    try:
        data = request.json
        
        # Extract form data
        from_city = data.get('from_city')
        to_city = data.get('destination')
        from_date = data.get('start_date')
        to_date = data.get('end_date')
        num_adults = int(data.get('adults', 1))
        num_children = int(data.get('children', 0))
        num_infants = int(data.get('infants', 0))
        total_travelers = num_adults + num_children + num_infants
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
            from_date_display = datetime.strptime(from_date, '%Y-%m-%d').strftime('%d %B, %Y')
            from_date_api = datetime.strptime(from_date, '%Y-%m-%d').strftime('%d-%m-%Y')
        if to_date:
            to_date_display = datetime.strptime(to_date, '%Y-%m-%d').strftime('%d %B, %Y')
            to_date_api = datetime.strptime(to_date, '%Y-%m-%d').strftime('%d-%m-%Y')

        # Start scraping process
        start_scraping(
            from_city=from_city,
            to_city=to_city,
            from_date=from_date_api,
            to_date=to_date_api,
            num_adults=num_adults,
            num_children=num_children,
            num_infants=num_infants,
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
                'from_date': from_date_api,
                'to_date': to_date_api,
                'num_adults': num_adults,
                'num_children': num_children,
                'num_infants': num_infants,
                'budget': budget,
                'num_days': num_days
            }
            
            # If user is logged in, create a Trip record
            if current_user.is_authenticated:
                trip = Trip(
                    user_id=current_user.id,
                    destination=to_city,
                    start_date=from_date_display,
                    end_date=to_date_display,
                    travelers=total_travelers,
                    status='Upcoming'
                )
                db.session.add(trip)
                db.session.commit()
                
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

@app.route('/api/save-destination', methods=['POST'])
@login_required
def save_destination():
    data = request.json
    
    destination = SavedDestination(
        user_id=current_user.id,
        name=data.get('name'),
        location=data.get('location'),
        price=data.get('price'),
        rating=data.get('rating')
    )
    
    db.session.add(destination)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/remove-saved-destination/<int:destination_id>', methods=['DELETE'])
@login_required
def remove_saved_destination(destination_id):
    destination = SavedDestination.query.filter_by(id=destination_id, user_id=current_user.id).first()
    
    if destination:
        db.session.delete(destination)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Destination not found'})

@app.route('/api/check-login')
def check_login():
    """Check if the user is logged in and return user data if they are"""
    if current_user.is_authenticated:
        user_data = {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email
        }
        return jsonify({
            'authenticated': True,
            'user': user_data
        })
    else:
        return jsonify({
            'authenticated': False
        })

if __name__ == '__main__':
    app.run(debug=True)