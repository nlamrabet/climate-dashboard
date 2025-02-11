# Verwendete Bibliotheken
import streamlit as st
import pandas as pd
import plotly.express as px



########################################
####### STREAMLIT USER INTERFACE #######
########################################


# Streamlit Set-Up
st.set_page_config(page_title="Klimadaten Dashboard", layout="wide")

# Seitemleiste Navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.selectbox("Wähle eine Ansicht", 
    ["🌍 Startseite", "📊 Land, Ozean und Jahreszeiten Analyse", "🗺 Global / Länder Analyse"]
)

# Seitenlogik
if page == "🌍 Startseite":
    st.title("🌍 Willkommen im Klimadaten-Dashboard")
    st.markdown("""
         
        Dieses Dashboard ermöglicht es dir, interaktiv globale Klimadaten zu analysieren. Es besteht aus zwei Hauptbereichen:
        
        1. **Land-, Ozean- und Jahreszeiten-Analyse**  
           - Analysiere globale Temperaturtrends auf Land- und Ozeanflächen sowie jahreszeitenspezifische Entwicklungen.

        2. **Global-/Länder-Analyse**  
           - Vergleiche weltweite Durchschnittstemperaturen, Temparaturanomalien und analysiere Temperaturentwicklungen für einzelne Länder oder Kontinente.
             
        **Wie navigiere ich?**  
          Benutze die **Seitenleiste**, um zwischen den verschiedenen Analyseseiten zu wechseln.
    """)

###################################################################################################################################################

