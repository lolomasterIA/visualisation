#!/usr/bin/env python
# coding: utf-8

# # Baby Names in France – Visualization 3: Gender-Based Name Evolution
# This notebook focuses on analyzing the **gender effects** in baby naming trends in France from 1900 to 2020. We particularly explore whether endings of names (the last letter) correlate with gender preferences over time.

# ## Setup: Install and Import Required Libraries


# In[2]:
import altair as alt
alt.data_transformers.enable('json')


# In[3]:


# Basic imports
import pandas as pd
import numpy as np
import plotly.graph_objs as go


# ## Data Loading

# In[ ]:


df = pd.read_csv("data/dpt2020.csv", sep=";")

# ## Data Cleaning

# In[6]:

# Keep only rows where 'annais' and 'dpt' are strictly numeric (or well-formed)
to_clean = ['annais', 'dpt']
for col in to_clean:
    df = df[df[col].str.isnumeric()]

    if col == 'annais':
        df[col] = df[col].astype(int)
    else:
        df[col] = df[col].astype("string")
        df.loc[df['dpt'] == '20', 'dpt'] = '2A'  # Normalize Corsican code
        df = df[~df['dpt'].isin(['971', '972', '973', '974'])]  # Exclude DOM-TOM


# ## Name Cleaning and Feature Engineering

# In[6]:


# Remove rare/aggregate names
df = df[df["preusuel"] != "_PRENOMS_RARES"]
# Add name length
df["longueur"] = df["preusuel"].str.len()
# Remove single-letter names
df = df[df["longueur"] > 1]

# ## Extract Last Letter of Each Name

# In[8]:


df['fin'] = df['preusuel'].str[-1].str.lower()


# ## Prepare Data for Pie Chart

# In[9]:


# Aggregate by year and final letter
df_pie = df.groupby(['annais', 'fin'])['nombre'].sum().reset_index()

# ## Function to Aggregate Top 10 Terminations

# In[11]:

def top10_terminaisons(df_pie, annee):
    data_annee = df_pie[df_pie['annais'] == annee].copy()
    top5 = data_annee.nlargest(10, 'nombre')
    autres = data_annee[~data_annee['fin'].isin(top5['fin'])]
    autres_sum = autres['nombre'].sum()
    if autres_sum > 0:
        autres_row = pd.DataFrame([{
            'annais': annee,
            'fin': 'autres',
            'nombre': autres_sum
        }])
        top10 = pd.concat([top5, autres_row], ignore_index=True)
    return top10


# ## Interactive Visualization: Name Terminations Over Time

# In[15]:

def visu3():
    annee_slider = alt.binding_range(
        min=df_pie['annais'].min(),
        max=df_pie['annais'].max(),
        step=1,
        name="Année :"
    )
    annee_param = alt.param(
        name="année",
        bind=annee_slider,
        value=df_pie['annais'].min()
    )

    base = alt.Chart(df_pie).transform_filter(
        alt.datum.annais == annee_param
    ).transform_window(
        rank='rank(nombre)',
        sort=[alt.SortField('nombre', order='descending')]
    ).transform_calculate(
        fin_affiche="datum.rank <= 10 ? datum.fin : 'autres'"
    ).transform_aggregate(
        nombre='sum(nombre)',
        groupby=['fin_affiche']
    ).transform_window(
        order_rank='rank(-datum.nombre)',
        sort=[alt.SortField('nombre', order='descending')]
    ).mark_arc().encode(
        theta=alt.Theta("nombre:Q", stack=True),
        color=alt.Color(
            "fin_affiche:N",
            title="Terminaison",
            sort=alt.EncodingSortField(field="nombre", op="sum", order="descending")
        ),
        tooltip=["fin_affiche:N", "nombre:Q"]
    ).add_params(
        annee_param
    ).properties(
        title="Répartition des prénoms selon leur terminaison (top 10, autres regroupés)"
    )
    return base