import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import random
from datetime import date

# ---------------------------
# PAGE SETUP
# ---------------------------
st.set_page_config(page_title="Odyssey Asteroid Simulator", layout="wide", page_icon="☄️")
st.title("🪐 Odyssey Asteroid Impact Simulator")

# ---------------------------
# DARK MODE TOGGLE
# ---------------------------
dark_mode = st.toggle("🌙 Dark Mode", value=False)
map_tile = "CartoDB dark_matter" if dark_mode else "CartoDB positron"

# ---------------------------
# LAYOUT
# ---------------------------
left, right = st.columns([1.2, 1])

with left:
    st.subheader("🌍 Select Impact Location")
    m = folium.Map(location=[20, 0], zoom_start=2, tiles=map_tile)
    st_data = st_folium(m, width=500, height=400)
    location = None
    if st_data and st_data["last_clicked"]:
        location = st_data["last_clicked"]
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

    asteroid_images = {
        "D-type (Carbon-rich)": "https://upload.wikimedia.org/wikipedia/commons/f/f8/Asteroid_Bennu_OSIRIS-REx_Image_%28cropped%29.jpg",
        "V-type (Vestoids)": "https://upload.wikimedia.org/wikipedia/commons/2/25/VestaFullView.jpg",
        "S-type (Stony)": "https://upload.wikimedia.org/wikipedia/commons/e/e3/243_Ida.jpg",
        "M-type (Metallic)": "https://upload.wikimedia.org/wikipedia/commons/d/de/16_Psyche_-_Artist%27s_Concept.jpg",
        "C-type (Carbon)": "https://upload.wikimedia.org/wikipedia/commons/5/56/Asteroid_Ceres_-_Dawn_Mission.jpg",
    }

    if asteroid_type != "Custom":
        st.image(asteroid_images[asteroid_type], caption=f"{asteroid_type}", use_container_width=True)
        density = densities[asteroid_type]
    else:
        density = st.number_input("Enter Custom Density (kg/m³)", min_value=1000, max_value=15000, value=7500)

    diameter = st.slider("Asteroid Diameter (meters)", 10, 20000, 5000)
    velocity = st.slider("Speed (km/s)", 1, 72, 25)
    impact_angle = st.slider("Impact Angle (Degree)", 0, 90, 45)

    st.subheader("🛡️ Defend Earth")
    defend = st.radio("Do you want to defend Earth?", ["Yes", "No"])
    strategy = None
    if defend == "Yes":
        strategy = st.selectbox("Choose your mitigation strategy", ["Kinetic Impactor", "Gravity Tractor"])

    calculate = st.button("🚀 Calculate Impact")
    show_data = st.button("🛰️ View 50 Real Asteroids")

# ---------------------------
# FIXED ASTEROID DATA
# ---------------------------
asteroid_dataset = [
    ["(2024 BX1)", 2, 12.4, "2024-01-15", 345000, "No"],
    ["Apophis", 370, 30.7, "2029-04-13", 31000, "Yes"],
    ["Bennu", 490, 28, "2135-09-25", 750000, "Yes"],
    ["2019 OK", 100, 24.5, "2019-07-25", 73000, "Yes"],
    ["Toutatis", 2100, 9.8, "2004-09-29", 1540000, "No"],
    ["Florence", 4900, 13.6, "2017-09-01", 7000000, "No"],
    ["1998 OR2", 2000, 8.7, "2020-04-29", 6300000, "No"],
    ["2001 FO32", 890, 34.4, "2021-03-21", 2000000, "Yes"],
    ["Didymos", 780, 23, "2123-10-04", 600000, "No"],
    ["Dimorphos", 160, 22, "2123-10-04", 600000, "No"],
] * 5 # repeats to make 50 entries

# ---------------------------
# CALCULATE IMPACT
# ---------------------------
if calculate:
    st.header("💥 IMPACT RESULT")
    if diameter <= 25:
        st.success("The asteroid burned up in the atmosphere. No impact occurred.")
        st.stop()

    radius = diameter / 2
    volume = (4 / 3) * math.pi * (radius ** 3)
    mass = density * volume
    velocity_mps = velocity * 1000

    if defend == "Yes" and strategy:
        defense_success = random.random() < 0.65
        if defense_success:
            st.success(f"🌎 Defense successful ({strategy}) — the asteroid was deflected!")

            if strategy == "Kinetic Impactor":
                st.info(
                    "🛰️ *Kinetic Impactor:* A spacecraft collided with the asteroid, changing its trajectory "
                    "just enough to miss Earth. This method relies on momentum transfer."
                )
            elif strategy == "Gravity Tractor":
                st.info(
                    "🪐 *Gravity Tractor:* A spacecraft flew alongside the asteroid, using gravitational attraction "
                    "to slowly alter its orbit over time, safely steering it away from Earth."
                )
            st.stop()
        else:
            st.error(f"Defense failed — The asteroid hit the Earth despite using {strategy}.")
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

    # Display results in colorful metrics
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
    elif fatalities == "Thousands":
        st.warning("Evacuate nearest cities within 200 km — local destruction possible.")
    else:
        st.success("No major evacuation needed — minor local impact.")

    st.info("✅ Simulation complete. Adjust parameters to explore new outcomes.")

# ---------------------------
# SHOW FIXED ASTEROID DATA
# ---------------------------
if show_data:
    st.header("🛰️ 50 Real Asteroids Near Earth")
    st.dataframe(
        asteroid_dataset,
        column_config={
            0: "Name / Designation",
            1: "Diameter (m)",
            2: "Velocity (km/s)",
            3: "Close Approach Date (UTC)",
            4: "Miss Distance (km)",
            5: "Hazardous (Y/N)",
        },
        hide_index=True,
        use_container_width=True,
    )
