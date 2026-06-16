import streamlit as st
import plotly.express as px
import time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import os
st.title("Overzicht Lifestyle Coach")

CSV_FILE = "vragen.csv"



# Controleer of het bestand bestaat en niet leeg is
if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
    # Laad de patiëntgegevens in
    data_patients = pd.read_csv(CSV_FILE)
    
    # Maak een dropdown-lijst met unieke namen
    gekozen_patient = st.selectbox(
        "Selecteer patiënt",
        data_patients["naam"].unique()
    )
    
    # Filter de data op de gekozen naam en pak de ALLERLAATSTE invoer (.iloc[-1])
    patient = data_patients[data_patients["naam"] == gekozen_patient].iloc[-1]
    
    # Toon de basisgegevens in de sidebar zoals jij dat wilde
    with st.sidebar:
        st.header("Client Profiel")
        matrix = pd.DataFrame(
            {
                "Waarde": [
                    patient["naam"],
                    patient["leeftijd"],
                    patient["lengte"],
                    patient["gewicht"],
                    patient["BMI"]
                ]
            },
            index=["Naam", "Leeftijd", "Lengte", "Gewicht", "BMI"]
        )
        st.table(matrix)

       
        with st.expander("Persoonsgegevens & Leefstijl"):
            st.write(f"**Werk**: {patient['werk']}")
            st.write(f"**Vrije tijd:** {patient['vrije_tijd']}")
            st.write(f"**Slaap:** {patient['slaap']} uur/dag")
            st.write(f"**Roken:** {patient['roken']} ({patient['roken_hoeveel']} p/d)")
            st.write(f"**Alcohol:** {patient['alcohol']} ({patient['alcohol_hoeveel']} p/w)")

        with st.expander("Point of care & Allergieën"):
            st.write(f"**Allergieën:** {patient['allergieen']}")
            if patient['allergieen'] == "Ja":
                st.write(f" Type: {patient['allergieen_eten']}")
            st.write(f"**Hartstikke Gezond Locatie:** {patient['hartstikke_gezond']}")
            if patient['hartstikke_gezond'] == "Ja":
                st.write(f" Waarden: {patient['hartstikke_gezond_waarden']}")

    st.success(f"Gegevens van {gekozen_patient} succesvol ingeladen in de sidebar!")

else:
    st.info("Er zijn nog geen patiënten opgeslagen. Vul eerst gegevens in op Pagina 1.")


def inladen(path):
    with open(path, 'r') as f:
        eerste_regel = f.readline()
    
    standaard_kolommen = ['time', 'ECG', 'accX', 'accY', 'accZ', 'gyroX', 'gyroY', 'gyroZ', 'temp']
    
    if 'time' in eerste_regel.lower() or 'ecg' in eerste_regel.lower():
        data = pd.read_csv(path)
        data.columns = data.columns.str.strip()
    else:
        data = pd.read_csv(path, names=standaard_kolommen)
    
    data = data.sort_values(by='time').reset_index(drop=True)
    
    # Bereken seconden
    data['seconde'] = (data['time'] - data['time'].iloc[0]) / 1000.0
    
    # NIEUW: Bereken uren (seconden / 3600)
    data['uren'] = data['seconde'] / 3600.0
    
    return data

def grafiek(data):
    peaks, properties = find_peaks(data['ECG'], height = 0.65 * data['ECG'].max())
    aantal = len(peaks)
    ecg_pieks = data.iloc[peaks]
    
    return ecg_pieks 

def interval(ecg_pieks):
    ecg_pieks['Interval'] = ecg_pieks['seconde'].diff()
    ecg_pieks['perpiek'] = 60 / ecg_pieks['Interval']
    ecg_piek = ecg_pieks.copy()
    return ecg_piek

def kolom (ecg_piek , leeftijd):
   # maxi = ecg_piek['perpiek'].max()
    maxi = 220 - leeftijd
    nul = 0
    rust = maxi / 2
    i1 = maxi / 100 * 65
    i2 = maxi / 100 * 75
    i5 = maxi 
    #print(i1, i2, i5)
    bins = [0, i1, i2, i5]
    labels = ['Rust','Matig', 'Intensief']
    ecg_piek['zones']= pd.cut(ecg_piek['perpiek'], bins = bins, labels = labels)
    #print(ecg_piek)
    return ecg_piek
