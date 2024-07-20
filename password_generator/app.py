from flask import Flask, render_template, request, redirect, url_for
import random
import string
from pymongo import MongoClient
from bson.objectid import ObjectId  # Add this import

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["password_generator"]
passwords_collection = db["passwords"]

def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def check_password_strength(password):
    length_criteria = len(password) >= 12
    digit_criteria = any(char.isdigit() for char in password)
    upper_criteria = any(char.isupper() for char in password)
    lower_criteria = any(char.islower() for char in password)
    special_criteria = any(char in string.punctuation for char in password)
    
    criteria_met = sum([length_criteria, digit_criteria, upper_criteria, lower_criteria, special_criteria])
    
    if criteria_met == 5:
        return "Strong"
    elif criteria_met >= 3:
        return "Medium"
    else:
        return "Weak"

@app.route("/", methods=["GET", "POST"])
def index():
    password = None
    strength = None
    if request.method == "POST":
        length = int(request.form["length"])
        password = generate_password(length)
        strength = check_password_strength(password)
        passwords_collection.insert_one({
            "length": length,
            "password": password,
            "strength": strength
        })
    return render_template("index.html", password=password, strength=strength)

@app.route("/passwords")
def passwords():
    passwords = list(passwords_collection.find())
    return render_template("passwords.html", passwords=passwords)

@app.route("/delete_password/<password_id>", methods=["POST"])
def delete_password(password_id):
    passwords_collection.delete_one({"_id": ObjectId(password_id)})
    return redirect(url_for("passwords"))

if __name__ == "__main__":
    app.run(debug=True)
