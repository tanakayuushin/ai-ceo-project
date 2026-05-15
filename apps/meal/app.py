import json
import os
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), 'meals.json')

MEAL_TYPES = ['朝食', '昼食', '夕食', '間食']


def load_meals():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, encoding='utf-8') as f:
        return json.load(f)


def save_meals(meals):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(meals, f, ensure_ascii=False, indent=2)


@app.route('/')
def index():
    target = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    all_meals = load_meals()
    day_meals = [m for m in all_meals if m['date'] == target]

    # 食事タイプ別に整理
    grouped = {t: [] for t in MEAL_TYPES}
    for m in day_meals:
        if m['type'] in grouped:
            grouped[m['type']].append(m)

    total_cal = sum(m['calories'] for m in day_meals)

    # 前日・翌日
    dt = datetime.strptime(target, '%Y-%m-%d')
    prev_date = (dt - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (dt + timedelta(days=1)).strftime('%Y-%m-%d')
    today = date.today().strftime('%Y-%m-%d')

    return render_template('index.html',
        grouped=grouped,
        meal_types=MEAL_TYPES,
        total_cal=total_cal,
        target=target,
        prev_date=prev_date,
        next_date=next_date,
        today=today,
        is_today=(target == today)
    )


@app.route('/add', methods=['POST'])
def add():
    target = request.form.get('date', date.today().strftime('%Y-%m-%d'))
    name     = request.form.get('name', '').strip()
    meal_type = request.form.get('type', '昼食')
    calories = request.form.get('calories', '0').strip()

    if name:
        try:
            cal = int(calories)
        except ValueError:
            cal = 0
        meals = load_meals()
        meals.append({
            'id':       datetime.now().strftime('%Y%m%d%H%M%S%f'),
            'date':     target,
            'name':     name,
            'type':     meal_type,
            'calories': cal,
        })
        save_meals(meals)
    return redirect(url_for('index', date=target))


@app.route('/delete/<meal_id>', methods=['POST'])
def delete(meal_id):
    target = request.form.get('date', date.today().strftime('%Y-%m-%d'))
    meals = load_meals()
    meals = [m for m in meals if m['id'] != meal_id]
    save_meals(meals)
    return redirect(url_for('index', date=target))


if __name__ == '__main__':
    app.run(debug=True, port=5002)