def figure(ecg_piek):
    st.info('Maak een keuze hieronder wat u wilt tonen in de grafiek')
    
    # Data voorbereiden - we groeperen nog steeds, maar 'uren' of 'seconde' maakt voor de count niet uit
    rapport = ecg_piek.groupby('zones', observed=False).agg(
        heart=('uren', 'sum'), # Veranderd naar uren als je totale duur in uren wilt berekenen
        zone_aantal=('zones', 'count')
    ).reset_index()

    ecg_piek = ecg_piek[(ecg_piek['perpiek'] < 220) & (ecg_piek['perpiek'] > 40)].copy()
    ecg_piek['hartslag average'] = ecg_piek['perpiek'].rolling(window=50).mean()

    ecg_piek['SM'] = ((ecg_piek['accY']**2) + (ecg_piek['accZ']**2) + (ecg_piek['accX']**2))**0.5
    ecg_piek['SMV'] = ecg_piek['SM'].rolling(window=50).mean()

    # Selecties
    gekozen_lijnen = st.multiselect(
        'Kies wat je wilt tonen:',
        ['Hartslag', 'SMV', 'Hartslagzones'],
        default=['Hartslag']
    )
    
    # NIEUW: Start en eind in uren (als float voor precisie)
    start_uur = float(ecg_piek['uren'].min())
    eind_uur = float(ecg_piek['uren'].max())

    # Slider aangepast naar uren, met een stapgrootte van bijvoorbeeld 1 minuut (1/60 uur)
    tijdsvenster = st.slider(
        "Kies getoonde tijdsbestek (in uren)",
        min_value=start_uur,
        max_value=eind_uur,
        value=(start_uur, eind_uur),
        step=0.01 # Stappen van honderdsten van een uur
    )

    # Filter data op het gekozen uren-interval
    ecg_piek = ecg_piek[
        (ecg_piek['uren'] >= tijdsvenster[0]) &
        (ecg_piek['uren'] <= tijdsvenster[1])
    ].copy()

    # Nieuwe figuur
    Fig3 = go.Figure()

    # Hartslag lijn (x is nu ecg_piek['uren'])
    if 'Hartslag' in gekozen_lijnen:
        Fig3.add_trace(
            go.Scatter(
                x=ecg_piek['uren'],
                y=ecg_piek['hartslag average'],
                mode='lines',
                name='Hartslag',
                line=dict(color='blue')
            )
        )

    # SMV lijn (x is nu ecg_piek['uren'])
    if 'SMV' in gekozen_lijnen:
        Fig3.add_trace(
            go.Scatter(
                x=ecg_piek['uren'],
                y=ecg_piek['SMV'],
                mode='lines',
                name='SMV',
                line=dict(color='purple')
            )
        )

    # Hartslagzones toevoegen
    if 'Hartslagzones' in gekozen_lijnen:
        bins_zones = [0, 118.8, 138.6, 158.4, 179.2, 198]
        colors = ['green', 'yellowgreen', 'orange', 'salmon', 'red']
        zone_names = ['Laag', 'Licht', 'Middel', 'Zwaar', 'Hoog']

        for i in range(len(bins_zones)-1):
            Fig3.add_hrect(
                y0=bins_zones[i],
                y1=bins_zones[i+1],
                fillcolor=colors[i],
                opacity=0.2,
                layer='below',
                line_width=0
            )

            Fig3.add_trace(
                go.Scatter(
                    x=[None],
                    y=[None],
                    mode='lines',
                    line=dict(color=colors[i], width=10),
                    name=zone_names[i]
                )
            )

    # Layout
    Fig3.update_layout(
        title='Hartslag en SMV over tijd',
        xaxis_title='Tijd(uren)',
        yaxis_title='Waarde',
        hovermode='x unified'
    )

    # Grafiek tonen
    
    st.plotly_chart(Fig3, use_container_width=True)


    with st.expander('Meer informatie over de grafiek'):
        st.write(
        'De gemeten hartslag per piek kan erg verschillen. Daardoor wordt er in de grafiek hierboven de gemeten hartslag (bpm) getoond, met een rolling window van 50.\n'
        'Dit betekent dat voor elk meetpunt het gemiddelde wordt genomen van 50 hartslagpunten (niet 50 seconden). Hierdoor is de getoonde lijn vlakker en makkelijker af te lezen.\n\n'
        'Voor meer technische informatie:\n'
        'https://rsisinternational.org/journals/ijrsi/uploads/vol12-iss8-pg178-186-202508_pdf.pdf\n\n'
        
    )
    rapport['uren_per_zone'] = rapport['zone_aantal'] / 3600.0

    # Tweede grafiek
    Figi = px.bar(
        rapport,
        x='zones',
        y='uren_per_zone',
        labels = {
            "zones": "Activiteitszone",
            "uren_per_zone": "Verstreken tijd (uren)"  # <--- Hier miste het " tekentje aan het einde!
        },
        title = 'Verstreken tijd in activiteit zones'
    )
    
    st.info('Hieronder wordt een staafdiagram getoond; hoeveel tijd er besteed is per activiteitzone')

    st.plotly_chart(Figi)

    with st.expander('Meer informatie over bovenstaand grafiek'):
        st.write(
            'De activiteitzones zijn berekend met de maximale hartslag. Hierbij is gerekend aan de hand van de vuistregel van de Hartstiching: Maximale hartslag = 220 - leeftijd. met een afwijking van ±15 slagen per minuut.\n\n'
            ' Hierbij zijn de volgende activiteitzones berekend op de volgende manier; Rust = 50-60% van maximale hartslag, matig = 60-80% van maximale hartslag,'
        'intensief sporten = 80%+ van maximale hartslag.\n\n'
        )
    return ecg_piek
    
