import pymongo.server_api
import streamlit as st
import hashlib
import pymongo
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import subprocess
import sys
from sklearn.metrics.pairwise import cosine_similarity
import random
import time

np.random.seed(1)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://jinang2110:jinu2110@cluster0.3aodk9n.mongodb.net/?retryWrites=true&w=majority&appName=cluster0",server_api=pymongo.server_api.ServerApi('1'))
db = client["Users_Recipe_Recommendation"]
users_collection = db["Users_Profile"]
recipes_collection = db["Food_Recipe"]

cursor = recipes_collection.find()
data_list = list(cursor)


# Convert list of dictionaries to pandas DataFrame
recipes_data = pd.DataFrame(data_list)
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(recipes_data['search_words'])


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

## Funct1
def add_recipe_to_favorites(username, recipe_id):
    result = users_collection.update_one(
        {"username": username},
        {"$addToSet": {"favorites": recipe_id}}
    )
    message=""
    if result.modified_count > 0:
       message="Recipe Added to your Favourites"
    else:
       message="Recipe Already exists in your Favourites"
    st.markdown(
    f"""
    <style>
    .popup {{
        position: fixed;
        top: 10%;
        left: 50%;
        transform: translateX(-50%);
        background-color: #1abc9c;
        color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        z-index: 1000;
    }}
    </style>
    """,
    unsafe_allow_html=True)
    st.markdown(f'<div class="popup">{message}</div>', unsafe_allow_html=True)
    time.sleep(2)
    st.markdown('<style>.popup{display: none;}</style>', unsafe_allow_html=True)


