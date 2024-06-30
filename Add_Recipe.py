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
}}
</style>
""",unsafe_allow_html=True)

# Apply the custom CSS
st.markdown(f'<div class="temp"></div>', unsafe_allow_html=True)
username=""
if len(sys.argv) > 1:
    username = sys.argv[1]
else:
    username = None

st.title(f"Add Your Recipe")
name = st.text_input("Recipe Name : ")
name = st.text_input("Cuisine : ")
name = st.text_input("Course : ")
name = st.text_input("Diet : ")
name = st.text_input("Instructions : ")
name = st.text_input("Cook Time : ")
name = st.text_input("Image_url : ")
button=st.button("Add")
