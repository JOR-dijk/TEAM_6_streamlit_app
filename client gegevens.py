import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.title("Client Gegevens Invoeren")

CSV_FILE = "vragen.csv"

# Inputvelden
naam = st.text_input("Wat is uw naam?")
leeftijd = st.number_input("Wat is uw leeftijd?", min_value=0, max_value=120, value=0)
gewicht = st.number_input("Wat is uw gewicht (in kilogram)?", min_value=0.0, value=0.0)
lengte = st.number_input("Wat is uw lengte? (in meter)", min_value=0.0, value=0.0)

# BMI Berekening
BMI = round(gewicht / (lengte**2), 2) if lengte > 0 else 0.0
st.write(f"**Berekend BMI:** {BMI}")

werk = st.text_input("Wat is uw werk?")
vrije_tijd = st.text_input("Wat doet u in uw vrije tijd?")

# Sport logica
sport_keuze = st.selectbox("Doet u aan sport?", ["maak een keuze", "Ja", "Nee"])
sport_welke = ""
sport_hoeveel = 0
if sport_keuze == "Ja":
    sport_welke = st.text_input("Welke sport doet u?")
    sport_hoeveel = st.number_input("Hoe veel uur per week sport u?", min_value=0)

# Roken logica
roken = st.selectbox("Doet u aan roken?", ["maak een keuze", "Ja", "Nee"])
roken_hoeveel = 0
if roken == "Ja":
    roken_hoeveel = st.number_input("Hoeveel sigaretten rookt u per dag?", min_value=0)

# Alcohol logica
alcohol = st.selectbox("Drinkt u alcohol?", ["maak een keuze", "Ja", "Nee"])
alcohol_hoeveel = 0
if alcohol == "Ja":
    alcohol_hoeveel = st.number_input("Hoeveel glazen alcohol drinkt u per week?", min_value=0)

# Allergie logica
allergieen = st.selectbox("Heeft u allergieën?", ["maak een keuze", "Ja", "Nee", "vegetarisch", "vegan"])
allergieen_eten = ""
if allergieen == "Ja":
    allergieen_eten = st.text_input("Welke allergieën heeft u?")

slaap = st.number_input("Hoeveel uur slaapt u per dag gemiddeld?", min_value=0.0, max_value=24.0, value=8.0)

# Hartstikke gezond logica
hartstikke_gezond = st.selectbox("Bent u aanwezig geweest bij een hartstikke gezond locatie?", ["maak een keuze", "Ja", "Nee"])
hartstikke_gezond_waarden = ""
if hartstikke_gezond == "Ja":
    hartstikke_gezond_waarden = st.text_input("Welke waardes zijn daar gemeten?")

# OPSLAAN KNOP
if st.button("Opslaan"):
    if not naam:
        st.error("Vul a.u.b. eerst een naam in om op te slaan.")
    else:
        # Maak de nieuwe rij aan als een nette Dictionary/DataFrame
        nieuwe_rij = pd.DataFrame([{
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "naam": naam,
            "leeftijd": leeftijd,
            "gewicht": gewicht,
            "lengte": lengte,
            "BMI": BMI,
            "werk": werk,
            "vrije_tijd": vrije_tijd,
            "sport_keuze": sport_keuze,
            "sport_welke": sport_welke,
            "sport_hoeveel": sport_hoeveel,
            "roken": roken,
            "roken_hoeveel": roken_hoeveel,
            "alcohol": alcohol,
            "alcohol_hoeveel": alcohol_hoeveel,
            "allergieen": allergieen,
            "allergieen_eten": allergieen_eten,
            "slaap": slaap,
            "hartstikke_gezond": hartstikke_gezond,
            "hartstikke_gezond_waarden": hartstikke_gezond_waarden
        }])

        # Check of bestand al bestaat voor de header
        file_exists = os.path.exists(CSV_FILE)

        # Append de data naar de CSV
        nieuwe_rij.to_csv(CSV_FILE, mode="a", header=not file_exists, index=False)
        st.success(f"Patiënt {naam} succesvol opgeslagen in {CSV_FILE}!")