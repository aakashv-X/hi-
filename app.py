from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True) 