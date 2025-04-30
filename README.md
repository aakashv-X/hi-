# traveLLex - Travel Website

A beautiful and modern travel website built with Flask, offering features for travelers to explore destinations, plan trips, and book travel experiences.

## Project Structure

```
traveLLex/
├── app.py                   # Main Flask application
├── requirements.txt         # Python dependencies
├── static/                  # Static files
│   ├── css/                 # CSS stylesheets
│   │   └── main.css         # Main CSS file
│   ├── js/                  # JavaScript files
│   │   └── main.js          # Main JS file
│   └── images/              # Image assets
└── templates/               # HTML templates
    ├── index.html           # Homepage
    ├── login.html           # Login page
    ├── register.html        # Registration page
    ├── plan_trip.html       # Trip planning page
    └── destinations.html    # Destinations page
```

## Features

- Responsive modern UI design
- Destination exploration and filtering
- Trip planning tool
- User authentication system (frontend only in this version)
- Destination categories and search

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation & Setup

1. Clone the repository
   ```
   git clone <repository-url>
   cd traveLLex
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   ```

3. Activate the virtual environment
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies
   ```
   pip install -r requirements.txt
   ```

5. Run the application
   ```
   python app.py
   ```

6. Access the website at http://127.0.0.1:5000

## Missing Resources

This repository contains only the code files. For a complete working version, you'll need to add the following image files to the `static/images/` directory:

- hero-bg.jpg
- login-bg.jpg
- register-bg.jpg
- cta-bg.jpg
- destination-1.jpg through destination-9.jpg
- testimonial-1.jpg through testimonial-3.jpg

## License

This project is for demonstration purposes.

## Acknowledgments

- Poppins font from Google Fonts
- Font Awesome for icons
- Flask for the web framework 