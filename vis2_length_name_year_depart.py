#!/usr/bin/env python
# coding: utf-8
import altair as alt
import pandas as pd
import json

import geopandas as gpd
from io import BytesIO
import requests


def visualisation2():
    dep = gdf.merge(df_final, how='right', left_on='code', right_on='dpt')
    dep['moyenne_longueur'] = dep['moyenne_longueur'].fillna(0).astype(int)
    dep = dep.dropna(subset=['geometry'])

    # Version en convertissant le GeoDataFrame en JSON pour Altair
    dep = dep.explode(index_parts=False)
    dep_json = json.loads(dep.to_json())
    # Paramètre pour l'année (avec un slider)
    year_param = alt.selection_point(
        fields=["properties.annais"],
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
        fields=["properties.sexe"],
        bind=alt.binding_radio(
            name="Sexe :", 
            options=[1, 2],
            labels=['♂ Homme', '♀ Femme']
        ),
        value=1
    )

    carte = alt.Chart(alt.Data(values=dep_json["features"])).mark_geoshape(
        stroke='white'
    ).encode(
        color=alt.Color("properties.moyenne_longueur:Q", scale=alt.Scale(scheme='viridis'), title="Longueur moyenne"),
        tooltip=[
            alt.Tooltip("properties.nom:N", title="Département"),
            alt.Tooltip("properties.code:N", title="Code"),
            alt.Tooltip("properties.moyenne_longueur:Q", title="Longueur moyenne du prénom"),
            alt.Tooltip("properties.preusuel:N", title="Prénom le plus populaire")
        ]
    ).add_params(
        gender_param,
        year_param
    ).transform_filter(
        gender_param & year_param
    ).project(
        type='mercator'
    ).properties(
        width=600,
        height=600
    )
    return carte

### --- MAIN --- ###
alt.data_transformers.enable('json')

# --- Nettoyer le dataset ---
df = pd.read_csv("data/dpt2020.csv", sep=";")

to_clean=['annais', 'dpt']
for col in to_clean:
    df = df[df[col].str.isnumeric()]
    if col == 'annais':
        df[col] = df[col].astype(int)
    else:
        df[col] = df[col].astype("string")
        df.loc[df['dpt'] == '20', 'dpt'] = '2A'
        df = df[~df['dpt'].isin(['971', '972', '973', '974'])]

df = df[df["preusuel"] != "_PRENOMS_RARES"]
df["longueur"] = df["preusuel"].str.len()
df = df[df["longueur"] > 1]

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

# --- Préparation de la carte ---
url = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"
response = requests.get(url)
response.raise_for_status()
gdf = gpd.read_file(BytesIO(response.content))
gdf["geometry"] = gdf["geometry"].simplify(0.01)