## Funct2
def recommend_recipe(ingredients, tfidf_matrix=tfidf_matrix, recipes_data=recipes_data):

    ingredients = [ingredient.lower() for ingredient in ingredients]
    input_search_words = ' '.join(ingredients)
    input_tfidf = tfidf.transform([input_search_words])
    similarity_scores = cosine_similarity(input_tfidf, tfidf_matrix)
    similarity_scores = list(enumerate(similarity_scores[0]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    similar_recipes_indices = [i[0] for i in similarity_scores[:5]]
    similar_recipes = recipes_data.iloc[similar_recipes_indices]
    return similar_recipes

##Func3
def add_rating(username, recipe_id, rating):
    # Update the user's rated recipes in the users_collection
    result = users_collection.update_one(
        {"username": username},
        {"$addToSet": {"rated": recipe_id}}
    )
    if result.matched_count>0:
        # If the recipe exists, update the rating and number of reviews
        number_of_reviews = int(recipes_data["number of reviews"][recipe_id]) + 1
        new_rating = ((recipes_data["rating"][recipe_id]*recipes_data["number of reviews"][recipe_id]) + rating) / number_of_reviews
        result1 = recipes_collection.update_one(
            {"id": recipe_id},
            {"$set": {"rating": float(new_rating), "number of reviews": int(number_of_reviews)}}
        )
       

# Streamlit UI components and logic
def main():

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'username' not in st.session_state:
        st.session_state.username = " "
    if not st.session_state.logged_in:
        st.title("Recipe Recommender")
        
        # Login/Register Section
        st.subheader("Login/Register")
        login_status = st.empty()
        user = st.text_input("Username")
        password = st.text_input("Password", type="password")

        login_button = st.button("Login")
        register_button = st.button("Register")

        if login_button:
            if login(user, password):
                st.session_state.logged_in = True
                st.session_state.username=user
                login_status.success("Welcome Back ! " + user)
                st.rerun()
                # run_python_file(username,"Profile.py")
            else:
                login_status.error("Invalid username or password.")

        if register_button:
            check=register(user, password)
            if check:
                login_status.success("User registered successfully.")
            else :
                login_status.warning("Username already exists. Please choose a different username.")
    
    else:
       
        st.subheader(f"Welcome back, {st.session_state.username}!")

        # Navigation buttons
        st.sidebar.image("img.jpg", use_column_width=True)
        
        selected_page = st.sidebar.radio("", ["Explore Recipes", "Add Recipe", "My Favorites"])
          
        if selected_page == "Explore Recipes":
            st.title("Recipe Recommender")
            ingredients_entry = st.text_input("Type In your Ingredients, Cuisine, Recipe name, Course here : ")
            session_state = st.session_state
            
            if "game_started" not in session_state:
                session_state.game_started = False

            if not session_state.game_started:
                play_button = st.button("Recommend")
                if play_button:
                    if ingredients_entry!='':
                        session_state.game_started = True
                    else : 
                        st.markdown(
                        f"""
                        <style>
                        .popup {{
                            position: fixed;
                            top: 10%;
                            left: 50%;
                            transform: translateX(-50%);
                            background-color: #ff9999;
                            color: white;
                            border-radius: 8px;
                            padding: 20px;
                            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                            z-index: 1000;
                        }}
                        </style>
                        """,
                        unsafe_allow_html=True)
                        st.markdown(f'<div class="popup">{"Please enter some ingredients, cuisine or Recipe name"}</div>', unsafe_allow_html=True)
                        time.sleep(2)
                        st.markdown('<style>.popup{display: none;}</style>', unsafe_allow_html=True)

            if session_state.game_started:
                ingredients = ingredients_entry.split()
                recipes = recommend_recipe(ingredients)
                names = list(recipes["name"])
                ids = list(recipes["id"])
                # Credit = list(recipes["By"])
                Descriptions = list(recipes["description"])
                Times = list(recipes["cook_time (in mins)"])
                images = list(recipes["image_url"])
                Ingredients = list(recipes["ingredients_quantity"])
                directions = list(recipes['instructions'])
                ratings = list(recipes['rating'])
                i = 0
                st.success(names[i])
                st.image(images[i],width=500,caption=names[i])
                st.write("Description : ",Descriptions[i])
                st.write("Ingredients : ",Ingredients[i])
                st.write("Directions : ",directions[i])
                st.write("Rating : ",ratings[i])
                button1 = st.button("Add to Favourites: " + names[i])
                rating = st.radio("Rating", options=[1, 2, 3, 4, 5],key=3)
                if st.button("Submit Review 1"):
                    if rating:
                        st.write("You rated the recipe :", rating)
                        add_rating(st.session_state.username,ids[i],rating)
                    else:
                        st.write("Please select a rating.")
                if button1:
                    add_recipe_to_favorites(st.session_state.username, ids[i])
                
                i = 1
                st.success(names[i])
                st.image(images[i],width=500,caption=names[i])
                st.write("Description : ",Descriptions[i])
                st.write("Ingredients : ",Ingredients[i])
                st.write("Directions : ",directions[i])
                st.write("Rating : ",ratings[i])
                button2 = st.button("Add to Favourites: " + names[i])
                rating1 = st.radio("Rating", options=[1, 2, 3, 4, 5],key=2)
                if st.button("Submit Review 2"):
                    if rating1:
                        st.write("You rated the recipe:", rating1)
                        add_rating(st.session_state.username,ids[i],rating1)
                    else:
                        st.write("Please select a rating.")
                if button2:
                    add_recipe_to_favorites(st.session_state.username, ids[i])
                i = 2
                st.success(names[i])
                st.image(images[i],width=500,caption=names[i])
                st.write("Description : ",Descriptions[i])
                st.write("Ingredients : ",Ingredients[i])
                st.write("Directions : ",directions[i])
                st.write("Rating : ",ratings[i])
                button3 = st.button("Add to Favourites: " + names[i])
                rating2 = st.radio("Rating", options=[1, 2, 3, 4, 5],key=1)
                if st.button("Submit Review 3"):
                    if rating2:
                        st.write("You rated the recipe:", rating2)
                        add_rating(st.session_state.username,ids[i],rating2)
                    else:
                        st.write("Please select a rating.")
                if button3:
                    add_recipe_to_favorites(st.session_state.username, ids[i])
                i = 3
                st.success(names[i])
                st.image(images[i],width=500,caption=names[i])
                st.write("Description : ",Descriptions[i])
                st.write("Ingredients : ",Ingredients[i])
                st.write("Directions : ",directions[i])
                st.write("Rating : ",ratings[i])
                rating3 = st.radio("Rating", options=[1, 2, 3, 4, 5],key=4)
                if st.button("Submit Review 4"):
                    if rating3:
                        st.write("You rated the recipe:", rating3)
                        add_rating(st.session_state.username,ids[i],rating3)
                    else:
                        st.write("Please select a rating.")
                button4 = st.button("Add to Favourites: " + names[i])
                if button4:
                    add_recipe_to_favorites(st.session_state.username, ids[i])
                i = 4
                st.success(names[i])
                st.image(images[i],width=500,caption=names[i])
                st.write("Description : ",Descriptions[i])
                st.write("Ingredients : ",Ingredients[i])
                st.write("Directions : ",directions[i])
                st.write("Rating : ",ratings[i])
                button5 = st.button("Add to Favourites: " + names[i])
                rating5 = st.radio("Rating", options=[1, 2, 3, 4, 5],key=5)
                if st.button("Submit Review 5"):
                    if rating5:
                        st.write("You rated the recipe:", rating5)
                        add_rating(st.session_state.username,ids[i],rating5)
                    else:
                        st.write("Please select a rating.")
                if button5:
                    add_recipe_to_favorites(st.session_state.username, ids[i])
        
        elif selected_page == "Add Recipe":
            st.title(f"Add Your Recipe")
            name = st.text_input("Recipe Name : ")
            name = st.text_input("Cuisine : ")
            name = st.text_input("Course : ")
            name = st.text_input("Diet : ")
            name = st.text_input("Instructions : ")
            name = st.text_input("Cook Time : ")
            name = st.text_input("Image_url : ")
            button=st.button("Add")
        
        elif selected_page == "My Favorites":
            st.title(f"{st.session_state.username}'s Favourites")

            # cursor = recipes_collection.find()
            # data_list = list(cursor)
            recipes_data = pd.DataFrame(data_list)

            user = users_collection.find_one({"username": st.session_state.username})

            for i in user['favorites']:
                st.success(recipes_data['name'][i])
                st.image(recipes_data['image_url'][i],width=500,caption=recipes_data['name'][i])
                st.write("Description : ",recipes_data['description'][i])
                st.write("Ingredients : ",recipes_data['ingredients_quantity'][i])
                st.write("Directions : ",recipes_data['instructions'][i])
                st.write("Rating : ",recipes_data['rating'][i])

            

if __name__ == "__main__":
    main()
        # st.session_state.logged_in = True