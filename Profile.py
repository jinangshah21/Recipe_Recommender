import streamlit as st
import sys
import subprocess

st.markdown(f"""
<style>
body {{
    width: 100vw;
    height: 100vh;
    background-image: url('https://images.pexels.com/photos/616401/pexels-photo-616401.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1');
    background-size: cover;
    background-repeat: no-repeat;
    filter: blur(100px);
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

username=""
if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = None
st.image("img.jpg")
st.title(f"Welcome, {username}")
button1 = st.button("Explore Recipes")
button2 = st.button("Add Recipe")
button3 = st.button("My Favourites")

if button1:
   run_python_file(username,"RRS.py")

if button2:
    run_python_file(username,"Add_Recipe.py")

if button3:
    run_python_file(username,"Favourites.py")
