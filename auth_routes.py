from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from config import MONGO_URI

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client.skin_disease_db
users_collection = db.users

bcrypt = Bcrypt()

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!")
            return redirect(url_for('auth.register'))

        if users_collection.find_one({'email': email}):
            flash("Email already exists!")
            return redirect(url_for('auth.register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users_collection.insert_one({'email': email, 'password': hashed_password, 'images': []})

        flash("Registration successful! Please log in.")
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({'email': email})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user'] = email
            flash("Login successful!")
            return redirect(url_for('index'))
        else:
            flash("Invalid email or password!")

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("You have been logged out.")
    return redirect(url_for('auth.login'))
