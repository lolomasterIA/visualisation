#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import plotly.graph_objs as go
import geopandas as gpd

def prenom_plus_court(groupe):
    mini = groupe[groupe["longueur"] == groupe["longueur"].min()]
    return mini.sort_values("nombre", ascending=False).iloc[0][["preusuel", "nombre"]]

def prenom_plus_utilisé(groupe):
    maxi = groupe[groupe["nombre"] == groupe["nombre"].max()]
    return maxi.iloc[0][["preusuel", "nombre"]]

def visualisation1():
    fig = go.Figure()

    # Garçons
    fig.add_trace(go.Scatter(
        x=moyennes.index, y=moyennes[1],
        mode='lines+markers',
        name='Filles',
        hovertext=[
            f"Plus court : {pc} ({int(nc)})<br>"
            f"Plus utilisé : {pf} ({int(nf)})"
            for annee, pc, nc, pf, nf in zip(
                moyennes.index,
                info["preusuel_m_court"], info["nombre_m_court"],
                info["preusuel_m_freq"], info["nombre_m_freq"]
            )
        ],
        line=dict(color='deeppink')
    ))

    # Filles
    fig.add_trace(go.Scatter(
        x=moyennes.index, y=moyennes[2],
        mode='lines+markers',
        name='Garçons',
        hovertext=[
            f"Plus court : {pc} ({int(nc)})<br>"
            f"Plus utilisé : {pf} ({int(nf)})"
            for annee, pc, nc, pf, nf in zip(
                moyennes.index,
                info["preusuel_f_court"], info["nombre_f_court"],
                info["preusuel_f_freq"], info["nombre_f_freq"]
            )
        ],
        line=dict(color='teal')
    ))

    fig.update_layout(
        title="Longueur moyenne des prénoms par année",
        xaxis_title="Année",
        yaxis_title="Nombre de lettres",
        hovermode="x unified",
        template="plotly_white"
    )

    return fig

### --- MAIN --- ###

# --- Nettoyer le dataset ---
df = pd.read_csv("data/dpt2020.csv", sep=";")
df = df[df["preusuel"] != "_PRENOMS_RARES"]
df["longueur"] = df["preusuel"].str.len()
df = df[df["longueur"] > 1]

moyennes = df.groupby(["annais", "sexe"])["longueur"].mean().unstack()

# --- Prénoms les plus courts ---
courts = df.groupby(["annais", "sexe"]).apply(prenom_plus_court).reset_index()
courts_pivot = courts.pivot(index="annais", columns="sexe", values=["preusuel", "nombre"])
courts_pivot.columns = ["preusuel_f_court", "preusuel_m_court", "nombre_f_court", "nombre_m_court"]

# --- Prénoms les plus utilisés ---
utilises = df.groupby(["annais", "sexe"]).apply(prenom_plus_utilisé).reset_index()
utilises_pivot = utilises.pivot(index="annais", columns="sexe", values=["preusuel", "nombre"])
utilises_pivot.columns = ["preusuel_f_freq", "preusuel_m_freq", "nombre_f_freq", "nombre_m_freq"]

# --- Fusion ---
info = pd.concat([courts_pivot, utilises_pivot], axis=1).sort_index()