def tabel(ecg_piek):

    ecg_piek['acc'] = np.sqrt(
    ecg_piek['accX']**2 +
    ecg_piek['accY']**2 +
    ecg_piek['accZ']**2
    )

    acc = ecg_piek['acc'] - ecg_piek['acc'].mean()

    peaks, properties = find_peaks(
        acc,
        distance=3,
        prominence=0.5
    )

    stappen = len(peaks)
    
    gemiddelde = ecg_piek['perpiek'].mean()
    maxi = ecg_piek['perpiek'].max()
    mini = ecg_piek['perpiek'].min()
    
    tijdrust = ecg_piek.loc[
        ecg_piek['zones'] == 'Rust', 'Interval'
    ].sum() / 3600

    tijdmatig = ecg_piek.loc[
        ecg_piek['zones'] == 'Matig', 'Interval'
    ].sum() / 3600

    tijdintensief = ecg_piek.loc[
        ecg_piek['zones'] == 'Intensief', 'Interval'
    ].sum() / 3600
    matrix = pd.DataFrame(
        {
            'Waardes': [gemiddelde, maxi, mini, stappen, tijdrust, tijdmatig, tijdintensief],
        },
        index= ['Gemiddelde hartslag', 'Hoogst gemeten hartslag', 'Laagst gemeten hartslag', 'Totaal aantal stappen tijdens meting', 'Verstreken tijd in activiteit zone Rust', 'Verstreken tijd in activiteit zone Matig', 'Verstreken tijd in activiteit zone Intensief'],
    )
    st.info('Een Numerieke tabel om inzicht in algemene gezondheid te vergroten')
    st.table(matrix)
    with st.expander('Meer informatie over tabel'):
        st.write('De richtlijnen van de overheid zijn als volgt;\n\n' 
        '•Doe minstens 150 minuten per week aan matig. intensieve inspanning, zoals wandelen en fietsen, verspreid over diverse dagen. Langer, vaker en/of intensiever bewegen geeft extra gezondheidsvoordeel.\n\n'
                 ' • Doe minstens tweemaal per week spier- en botversterkende activiteiten, voor ouderen gecombineerd met balansoefeningen.\n\n'
                 ' • En: voorkom veel stilzitten.'
                )

    with st.expander('bronnen voor getoonde informatie'):
        st.write('Informatie vanuit de Hartstichting over gezonde hartslag en activiteitzones:'
        'https://www.hartstichting.nl/gezond-leven/hartslag/hartslag-bij-inspanning \n\n'
        'Informatie vanuit de overheid voor streefregels omtrend gezondheid:'
        'https://www.rijksoverheid.nl/themas/familie-zorg-en-gezondheid/sport-en-bewegen/sport-bewegen-en-gezondheid'

            
        )
#       gemiddelde over dag (tijdslot) - hartslag zones - tijd in activiteitzones - stappen in dag

def main():
    path = r"D:\data.txt"
    data = inladen(path)
    ecg_pieks = grafiek(data)
    ecg_piek = interval(ecg_pieks)
    ko = kolom(ecg_piek, patient["leeftijd"])
    ecg_piek = figure(ecg_piek)
    tab = tabel(ecg_piek)

main()
#"D:\data.txt"
#"C:\Users\jorri\OneDrive\Documenten\7.2 project deel 2\data 2.txt"