import json
import config
import pandas as pd
import streamlit as st
import plotly.express as px

from streamlit_folium import st_folium
from utils import (markdown, geocoding)
from map import Map

# Configuration de la page
st.set_page_config(
    page_title="Basic fit Dashboard 💪",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="https://companieslogo.com/img/orig/BFIT.AS-f0360106.png?t=1664515365",
    menu_items={
    'Get Help': 'mailto:tanguy.minot@laposte.net',
    'About': "Dashboard by Tanguy Minot! 🧑‍💻"
    }
)

# Configuration avec des styles CSS pour les différents background
st.markdown('<style>{}</style>'.format(config.main_page_background), unsafe_allow_html=True)
st.markdown('<style>{}</style>'.format(config.sidebar_background), unsafe_allow_html=True)
st.markdown('<style>{}</style>'.format(config.sidebar_message_success), unsafe_allow_html=True)

#Affichage d'un titre
st.title("🔍 Basic fit Dashboard \n")

#Initialisation de la sidebar
file = st.sidebar.file_uploader("**Importer votre fichier Basic fit :**")

#Importation du fichier utilisateur
if file: 
    try:
        json_data = json.load(file)
        visits = json_data["visits"]
        df = pd.DataFrame(visits).assign(
            date=lambda x: x["date"] + " " + x["time"],
            club=lambda x: x.club.str.lstrip("Basic-Fit"),
            dow=lambda x: pd.to_datetime(x["date"]).dt.day_name()
        ).drop(["time"], axis=1).astype({"date": "datetime64"}).set_index("date")

        st.sidebar.success("✅ Fichier correctement importé")
    except:
        st.error("❌ Mauvais fichier importé. Veuillez importer le fichier json de l'application basic-fit/mes données.")
        st.sidebar.error("❌ Erreur dans l'importation du fichier !")
        st.stop()
else: 
    st.info("💡 Importer votre fichier BasicFit dans la barre latéral à gauche.")
    st.stop()

# """
# Création des différents dash
# """

# KPI's sur les entraînements
col1, col2, col3 = st.columns(3)
col1.metric(label="Nombre d'entraînements ", value=df.shape[0])
col2.metric(label="Nombre de basic-fit différents", value=len(df["club"].unique()))
close_days = (pd.to_datetime("2021-06-09") - pd.to_datetime("2020-10-29")).days
col3.metric(label="Nombre d'entraînements par semaine", value=round(7/(((df.index[0] - df.index[-1]).days-close_days)/(df.shape[0]+10)), 2))

# Top des basic-fit les plus visités
st.write("\n")
st.plotly_chart(
    px.bar(
        df.groupby("club").size().to_frame().rename(
            columns={0 : "visites"}
            ).sort_values("visites", ascending=False).query("visites>=5"), 
        y="visites", text_auto=True, title = "Top des basic-fit les plus visités", 
        color_discrete_sequence=["black"]
    ).update_layout(
        plot_bgcolor="rgba(0, 0, 0, 0)", 
        paper_bgcolor="rgba(0, 0, 0, 0)",
        xaxis_title=dict(font=dict(color='black')),
        xaxis=dict(tickfont=dict(color='black'), title=dict(font=dict(color='black'))),
        yaxis=dict(tickfont=dict(color='black'), title=dict(font=dict(color='black')))
    ).update_traces(textposition='auto', textfont=dict(color='white')),
    use_container_width=True
)

# Entraînements les plus tardif et les plus tôt.
col1, col2 = st.columns(2)
col1.write("**Entrainements les plus tôts :**")
col1.write(
    df.sort_values(
        "date", key=lambda x: x.map(lambda x: x.time()),ascending=True
    ).head(3).style.set_table_styles(
        [{
            'selector': 'table',
            'props': [('background-color', 'transparent')]
        }]
    ).render(),
    unsafe_allow_html=True
)
col2.write("**Entrainements les plus tardifs :**")
col2.write(
    df.sort_values(
        "date", key=lambda x: x.map(lambda x: x.time()),ascending=False
    ).head(3).style.set_table_styles(
        [{
            'selector': 'table',
            'props': [('background-color', 'transparent')]
        }]
    ).render(),
    unsafe_allow_html=True
)

# Entraînements par jour de la semaine
st.plotly_chart(
    px.bar(df.groupby("dow").count().rename(
        columns={"club" : "nb_training"}
        ).loc[["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],:],
        y="nb_training", text_auto=True, title= "Entraînements par jour de la semaine",
        color_discrete_sequence = ["black"]*7
    ).update_layout(
    { "plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)", 
      "xaxis_title": dict(text="Nombre d'entraînements", font=dict(color='black')),
      "yaxis_title": dict(text="Jour de la semaine", font=dict(color='black')),
      "xaxis": dict(tickfont=dict(color='black'), title=dict(font=dict(color='black'))),
      "yaxis": dict(tickfont=dict(color='black'), title=dict(font=dict(color='black')))
    }
),use_container_width=True
)

# Histogramme du nbr entraînement par heure la semaine et le week end
st.plotly_chart(
    px.histogram(
        df.assign(we=[i*"Week-end"+(not i)*"Semaine" for i in list(df["dow"].isin(['Saturday', 'Sunday']))]).set_index(
            df.index.hour
        ).reset_index(names="hour").groupby(["hour","we"]).size().to_frame(name="count").reset_index(),
        x="hour", y="count", text_auto=True, title= "Entraînements par heure le week-end ou la semaine",
        color="we", barmode="group", nbins=17, color_discrete_map={"Semaine": "orange", "Week-end": "black"}, labels={"hour": "Heure", "we": ""}
    ).update_layout(
        { 
            "plot_bgcolor": "rgba(0, 0, 0, 0)", 
            "paper_bgcolor": "rgba(0, 0, 0, 0)", 
            "xaxis_title": {"font": {"color": "black"}},
            "xaxis": {
                "tickfont": {"color": "black"}, 
                "title": {"font": {"color": "black"}}
            },
            "yaxis": {
                "tickfont": {"color": "black"}, 
                "title": {
                    "text": "Nombre d'entraînements", 
                    "font": {"color": "black"}
                }
            }
        }
    ).update_traces(textposition='auto', textfont=dict(color='white')),
    use_container_width=True
)

# Affichage de la carte de tous les basic fit visités
mapper=Map()
result = mapper.map(df["club"].unique().tolist())

# Affichage des basic fit non placés (si necessaire)
if result[1]:
    for erreur in result[1]:
        st.write(erreur)

# Affichage de la carte
markdown("Points de tous les basic-fit visités",size="20px",center=True)
st_folium(result[0], returned_objects=[""], width=800, height=600)

# Affichage des séances les plus éloignées en distances
st.write(geocoding("Bagneux Avenue Aristide Briand"))
