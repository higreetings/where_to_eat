from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_PATH = 'data/restaurants.json'

def load_data():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def is_open_now(restaurant):
    now = datetime.now()
    day = str(now.weekday()) if now.weekday() != 6 else "0"  # Sunday = 0
    time_now = now.strftime('%H:%M')
    hours = restaurant.get("hours", {})
    if day in hours:
        return hours[day]["open"] <= time_now <= hours[day]["close"]
    return False

@app.route('/', methods=['GET'])
def index():
    restaurants = load_data()
    for r in restaurants:
        r['status'] = 'Open' if is_open_now(r) else 'Closed'
    return render_template('index.html', restaurants=restaurants)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    hours = {}
    for i in range(7):
        open_time = request.form.get(f'open-{i}')
        close_time = request.form.get(f'close-{i}')
        if open_time and close_time:
            hours[str(i)] = { "open": open_time, "close": close_time }
    restaurant = { "name": name, "hours": hours }
    data = load_data()
    data.append(restaurant)
    save_data(data)
    return redirect('/')

@app.route('/delete/<int:index>')
def delete(index):
    data = load_data()
    if 0 <= index < len(data):
        data.pop(index)
        save_data(data)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
