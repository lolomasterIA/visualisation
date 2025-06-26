'''
# Choix de visu
option = st.sidebar.radio("Choisir une visualisation :", ["Vue 1", "Vue 2", "Vue 3"])

# Affichage
if option == "Vue 1":
    st.subheader("Visualisation 1")
    st.plotly_chart(visu1(), use_container_width=True)

elif option == "Vue 2":
    st.subheader("Visualisation 2")
    st.altair_chart(visu2(), use_container_width=True)

elif option == "Vue 3":
    st.subheader("Visualisation 3")
    st.altair_chart(visu3(), use_container_width=True)
    
'''
    
import streamlit as st
import plotly.express as px
import pandas as pd
import base64

from vis1_longueurprenom import visu1
from vis2_length_name_year_depart import visu2
from vis3_gender_analysis import visu3

def get_img_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Chemin vers l'image .webp (dans le dossier "images")
img_base64 = get_img_as_base64("images/Blue_and_pink_clouds.webp")

# --- HEADER ---
# CSS avec fond d'écran
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/webp;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .title {{
        font-size: 40px;
        font-weight: 700;
        color: #A77FF9;
        margin-bottom: 2rem;
    }}
    .card {{
        background-color: #F0F0F0;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 10px #00000055;
    }}
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Dashboard interactif", layout="wide")
st.markdown("<h1 class='title'> 👼 Visualisation - Baby Names</h1>", unsafe_allow_html=True)

# --- GRAPHIQUES ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("Baby Name Lengths Over Time by Gender")
st.write("Evolution of baby names length by genre between 1900 and 2020. We can hover over the graph for information about the most popular name and the shortest one and see its evolution during time.")
st.plotly_chart(visu1(), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.subheader("Baby Name Lengths Across France")
st.write("A map of France showing the baby names length evolution during time and gender by selecting the gender and year to display. The most popular baby names in each department is also display by hovering on a specific department.")
st.altair_chart(visu2(), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.subheader("Trends in Name Endings by Gender")
st.write("visualization that explores how the final letters of baby names in France have evolved over time, with a focus on gender differences. It uses an interactive pie chart created with Altair, where users can move a slider to select a year from 1900 to 2020.")
st.altair_chart(visu3(), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)