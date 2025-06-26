import streamlit as st

from vis1_longueurprenom import visu1
from vis2_length_name_year_depart import visu2
from vis3_gender_analysis import visu3

# Titre
st.set_page_config(page_title="Dashboard interactif", layout="wide")
st.title("Visualisations interactives du dataset")

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