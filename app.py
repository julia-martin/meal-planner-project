import os
from flask import Flask, flash, redirect, render_template, request, session, url_for, g
from flask_session.__init__ import Session
from markupsafe import escape
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import json
from cs50 import SQL

from datetime import datetime, date, timedelta
import calendar
import re

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = os.urandom(12).hex()
Session(app)

db = SQL(os.getenv("DATABASE_URL"))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.get_json():
            data = request.get_json()
            # For saving meals
            name = data['name']
            meal = data['meal']
            date = datetime.strptime(data['date'], '%A, %b %d, %Y')
            if 'key_ingred' in data:
                key_ingred = data['key_ingred']
            else:
                key_ingred = None
            if 'recipe' in data:
                recipe = data['recipe']
            else:
                recipe = None
            # Check if current entry exists
            existing = db.execute("SELECT * FROM meal_plans WHERE username = ? AND date = ? AND meal = ?", session['username'], date, meal)
            if len(existing) > 0:
                print(existing[0]['name'], existing[0]['key_ingred'])
                if (existing[0]['name'] != name or existing[0]['key_ingred'] != key_ingred or existing[0]['recipe'] != recipe):
                    db.execute("UPDATE meal_plans SET name = ?, key_ingred = ?, recipe = ? WHERE username = ? AND date = ? AND meal = ?", name, key_ingred, recipe, session['username'], date, meal)
            else:
                db.execute("INSERT INTO meal_plans (name, key_ingred, recipe, username, date, meal) VALUES(?, ?, ?, ?, ?, ?)",
                            name, key_ingred, recipe, session['username'], date, meal)
            return 'Saved Changes'

    else: # GET
        # If not logged in
        if 'username' not in session:
            return redirect('/login')

        day = datetime.today() - timedelta(days=datetime.today().weekday() % 7)
        dates = [day]
        for _ in range(6):
            day += timedelta(days=1)
            dates.append(day)
        dates = [x.strftime('%A, %b %d, %Y') for x in dates]
        if 'ingredients' not in session:
            session['ingredients'] = [row['ingredient'] for row in db.execute(
                "SELECT DISTINCT ingredient FROM ingredient_list WHERE username = ?", session['username'])]
        ingredients = session['ingredients']
        # Query for existing meal data
        meals = db.execute("SELECT * FROM meal_plans WHERE username = ?", session['username'])
        if len(meals) > 0:
            for row in meals:
                row['date'] = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S').strftime('%A, %b %d, %Y')
        else: meals = None
        return render_template('index.html', ingredients=ingredients, dates=dates, meals=meals)

@app.route('/ingredients', methods=['GET', 'POST'])
def ingredients():
    if request.method == 'POST':
        # For adding ingredients
        if request.form:  # if 'addItem' in request.form:
            session['ingredients'].append(request.form.get('addItem'))
            session.modified = True
            ingredients = session['ingredients']
            return render_template('ingredients.html', ingredients=ingredients)
        # For deleting items
        elif request.get_json(force=True):
            data = request.get_json(force=True)
            to_remove = data['delete']
            session['ingredients'].remove(to_remove)
            session.modified = True
            ingredients = session['ingredients']
            return render_template('ingredients.html', ingredients=ingredients)
    else: # GET
        if 'ingredients' not in session:
            session['ingredients'] = [row['ingredient'] for row in db.execute(
                "SELECT DISTINCT ingredient FROM ingredient_list WHERE username = ?", session['username'])]
        ingredients = session['ingredients']
        return render_template('ingredients.html', ingredients=ingredients)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check username
        user_lookup = db.execute("SELECT * FROM users WHERE username = ?", request.form['username'])
        if len(user_lookup) != 1:
            return render_template('login.html', error='User does not exist')
        session['username'] = request.form['username']
        # Check password
        if not check_password_hash(user_lookup[0]["hash"], request.form.get("password")):
            return render_template('login.html', error='Incorrect password. Please try again')
        return redirect('/')
    # GET
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Update ingredient list in table
    db.execute("DELETE FROM ingredient_list WHERE username = ?", session['username'])
    for ing in session['ingredients']:
        db.execute("INSERT INTO ingredient_list (username, ingredient) VALUES (?, ?)", session['username'], ing)
    session.pop('username', None)
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Check name and username
    if request.method == 'POST':
        if not request.form['name']:
            return render_template('register.html', error='Please enter your name')
        user_lookup = db.execute("SELECT * FROM users WHERE username = ?", request.form['username'])
        if len(user_lookup) > 0:
            return render_template('register.html', error='Username already taken')

        # Check password requirements
        def valid_password(password):
            if len(password) < 8:
                return False
            if not re.match(r'[A-Za-z0-9\_\-\%\&\@\$\*]', password):
                return False
            return True
        if valid_password(request.form['password']):
            # Insert into users table
            session['username'] = request.form['username']
            db.execute("INSERT INTO users (username, hash, time_created, name) VALUES (?, ?, ?, ?)",
                        request.form['username'], generate_password_hash(request.form['password']), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request.form['name'])
            return redirect('/')
    # GET
    return render_template('register.html')