import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import random
import pandas as pd
st.set_page_config(
    page_title="Odyssey Asteroid Simulator",
    layout="wide",
    page_icon="☄️"
)
st.title("🪐 Odyssey Asteroid Impact Simulator
# DARK MODe
dark_mode = st.checkbox("🌙 Dark Mode", value=False)
map_tile = "CartoDB dark_matter" if dark_mode else "CartoDB positron"

#  LAYOUT
left, right = st.columns([1.2, 1])

with left:
    st.subheader("🌍 Select Impact Location")
    st.write("Click anywhere on the map — the last clicked area is selected as the impact location.")
    m = folium.Map(location=[20, 0], zoom_start=2, tiles=map_tile)
    st_data = st_folium(m, width=500, height=400)
    location = None
    if st_data and st_data.get("last_clicked"):
        location = st_data.get("last_clicked")
        st.success(f"📍 Selected Location: {location}")

with right:
    st.subheader("⚙️ Asteroid Parameters")

    asteroid_type = st.selectbox(
        "Asteroid Type",
        ["D-type (Carbon-rich)", "V-type (Vestoids)", "S-type (Stony)", "M-type (Metallic)", "C-type (Carbon)", "Custom"]
    )

    densities = {
        "D-type (Carbon-rich)": 1300,
        "V-type (Vestoids)": 3500,
        "S-type (Stony)": 2700,
        "M-type (Metallic)": 7800,
        "C-type (Carbon)": 1700
    }

    if asteroid_type != "Custom":
        density = densities[asteroid_type]
    else:
        density = st.number_input("Enter Custom Density (kg/m³)", min_value=1000, max_value=15000, value=7500)

    diameter = st.slider("Asteroid Diameter (meters)", 10, 20000, 5000)
    velocity = st.slider("Speed (km/s)", 1, 72, 25)
    impact_angle = st.slider("Impact Angle (°)", 0, 90, 45)

    st.subheader("🛡️ Defend Earth")
    defend = st.radio("Do you want to defend Earth?", ["Yes", "No"])
    strategy = None
    if defend == "Yes":
        strategy = st.selectbox("Choose your mitigation strategy", ["Kinetic Impactor", "Gravity Tractor"])

    calculate = st.button("🚀 Calculate Impact")
    show_data = st.button("🛰️ View  Real Asteroids")
#  FIXED ASTEROID DATA (51 rows)

asteroid_dataset = [
    ["2024 BX1", 2, 12.4, "2024-01-15", 345000, "N"],
    ["Apophis", 370, 30.7, "2029-04-13", 31000, "Y"],
    ["Bennu", 490, 28.0, "2135-09-25", 750000, "Y"],
    ["2019 OK", 100, 24.5, "2019-07-25", 73000, "Y"],
    ["Toutatis", 2100, 9.8, "2004-09-29", 1540000, "N"],
    ["Florence", 4900, 13.6, "2017-09-01", 7000000, "N"],
    ["1998 OR2", 2000, 8.7, "2020-04-29", 6300000, "N"],
    ["2001 FO32", 890, 34.4, "2021-03-21", 2000000, "Y"],
    ["Didymos", 780, 23.0, "2123-10-04", 600000, "N"],
    ["Dimorphos", 160, 22.0, "2123-10-04", 600000, "N"],
    ["2004 BL86", 325, 15.6, "2015-01-26", 1200000, "N"],
    ["99942 Apophis", 370, 31.3, "2029-04-13", 31000, "Y"],
    ["4179 Toutatis", 2100, 10.6, "2004-09-29", 1540000, "N"],
    ["3200 Phaethon", 5100, 31.0, "2093-12-14", 7300000, "N"],
    ["3122 Florence", 4900, 13.6, "2017-09-01", 7000000, "N"],
    ["2015 TB145", 600, 35.2, "2015-10-31", 486000, "Y"],
    ["2021 EQ3", 30, 9.6, "2021-03-22", 278000, "N"],
    ["2002 AJ129", 1300, 34.0, "2018-02-04", 4200000, "N"],
    ["2010 XC15", 150, 8.7, "2022-12-27", 770000, "N"],
    ["2003 SD220", 2400, 7.3, "2018-12-22", 2900000, "N"],
    ["2023 DZ2", 64, 28.0, "2023-03-25", 175000, "N"],
    ["2001 WN5", 950, 14.0, "2028-06-26", 248000, "Y"],
    ["2002 NY40", 800, 28.0, "2002-08-18", 534000, "N"],
    ["2014 JO25", 650, 33.8, "2017-04-19", 1800000, "N"],
    ["2023 BU", 8, 9.3, "2023-01-26", 3600, "N"],
    ["2006 QV89", 40, 15.0, "2019-09-27", 7400000, "N"],
    ["2019 DS1", 13, 18.2, "2019-02-28", 257000, "N"],
    ["2020 QG", 3, 12.3, "2020-08-16", 2950, "N"],
    ["2022 EB5", 2, 18.5, "2022-03-11", 0, "N"],
    ["2018 LA", 2.6, 17.0, "2018-06-02", 0, "N"],
    ["2013 TX68", 30, 14.0, "2013-09-07", 4400000, "N"],
    ["2007 TU24", 250, 9.3, "2008-01-29", 554000, "N"],
    ["2008 EV5", 400, 10.5, "2023-12-23", 8900000, "Y"],
    ["2009 FD", 472, 22.1, "2185-03-29", 1230000, "Y"],
    ["2011 AG5", 140, 14.7, "2040-02-05", 9600000, "Y"],
    ["2015 EG", 30, 10.0, "2015-03-08", 330000, "N"],
    ["2016 RB1", 10, 9.2, "2016-09-07", 37000, "N"],
    ["2017 BX", 6, 7.1, "2017-01-30", 65000, "N"],
    ["2018 VP1", 2, 12.0, "2020-11-02", 400000, "N"],
    ["2020 SW", 10, 8.5, "2020-09-24", 27000, "N"],
    ["2001 YB5", 300, 13.0, "2002-01-07", 590000, "N"],
    ["2021 UA1", 5, 12.1, "2021-10-26", 2200, "N"],
    ["2020 KT1", 12, 9.8, "2020-05-28", 48000, "N"],
    ["2019 UN13", 8, 14.3, "2019-10-31", 15000, "N"],
    ["2018 GE3", 48, 8.0, "2018-04-14", 192000, "N"],
    ["2017 QV1", 15, 11.5, "2017-08-24", 64000, "N"],
    ["2016 AA", 2, 12.0, "2016-01-02", 4300, "N"],
    ["2015 SO2", 50, 7.5, "2015-09-29", 123000, "N"],
    ["2014 HQ124", 325, 13.4, "2014-06-08", 2150000, "N"],
    ["2002 TC11", 95, 10.2, "2002-10-31", 340000, "N"],
    ["1999 AN10", 800, 17.3, "2027-08-07", 380000, "Y"],
]

#  CALCULATE IMPACT-
if calculate:
    st.header("💥 IMPACT RESULT")

    if diameter <= 25:
        st.success("☁️ The asteroid burned up in the atmosphere. No impact occurred.")
        st.stop()

    radius = diameter / 2
    volume = (4 / 3) * math.pi * (radius ** 3)
    mass = density * volume
    velocity_mps = velocity * 1000

    if defend == "Yes" and strategy:
        defense_success = random.random() < 0.65
        if defense_success:
            st.success(f"🌍 Defense successful ({strategy}) — the asteroid was deflected!")
            if strategy == "Kinetic Impactor":
                st.info(
                    "🛰️ **Kinetic Impactor:** A spacecraft collided with the asteroid, "
                    "changing its trajectory to avoid Earth."
                )
            elif strategy == "Gravity Tractor":
                st.info(
                    "🪐 **Gravity Tractor:** A spacecraft used gravitational pull "
                    "to slowly alter the asteroid's orbit away from Earth."
                )
            st.stop()
        else:
            st.error(f"🚨 Defense failed — The asteroid hit Earth despite using {strategy}.")
            if strategy == "Kinetic Impactor":
                velocity_mps *= 0.9
            elif strategy == "Gravity Tractor":
                velocity_mps *= 0.95

    KE = 0.5 * mass * (velocity_mps ** 2)
    crater_diameter = (KE / 1e12) ** 0.3
    TNT = KE / 4.184e9

    if KE > 2e50:
        fatalities = "Billions"
    elif KE > 1e18:
        fatalities = "Millions"
    elif KE > 1e16:
        fatalities = "Thousands"
    else:
        fatalities = "Few hundreds"

    if impact_angle < 45 and KE > 1e15:
        tsunami = f"{round(KE / 1e15, 2)} meters high (approx.)"
    else:
        tsunami = "No significant tsunami"

    # Display metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("🌑 Kinetic Energy", f"{KE:.2e} J")
    c2.metric("🌍 Asteroid Mass", f"{mass:.2e} kg")
    c3.metric("☄️ Crater Diameter", f"{crater_diameter:.2f} km")

    c4, c5, c6 = st.columns(3)
    c4.metric("💣 TNT Equivalent", f"{TNT:.2e} tons")
    c5.metric("👥 Estimated Casualties", fatalities)
    c6.metric("🌊 Tsunami Height", tsunami)

    st.subheader("🚨 Evacuation and Safety Plan")
    if fatalities == "Billions":
        st.warning("Evacuate all areas within 1000 km — global catastrophe likely.")
    elif fatalities == "Millions":
        st.warning("Evacuate coastal and populated regions within 500 km — high danger.")
    elif fatalities == "Thousands
