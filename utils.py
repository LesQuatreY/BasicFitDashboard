import requests
import api_access

def nb_vict_aff(data):
    import pandas as pd
    return pd.date_range(data.name.date(), periods=2).isin(data.index.date)

def markdown(text, center=False, size="30px", color=None, sidebar=False):
    import streamlit as st
    text_to_center = ("<div style='text-align:center';>", "</div>") if center else ("", "")
    if sidebar:
        return st.sidebar.markdown(
            f"{text_to_center[0]}<span style='font-size:{size};color:{color};'>{text}</span>{text_to_center[1]}",
            unsafe_allow_html=True
        )
    else:
        return st.markdown(
            f"{text_to_center[0]}<span style='font-size:{size};color:{color};'>{text}</span>{text_to_center[1]}",
            unsafe_allow_html=True
        )

def clean_address(address):
    address = address.strip()  # Supprime les espaces en début et fin de la chaîne

    if " ZAC " in address:
        address = address.replace(" ZAC ", "%20")

    for word in ["Avenue", "Rue", "CC", "Boulevard", "Route", "Chemin"]:
        if word in address:
            parts = address.split(word)
            address = word + " " + parts[1].strip() + "," + " " + " " + parts[0]
            break

    return address

def geocoding(address):
    return requests.get(
            f"https://maps.googleapis.com/maps/api/geocode/json?address={clean_address(address)}&key={api_access.API_key}"
            ).json()["results"][0]["geometry"]["location"]

