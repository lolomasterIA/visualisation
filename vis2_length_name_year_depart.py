#!/usr/bin/env python
# coding: utf-8

# #### Attention:
# Ceci ne prend pas en compte les départements d'outre mer mais uniquement la métrople !! (je n'ai pas trouvé de carte fonctionnel)

# In[2]:
import altair as alt 
alt.data_transformers.enable('json')


# In[3]:


import pandas as pd
import plotly.graph_objs as go
import numpy as np


# In[4]:


df = pd.read_csv("data/dpt2020.csv", sep=";")

# In[5]:

# supp years and dpt = XXXX and transform to int
to_clean=['annais', 'dpt']
for col in to_clean:
    #df[col] = df[col].astype(str).str.strip()

    # Supprimer les lignes où la colonne n'est pas strictement numérique
    df = df[df[col].str.isnumeric()]

    if col == 'annais':
        df[col] = df[col].astype(int)

    else:
    # Reforcer le type string natif (facultatif mais propre)
        df[col] = df[col].astype("string")

        ### Ce n'est pas supported par la carte que nous avons ###
        # Transformation pour la corse => tout est transformé en 2A
        df.loc[df['dpt'] == '20', 'dpt'] = '2A'
        # Exclusion des DOM_TOM
        df = df[~df['dpt'].isin(['971', '972', '973', '974'])]


# In[6]:


# Supprimer les prénoms "_PRENOMS_RARES"
df = df[df["preusuel"] != "_PRENOMS_RARES"]
# Ajouter une colonne de longueur de prénom
df["longueur"] = df["preusuel"].str.len()
# Supprimer les prénoms de longueur 1
df = df[df["longueur"] > 1]


# In[8]:


max_nombre = df.groupby(['sexe', 'annais', 'dpt'])['nombre'].transform('max')
df_final = df[df['nombre'] == max_nombre]
# Tri décroissant puis suppression des duplicatas
df_final = (
    df.sort_values('nombre', ascending=False)
      .drop_duplicates(['sexe', 'annais', 'dpt'])
      .sort_values(by=['sexe', 'annais', 'dpt'])
)
moyenne_longueur = df.groupby(['sexe', 'annais', 'dpt'])['longueur'].transform('mean').round().astype(int)
df_final['moyenne_longueur'] = moyenne_longueur


# In[10]:


df_final[(df_final['annais'] == 2018) & (df_final['dpt'] == '46')]


# In[11]:

import geopandas as gpd
from io import BytesIO
import requests

def visu2():
    
    #Préparation de la carte
    url = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
    response = requests.get(url)
    response.raise_for_status()
    gdf = gpd.read_file(BytesIO(response.content))
    gdf["geometry"] = gdf["geometry"].simplify(0.01)

    dep = gdf.merge(df_final, how='right', left_on='code', right_on='dpt')
    dep['moyenne_longueur'] = dep['moyenne_longueur'].fillna(0).astype(int)
    dep = dep.dropna(subset=['geometry'])
    #dep[(dep['annais'] == 2018) &f (dep['dpt'] == '46')]

    #Widget pour la carte
    # Paramètre pour l'année (avec un slider)
    year_param = alt.selection_point(
        fields=["annais"],
        bind=alt.binding_range(
            min=dep['annais'].min(),
            max=dep['annais'].max(),
            step=1,
        name="Année :"
        ),
        value=dep['annais'].min()
    )

    # Paramètre pour le sexe (avec bouton radio)
    gender_param = alt.selection_point(
        fields=["sexe"],
        bind=alt.binding_radio(
            name="Sexe :", 
            options=[1, 2],
            labels=['♂ Homme', '♀ Femme']
        ),
        value=1
    )

    # Paramètre pour la longueur (avec liste déroulante)
    length_param = alt.selection_point(
        fields=["moyenne_longueur"], 
        bind=alt.binding_select(
            options=sorted(dep["moyenne_longueur"].dropna().unique()), 
            name="Longueur moyenne : "
        ),
        value=dep["moyenne_longueur"].iloc[0]  # Valeur par défaut
    )

    carte = alt.Chart(dep).mark_geoshape(
        stroke='white'
    ).encode(
        color=alt.Color("moyenne_longueur:Q", scale=alt.Scale(scheme='viridis'), title="Longueur moyenne"),
        tooltip=[
            alt.Tooltip("nom:N", title="Département"),
            alt.Tooltip("code:N", title="Code"),
            alt.Tooltip("moyenne_longueur:Q", title="Longueur moyenne du prénom"),
            alt.Tooltip("preusuel:N", title="Prénom le plus populaire")]
    ).add_params(
        gender_param,
        year_param
    ).transform_filter(
        gender_param,
        year_param
    ).project(
        type='mercator'
    ).properties(
        width=600,
        height=600
    )

    return carte