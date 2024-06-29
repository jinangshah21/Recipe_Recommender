import streamlit as st
import hashlib
import pymongo
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import subprocess

np.random.seed(1)
st.markdown(f"""
<style>
body {{
    width: 100vw;
    height: 100vh;
    background-image: url('https://images.pexels.com/photos/616401/pexels-photo-616401.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1');
    background-size: cover;
    background-repeat: no-repeat;

}}
</style>
""",unsafe_allow_html=True)

# Apply the custom CSS
st.markdown(f'<div class="temp"></div>', unsafe_allow_html=True)
def run_python_file(username, file_path):
    try:
        command = ["streamlit", "run", file_path, "--", f"{username}"]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, text=True)
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Users_Recipe_Recommendation"]
users_collection = db["Users_Profile"]
recipes_collection = db["Food_Recipe"]

# Define functions for registration, login, and recipe recommendation
def register(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = users_collection.find_one({"username": username})
    if user:
        return False
    else:
        user_data = {"username": username, "password": hashed_password, "rated": [], "favorites": []}
        users_collection.insert_one(user_data)
        st.write("User created successfully.")
        return True     

def login(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = users_collection.find_one({"username": username, "password": hashed_password})
    if user:
        st.success("Login successful.")
        return True
    else:
        st.write("Invalid username or password.")
        return False

# def recommend_recipes(ingredients):
#     # Placeholder function, replace with actual recommendation logic
#     return ["Recipe 1", "Recipe 2", "Recipe 3"]

# Streamlit UI components and logic
def main():
    st.title("Recipe Recommender")
    # Login/Register Section
    st.subheader("Login/Register")
    login_status = st.empty()
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    login_button = st.button("Login")
    register_button = st.button("Register")

    if login_button:
        if login(username, password):
            login_status.success("Welcome Back ! " + username)
            run_python_file(username,"Profile.py")
            return True
        else:
            login_status.error("Invalid username or password.")
            return False

    if register_button:
        check=register(username, password)
        if check:
            login_status.success("User registered successfully.")
        else :
            login_status.warning("Username already exists. Please choose a different username.")

cursor = recipes_collection.find()
data_list = list(cursor)

# Convert list of dictionaries to pandas DataFrame
recipes_data = pd.DataFrame(data_list)
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(recipes_data['search_words'])
# recipes_data.to_csv('Food_Recipe.csv', index=False)

if __name__ == "__main__":
    st.session_state.logged_in = False
    if main():
        st.session_state.logged_in = True
