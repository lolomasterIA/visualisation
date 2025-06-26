#!/usr/bin/env python
# coding: utf-8

import altair as alt
import pandas as pd
import numpy as np
import plotly.graph_objs as go

def visualisation3():
    # Creating slider
    annee_slider = alt.binding_range(
        min=df_gender_pie['annais'].min(),
        max=df_gender_pie['annais'].max(),
        step=1,
        name="Year:"
    )

    # Connecting the slider to a parameter
    annee_param = alt.param(
        name="year",
        bind=annee_slider,
        value=df_gender_pie['annais'].min()
    )

    # Create pie charts r
    base = alt.Chart(df_gender_pie).transform_filter(
        alt.datum.annais == annee_param
    ).transform_window(
        rank='rank(nombre)',
        sort=[alt.SortField('nombre', order='descending')],
        groupby=["sexe"]
    ).transform_calculate(
        fin_affiche="datum.rank <= 10 ? datum.fin : 'others'"
    ).transform_aggregate(
        nombre='sum(nombre)',
        groupby=['sexe', 'fin_affiche']
    ).transform_window(
        order_rank='rank(-datum.nombre)',
        sort=[alt.SortField('nombre', order='descending')],
        groupby=["sexe"]
    ).transform_calculate(
        sexe_label="datum.sexe == 1 ? 'Homme' : 'Femme'"
    ).mark_arc().encode(
        theta=alt.Theta("nombre:Q", stack=True),
        color=alt.Color("fin_affiche:N", title="Ending"),
        column=alt.Column("sexe_label:N", title="Gender"),
        tooltip=["fin_affiche:N", "nombre:Q"]
    ).add_params(
        annee_param
    ).properties(
        title="Top name endings by gender grouped by year"
    )

    return base

### --- MAIN --- ###
alt.data_transformers.enable('json')

# --- Nettoyer le dataset ---
df = pd.read_csv("data/dpt2020.csv", sep=";")

to_clean = ['annais', 'dpt']
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

df['fin'] = df['preusuel'].str[-1].str.lower()

# --- Prepare Data for Pie Chart ---
df_gender_pie = df.groupby(['annais', 'fin', 'sexe'])['nombre'].sum().reset_index()