elif page == "📊 Land, Ozean und Jahreszeiten Analyse":
    st.title("📊 Land-, Ozean- und Jahreszeiten-Analyse")
    st.markdown("""
        **Anleitung für diese Seite:**  
        - **Zeitraum wählen:** Nutze den **Slider**, um den gewünschten Analysezeitraum einzustellen.  
        - **Temperaturtyp wählen:** Entscheide, ob du Landtemperaturen, Ozeantemperaturen oder beides anzeigen möchtest.  
        - **Jahreszeitenvergleich:** Wähle spezifische Jahreszeiten aus, um Temperaturtrends für Frühling, Sommer, Herbst oder Winter zu vergleichen.
    """)

    st.markdown("---")

    # Daten Laden
    @st.cache_data
    def load_global_data():
        df = pd.read_csv("GlobalTemperatures.csv", parse_dates=["dt"])
        df["year"] = df["dt"].dt.year  # Jahr extrahieren
        return df

    global_df = load_global_data()

    # Interaktive Auswahl
    st.markdown("### 🌡 Entwicklung der globalen Temperaturen")

    min_year, max_year = int(global_df["year"].min()), int(global_df["year"].max())
    selected_years = st.slider("Zeitraum wählen:", min_year, max_year, (1900, 2015))

    # Auswahl der Temperaturart
    temp_type = st.radio(
        "Welche Temperatur soll angezeigt werden?",
        ("Landtemperatur", "Ozeantemperatur", "Beides"),
    )

    # Daten Filtern
    filtered_df = global_df[
        (global_df["year"] >= selected_years[0]) & (global_df["year"] <= selected_years[1])
    ]

    # Zeitreihenplot
    fig = px.line(
        title="",
        labels={"value": "Temperatur (°C)", "dt": "Jahr"},
        template="plotly_dark",
    )

    if temp_type == "Landtemperatur":
        fig.add_scatter(x=filtered_df["dt"], y=filtered_df["LandAverageTemperature"], mode="lines", name="Landtemperatur")
    elif temp_type == "Ozeantemperatur":
        fig.add_scatter(x=filtered_df["dt"], y=filtered_df["LandAndOceanAverageTemperature"], mode="lines", name="Ozeantemperatur")
    else:
        fig.add_scatter(x=filtered_df["dt"], y=filtered_df["LandAverageTemperature"], mode="lines", name="Landtemperatur")
        fig.add_scatter(x=filtered_df["dt"], y=filtered_df["LandAndOceanAverageTemperature"], mode="lines", name="Ozeantemperatur")
    


    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Jahreszeiten berechnen 
    global_df["month"] = global_df["dt"].dt.month
    seasons = {
    "Winter": [12, 1, 2],
    "Frühling": [3, 4, 5],
    "Sommer": [6, 7, 8],
    "Herbst": [9, 10, 11]
    }

    # Monatliche Durchschnittstemperaturen als Heatmap mit feinen Farbsprüngen
    st.markdown("### 🌡 Monatliche Durchschnittstemperaturen")

    monthly_avg = global_df.groupby(["year", "month"])["LandAverageTemperature"].mean().unstack()

    fig_heatmap = px.imshow(
        monthly_avg,
        labels={"x": "Monat", "y": "Jahr", "color": "Temperatur (°C)"},
        title="🌡 Monatliche Durchschnittstemperaturen",
        color_continuous_scale=[
            [0.00, "darkblue"],   
            [0.10, "blue"],       
            [0.20, "cyan"],       
            [0.30, "lightgreen"], 
            [0.40, "green"],      
            [0.50, "yellow"],     
            [0.60, "orange"],     
            [0.70, "darkorange"], 
            [0.80, "red"],        
            [0.90, "darkred"],    
            [1.00, "#8B0000"],    
        ],
        template="plotly_dark",
        aspect="auto",
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("---")


    # Jahreszeitenvergleich
    st.markdown("### 🌦 Jahreszeitenvergleich Global")

    # Neue Spalte für Jahreszeit zuweisen
    def assign_season(month):
        for season, months in seasons.items():
            if month in months:
                return season
        return "Unknown"

    global_df["Season"] = global_df["month"].apply(assign_season)

    # Mittelwerte pro Jahreszeit und Jahr berechnen
    season_avg = global_df.groupby(["year", "Season"])["LandAverageTemperature"].mean().reset_index()

    # Auswahl der Jahreszeiten für den Vergleich
    selected_seasons = st.multiselect(
    "Wähle Jahreszeiten für den Vergleich:", seasons.keys(), ["Winter", "Sommer"]
    )

    # Daten filtern
    filtered_season_data = season_avg[season_avg["Season"].isin(selected_seasons)]

    # Liniendiagramm für Jahreszeitenvergleich
    fig_seasons = px.line(
    filtered_season_data,
    x="year",
    y="LandAverageTemperature",
    color="Season",
    title="🌡 Temperaturentwicklung nach Jahreszeiten",
    labels={"LandAverageTemperature": "Durchschnittstemperatur (°C)", "year": "Jahr"},
    template="plotly_dark",
    )

    st.plotly_chart(fig_seasons, use_container_width=True)





#################################################################################################################################################

elif page == "🗺 Global / Länder Analyse":
    st.title("🗺 Global- und Länder-Analyse")
    st.markdown("""
        **Anleitung für diese Seite:**  
        - **Globale Temperaturverteilung:**  
          - Wähle ein Jahr mit dem **Slider**, um die weltweiten Durchschnittstemperaturen als Karte zu visualisieren.
          - Wähle die Referenzperiode für die Temperaturanomalie des ausgewählten Jahres 
        - **Kontinentenvergleich:**  
          - Wähle Kontinente aus der Dropdown-Liste, um deren Temperaturentwicklung im Zeitverlauf zu vergleichen.  
        - **Ländervergleich:**  
          - Wähle Länder aus der Dropdown-Liste, um deren Temperaturentwicklung im Zeitverlauf zu vergleichen.
          - Wähle ein Land aus der Dropdown-Liste und einen spezifischen Zeitraum um die monatlichen Durchschnittstemperaturen anzeigen zu lassen
    """)

    st.markdown("---")

    # Daten Laden
    @st.cache_data
    def load_country_data():
        df = pd.read_csv("GlobalLandTemperaturesByCountry.csv", parse_dates=["dt"])
        df["year"] = df["dt"].dt.year  # Jahr extrahieren
        df["month"] = df["dt"].dt.month  # Monat extrahieren

        # 👉 Datensatz 1: Aggregierte Jahresdurchschnittswerte (für bestehende Darstellungen)
        country_yearly_df = df.groupby(["Country", "year"])["AverageTemperature"].mean().reset_index()

        # 👉 Datensatz 2: Monatliche Durchschnittswerte (nur für die neue Heatmap)
        country_monthly_df = df.groupby(["Country", "year", "month"])["AverageTemperature"].mean().reset_index()

        return country_yearly_df, country_monthly_df

    # Daten abrufen
    country_yearly_df, country_monthly_df = load_country_data()


    # Entferne Kontinente aus der Länderliste
    continents_to_exclude = [
        "Africa", "Asia", "Europe", "North America", "South America", "Oceania"]
    country_yearly_df = country_yearly_df[~country_yearly_df["Country"].isin(continents_to_exclude)]

    # Interaktive Weltkarte
    st.markdown("## 🗺 Globale Temperaturverteilung")

    # Slider zur Auswahl eines spezifischen Jahres für die Karte
    min_year, max_year = int(country_yearly_df["year"].min()), int(country_yearly_df["year"].max())
    selected_map_year = st.slider("Wähle ein Jahr für die Weltkarte:", min_year, max_year, 2000)

    # Daten für das ausgewählte Jahr filtern
    map_data = country_yearly_df[country_yearly_df["year"] == selected_map_year]

    # Entferne NaN-Werte aus der Temperaturspalte
    map_data = map_data.dropna(subset=["AverageTemperature"])

    # Werte auf 2 Nachkommastellen runden
    map_data["AverageTemperature"] = map_data["AverageTemperature"].round(2)

    # Auswahl der Referenzperiode für Temperaturanomalien
    reference_choice = st.radio(
        "Wähle die Referenzperiode für die Temperaturanomalie:",
        ["1961-1990 (WMO)", "1850-1900 (IPCC)"], horizontal=True
    )

    # Historischen Mittelwert berechnen
    if reference_choice == "1961-1990 (WMO)":
        reference_period = country_yearly_df[(country_yearly_df["year"] >= 1961) & (country_yearly_df["year"] <= 1990)]
        selected_reference = "1961-1990 (WMO)"
    elif reference_choice == "1850-1900 (IPCC)":
        reference_period = country_yearly_df[(country_yearly_df["year"] >= 1850) & (country_yearly_df["year"] <= 1900)]
        selected_reference = "1850-1900 (IPCC)"

    # Falls keine Daten verfügbar sind, setze Standardwert
    if reference_period.empty:
        st.warning("⚠️ Keine Daten für die gewählte Referenzperiode verfügbar!")
        historical_global_avg_temp = 0
    else:
        historical_global_avg_temp = reference_period["AverageTemperature"].mean()

    # Durchschnittstemperatur weltweit berechnen
    global_avg_temp = map_data["AverageTemperature"].mean()

    # Berechnung der Temperaturanomalie
    temperature_anomaly = global_avg_temp - historical_global_avg_temp

    # 📌 Layout für KPI-Metriken erstellen (2 Spalten)
    col1, col2 = st.columns(2)

    # 🌡 Durchschnittstemperatur weltweit als KPI
    col1.metric(
        label="🌍 Durchschnittstemperatur weltweit",
        value=f"{global_avg_temp:.2f}°C",
        delta=None
    )

    # 🔥 Temperaturabweichung vom historischen Mittelwert als KPI
    col2.metric(
        label=f"🔥 Temperaturabweichung ({selected_reference})",
        value=f"{temperature_anomaly:.2f}°C",
        delta=None  
    )

    # Map Konfiguration (nur Durchschnittstemperaturen!)
    fig_map = px.choropleth(
        map_data,
        locations="Country",
        locationmode="country names",
        color="AverageTemperature",
        hover_name="Country",
        color_continuous_scale="thermal",  # Verbesserte Farbskala für bessere Sichtbarkeit
        title=f"🌡 Durchschnittstemperaturen weltweit im Jahr {selected_map_year}",
        labels={"AverageTemperature": "Durchschnittstemperatur (°C)"},
        template="plotly_dark",
    )

    fig_map.update_layout(
        height=700,
        margin={"r": 0, "t": 50, "l": 0, "b": 0}
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")

    # Kontinentenvergleich 
    st.markdown("## 🌍 Vergleich der Kontinente")

    # Mapping von Ländern zu Kontinenten
    # Zuordnung aller Länder zu Kontinenten
    continent_map_full = {
    "Afrika": [
        "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Cape Verde",
        "Central African Republic", "Chad", "Comoros", "Congo (Brazzaville)", "Congo (Kinshasa)",
        "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Gabon", "Gambia",
        "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Libya",
        "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia",
        "Niger", "Nigeria", "Rwanda", "Sao Tome and Principe", "Senegal", "Seychelles", "Sierra Leone",
        "Somalia", "South Africa", "South Sudan", "Sudan", "Tanzania", "Togo", "Tunisia", "Uganda",
        "Zambia", "Zimbabwe"
    ],
    "Asien": [
        "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodia",
        "China", "Cyprus", "Georgia", "India", "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan",
        "Kazakhstan", "Kuwait", "Kyrgyzstan", "Laos", "Lebanon", "Malaysia", "Maldives", "Mongolia",
        "Myanmar", "Nepal", "North Korea", "Oman", "Pakistan", "Palestine", "Philippines", "Qatar",
        "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka", "Syria", "Tajikistan", "Thailand",
        "Timor-Leste", "Turkey", "Turkmenistan", "United Arab Emirates", "Uzbekistan", "Vietnam", "Yemen"
    ],
    "Europa": [
        "Albania", "Andorra", "Armenia", "Austria", "Azerbaijan", "Belarus", "Belgium", "Bosnia and Herzegovina",
        "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France",
        "Georgia", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Kosovo", "Latvia",
        "Liechtenstein", "Lithuania", "Luxembourg", "Malta", "Moldova", "Monaco", "Montenegro", "Netherlands",
        "North Macedonia", "Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino", "Serbia",
        "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom",
        "Vatican City"
    ],
    "Nord-Amerika": [
        "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Canada", "Costa Rica", "Cuba", "Dominica",
        "Dominican Republic", "El Salvador", "Grenada", "Guatemala", "Haiti", "Honduras", "Jamaica",
        "Mexico", "Nicaragua", "Panama", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines",
        "Trinidad and Tobago", "United States"
    ],
    "Süd-Amerika": [
        "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador", "Guyana", "Paraguay", "Peru",
        "Suriname", "Uruguay", "Venezuela"
    ],
    "Ozeanien": [
        "Australia", "Fiji", "Kiribati", "Marshall Islands", "Micronesia", "Nauru", "New Zealand",
        "Palau", "Papua New Guinea", "Samoa", "Solomon Islands", "Tonga", "Tuvalu", "Vanuatu"
    ]
    }


    # Kontinente zuordnen
    def assign_continent(country):
        for continent, countries in continent_map_full.items():
            if country in countries:
                return continent
        return "Andere"

    country_yearly_df["Continent"] = country_yearly_df["Country"].apply(assign_continent)

    # Durchschnittstemperatur pro Kontinent und Jahr berechnen
    continent_data = country_yearly_df.groupby(["Continent", "year"])["AverageTemperature"].mean().reset_index()

    # Mehrfachauswahl für Kontinente
    unique_continents = continent_data["Continent"].unique()
    selected_continents = st.multiselect(
    "Wähle Kontinente zum Vergleich:", unique_continents, unique_continents
    )

    # Daten für die ausgewählten Kontinente und Zeiträume filtern
    selected_continent_years = st.slider("Zeitraum wählen:", min_year, max_year, (1900, 2013), key="continent_years")
    filtered_continent_data = continent_data[
    (continent_data["year"] >= selected_continent_years[0]) & 
    (continent_data["year"] <= selected_continent_years[1]) &
    (continent_data["Continent"].isin(selected_continents))
    ]

    # Liniendiagramm erstellen
    fig_continent = px.line(
    filtered_continent_data,
    x="year",
    y="AverageTemperature",
    color="Continent",
    title="🌡 Temperaturentwicklung der Kontinente",
    labels={"AverageTemperature": "Durchschnittstemperatur (°C)", "year": "Jahr"},
    template="plotly_dark",
    )

    st.plotly_chart(fig_continent, use_container_width=True)

    st.markdown("---")

    # Länderspezifische Temperaturentwicklung
    st.markdown("## 🌍 Länderspezifische Temperaturentwicklung")

    # Dropdown für Länderauswahl 
    unique_countries = country_yearly_df["Country"].unique()
    selected_countries = st.multiselect(
        "Wähle Länder zum Vergleich:", unique_countries, ["Germany", "United States"]
    )

    # Slider zur Auswahl eines Zeitraums
    selected_years = st.slider("Zeitraum wählen:", min_year, max_year, (1900, 2013), key="country_years")

    # Daten für ausgewählte Länder filtern
    filtered_country_df = country_yearly_df[
        (country_yearly_df["year"] >= selected_years[0]) & (country_yearly_df["year"] <= selected_years[1]) &
        (country_yearly_df["Country"].isin(selected_countries))
    ]

    # Zeitreihenplot
    fig_country = px.line(
        filtered_country_df,
        x="year",
        y="AverageTemperature",
        color="Country",
        title="🌡 Temperaturentwicklung nach Ländern",
        labels={"AverageTemperature": "Durchschnittstemperatur (°C)", "year": "Jahr"},
        template="plotly_dark",
    )

    st.plotly_chart(fig_country, use_container_width=True)


    st.markdown("---")

    # Länderspezifische Temperatur-Heatmap
    st.markdown("## 📆 Monatliche Durchschnittstemperaturen für ein Land")

    # Drop-down für Länderauswahl
    selected_country_heatmap = st.selectbox(
        "Wähle ein Land für die Heatmap:", 
        country_monthly_df["Country"].unique(), 
        key="heatmap_country"
    )

    # Slider für Zeitraum
    min_year, max_year = int(country_monthly_df["year"].min()), int(country_monthly_df["year"].max())
    selected_years_heatmap = st.slider(
        "Wähle den Zeitraum für die Heatmap:", 
        min_year, max_year, (2000, 2013),
        key="heatmap_years"
    )

    # Daten für das ausgewählte Land und den Zeitraum filtern
    country_heatmap_data = country_monthly_df[
        (country_monthly_df["Country"] == selected_country_heatmap) & 
        (country_monthly_df["year"] >= selected_years_heatmap[0]) & 
        (country_monthly_df["year"] <= selected_years_heatmap[1])
    ]

    # Heatmap-Daten umstrukturieren (Jahr als Zeile, Monat als Spalte)
    heatmap_matrix = country_heatmap_data.pivot(index="year", columns="month", values="AverageTemperature")

    # Erstelle die Heatmap mit Plotly
    fig_heatmap_country = px.imshow(
        heatmap_matrix,
        labels={"x": "Monat", "y": "Jahr", "color": "Temperatur (°C)"},
        title=f"🌡 Monatliche Durchschnittstemperaturen in {selected_country_heatmap}",
        color_continuous_scale=[
            [0.00, "darkblue"],   
            [0.10, "blue"],       
            [0.20, "cyan"],       
            [0.30, "lightgreen"], 
            [0.40, "green"],      
            [0.50, "yellow"],     
            [0.60, "orange"],     
            [0.70, "darkorange"], 
            [0.80, "red"],        
            [0.90, "darkred"],    
            [1.00, "#8B0000"],    
        ],
        template="plotly_dark",
        aspect="auto",
    )

    st.plotly_chart(fig_heatmap_country, use_container_width=True)





