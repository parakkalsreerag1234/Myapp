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
st.title("🪐 Odyssey Asteroid Impact Simulator")


#DARK MODe
dark_mode = st.checkbox("🌙 Dark Mode", value=False)
map_tile = "CartoDB dark_matter" if dark_mode else "CartoDB positron"

# 🌎 LAYOUT
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
    show_data = st.button("🛰️ View 50 Real Asteroids")

# 🪐 FIXED ASTEROID DATA (50 records)
asteroid_dataset = [
    ["Apophis", 370, 30.7, "2029-04-13", 31000, "Yes"],
    ["Bennu", 490, 28, "2135-09-25", 750000, "Yes"],
    ["2019 OK", 100, 24.5, "2019-07-25", 73000, "Yes"],
    ["Toutatis", 2100, 9.8, "2004-09-29", 1540000, "No"],
    ["Florence", 4900, 13.6, "2017-09-01", 7000000, "No"],
    ["1998 OR2", 2000, 8.7, "2020-04-29", 6300000, "No"],
    ["2001 FO32", 890, 34.4, "2021-03-21", 2000000, "Yes"],
    ["Didymos", 780, 23, "2123-10-04", 600000, "No"],
    ["Dimorphos", 160, 22, "2123-10-04", 600000, "No"],
    ["(2024 BX1)", 2, 12.4, "2024-01-15", 345000, "No"],
] 
# 💥 CALCULATE IMPACT
if calculate:
    st.header("💥 IMPACT RESULT")

    if diameter <= 25:
        st.success("☁️ The asteroid burned up in the atmosphere. No impact occurred.")
        st.stop()

    # Physics calculations
    radius = diameter / 2
    volume = (4 / 3) * math.pi * (radius ** 3)
    mass = density * volume
    velocity_mps = velocity * 1000

    # 🌎 DEFENSE SECTION
    if defend == "Yes" and strategy:
        defense_success = random.random() < 0.65
        if defense_success:
            st.success(f"🌍 Defense successful ({strategy}) — the asteroid was deflected!")

            if strategy == "Kinetic Impactor":
                st.info(
                    "🛰️ **Kinetic Impactor:** A spacecraft was deliberately crashed into the asteroid, "
                    "transferring momentum and slightly altering its trajectory so it missed Earth."
                )
            elif strategy == "Gravity Tractor":
                st.info(
                    "🪐 **Gravity Tractor:** A spacecraft flew alongside the asteroid, using gravitational pull "
                    "to gently tug it onto a safer orbit over time, preventing collision."
                )
            st.stop()
        else:
            st.error(f"🚨 Defense failed — The asteroid hit Earth despite using {strategy}.")
            if strategy == "Kinetic Impactor":
                velocity_mps *= 0.9
            elif strategy == "Gravity Tractor":
                velocity_mps *= 0.95

    #  IMPACT PHYSICS
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

    # 📊 DISPLAY RESULTS
    c1, c2, c3 = st.columns(3)
    c1.metric("🌑 Kinetic Energy", f"{KE:.2e} J")
    c2.metric("🌍 Asteroid Mass", f"{mass:.2e} kg")
    c3.metric("☄️ Crater Diameter", f"{crater_diameter:.2f} km")

    c4, c5, c6 = st.columns(3)
    c4.metric("💣 TNT Equivalent", f"{TNT:.2e} tons")
    c5.metric("👥 Estimated Casualties", fatalities)
    c6.metric("🌊 Tsunami Height", tsunami)

    # 🚨 SAFETY PLAN
    st.subheader("🚨 Evacuation and Safety Plan")
    if fatalities == "Billions":
        st.warning("Evacuate all areas within 1000 km — global catastrophe likely.")
    elif fatalities == "Millions":
        st.warning("Evacuate coastal and populated regions within 500 km — high danger.")
    elif fatalities == "Thousands":
        st.warning("Evacuate nearest cities within 200 km — local destruction possible.")
    else:
        st.success("No major evacuation needed — minor local impact.")

    st.info("✅ Simulation complete. Adjust parameters to explore new outcomes.")

#  SHOW REAL ASTEROID DAta
if show_data:
    st.header("🛰️ 50 Real Asteroids Near Earth")
    df = pd.DataFrame(
        asteroid_dataset,
        columns=[
            "Name / Designation",
            "Diameter (m)",
            "Velocity (km/s)",
            "Close Approach Date (UTC)",
            "Miss Distance (km)",
            "Hazardous (Y/N)"
        ]
    )
    st.dataframe(df, use_container_width=True)
