from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
bcrypt = Bcrypt(app)

# MongoDB setup
from config import MONGO_URI
client = MongoClient(MONGO_URI)
db = client.skin_disease_db
users_collection = db.users  # Users collection

# Load the model
MODEL_PATH = 'Model.h5'
model = load_model(MODEL_PATH)

# Define allowed extensions for uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_skin_disease(img_path):
    img = image.load_img(img_path, target_size=(228, 228))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    predictions = model.predict(img_array)[0]
    class_idx = np.argmax(predictions)
    confidence = predictions[class_idx]

    labels = ['Eczema', 'Warts Molluscum and other Viral Infections', 'Melanoma', 
              'Atopic Dermatitis', 'Basal Cell Carcinoma', 'Melanocytic Nevi', 
              'Benign Keratosis-like Lesions', 'Psoriasis pictures Lichen Planus and related diseases', 
              'Seborrheic Keratoses and other Benign Tumors', 'Tinea Ringworm Candidiasis and other Fungal Infections']

    return labels[class_idx], confidence

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    # Fetch user's previous searches (images, predictions, and actions)
    user = users_collection.find_one({'email': session['user']})

    if not user:
        flash("User not found in the database.", "error")
        return redirect(url_for('auth.login'))

    # Get image data or default to an empty list if no images found
    image_data = user.get('images', [])

    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded", 400
        file = request.files['file']
        if file and allowed_file(file.filename):
            # Save the file
            file_dir = 'static/user_images'
            os.makedirs(file_dir, exist_ok=True)
            filename = f"{int(time.time())}_{secure_filename(file.filename)}"
            filepath = os.path.join(file_dir, filename)
            file.save(filepath)

            # Make prediction
            prediction, confidence = predict_skin_disease(filepath)

            # Update the user's record in MongoDB
            users_collection.update_one(
                {'email': session['user']},
                {'$push': {
                    'images': {
                        'image_path': filepath,
                        'prediction': prediction,
                        'confidence': float(confidence)  # Convert numpy.float32 to Python float
                    }
                }}
            )

            # Reload the image data after adding the new entry
            image_data = users_collection.find_one({'email': session['user']}).get('images', [])

            return render_template('index.html', username=session['user'], image_data=image_data, prediction=prediction, confidence=confidence, image_path=filepath)

    return render_template('index.html', username=session['user'], image_data=image_data)


@app.route('/about')
def about():
    return "About this application"
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

    # Fetch the user’s image history from the MongoDB database
    user = users_collection.find_one({'email': session['user']})
    image_data = user.get('images', [])  # Retrieve the 'images' field for the user
    
    return render_template('history.html', username=session['user'], image_data=image_data)



# Import authentication routes
from auth_routes import auth_bp
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
