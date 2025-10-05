import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import random
import pandas as pd

# ---------------------------
# 🌍 PAGE SETUP
# ---------------------------
st.set_page_config(page_title="Odyssey Asteroid Simulator", layout="wide", page_icon="☄️")
st.title("☄️ Odyssey Asteroid Impact Simulator")
st.write("Simulate asteroid impacts, visualize outcomes, and explore real NASA asteroid data!")

# ---------------------------
# 🌍 MAP AND CONTROLS
# ---------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🌎 Select Impact Location")
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")
    st_data = st_folium(m, width=450, height=350)
    location = None
    if st_data and st_data.get("last_clicked"):
        location = st_data["last_clicked"]
        st.write("**Selected Location:**", location)

with col2:
    st.subheader("⚙️ Asteroid Parameters")
    asteroid_type = st.selectbox(
        "Asteroid Type",
        ["D-type (Carbon-rich)", "V-type (Vestoids)", "S-type (Stony)",
         "M-type (Metallic)", "C-type (Carbon)", "Custom"]
    )

    densities = {
        "D-type (Carbon-rich)": 1300,
        "V-type (Vestoids)": 3500,
        "S-type (Stony)": 2700,
        "M-type (Metallic)": 7800,
        "C-type (Carbon)": 1700
    }

    asteroid_images = {
        "D-type (Carbon-rich)": "https://upload.wikimedia.org/wikipedia/commons/4/45/Bennu_OSIRIS-REx.png",
        "V-type (Vestoids)": "https://upload.wikimedia.org/wikipedia/commons/2/25/VestaFullView.jpg",
        "S-type (Stony)": "https://upload.wikimedia.org/wikipedia/commons/e/e3/243_Ida.jpg",
        "M-type (Metallic)": "https://upload.wikimedia.org/wikipedia/commons/d/de/16_Psyche_-_Artist%27s_Concept.jpg",
        "C-type (Carbon)": "https://upload.wikimedia.org/wikipedia/commons/5/5b/Asteroid_Bennu.png",
    }

    if asteroid_type != "Custom":
        st.image(asteroid_images[asteroid_type], caption=f"{asteroid_type}", use_container_width=True)

    if asteroid_type == "Custom":
        density = st.number_input("Enter Custom Density (kg/m³)", min_value=1000, max_value=15000, value=7500)
    else:
        density = densities[asteroid_type]

    diameter = st.slider("Asteroid Diameter (m)", 10, 20000, 5000)
    velocity = st.slider("Speed (km/s)", 1, 72, 25)
    impact_angle = st.slider("Impact Angle (°)", 0, 90, 45)

    st.subheader("🛡️ Defend Earth")
    defend = st.radio("Do you want to defend Earth?", ["Yes", "No"])
    strategy = None
    if defend == "Yes":
        strategy = st.selectbox("Choose your strategy", ["Kinetic Impactor", "Gravity Tractor"])

    colA, colB = st.columns(2)
    with colA:
        calculate = st.button("🚀 Calculate Impact")
    with colB:
        show_data = st.button("📡 View Real Asteroid Data")

# ---------------------------
# 📊 REAL ASTEROID DATA
# ---------------------------
if show_data:
    st.subheader("🪐 Real Near-Earth Asteroids (Sample NASA Data)")
    df = pd.DataFrame({
        "Name": ["Apophis", "Bennu", "Didymos", "Psyche", "Vesta"],
        "Diameter (m)": [340, 490, 780, 226000, 525000],
        "Velocity (km/s)": [30.7, 28.0, 23.6, 19.4, 20.3],
        "Potential Hazard": ["No", "Possibly", "Possibly", "Yes", "Yes"],
        "Closest Approach": ["2029-04-13", "2135-09-25", "2123-11-18", "N/A", "N/A"]
    })
    st.dataframe(df, use_container_width=True)

# ---------------------------
# 💥 IMPACT SIMULATION
# ---------------------------
if calculate:
    st.divider()
    st.header("💥 Impact Results")

    if diameter <= 25:
        st.success("The asteroid burned up in Earth's atmosphere. No impact occurred.")
        st.stop()

    radius = diameter / 2
    volume = (4 / 3) * math.pi * (radius ** 3)
    mass = density * volume
    velocity_mps = velocity * 1000

    # Defense system
    if defend == "Yes" and strategy:
        defense_success = random.random() < 0.65
        if defense_success:
            st.success(f"🛡️ Defense Successful using {strategy}!")
            if strategy == "Kinetic Impactor":
                st.info(
                    "A high-speed spacecraft was launched to collide with the asteroid. "
                    "The impact changed its path slightly, but enough to prevent collision with Earth. "
                    "This method relies on momentum transfer and precise timing."
                )
            elif strategy == "Gravity Tractor":
                st.info(
                    "A spacecraft matched the asteroid’s orbit and used gentle gravitational attraction "
                    "to slowly pull it off course over time. This method is subtle but extremely effective "
                    "for long-term deflection missions."
                )
            st.stop()
        else:
            st.error(f"⚠️ Defense Failed using {strategy}. The asteroid hit Earth.")
            if strategy == "Kinetic Impactor":
                velocity_mps *= 0.9
            elif strategy == "Gravity Tractor":
                velocity_mps *= 0.95

    # Physics calculations
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
        fatalities = "Few Hundreds"

    if impact_angle < 45 and KE > 1e15:
        tsunami = f"{round(KE / 1e15, 2)} meters high (approx.)"
    else:
        tsunami = "No significant tsunami"

    # ---------------------------
    # 📈 COLORFUL METRICS (via emojis)
    # ---------------------------
    st.subheader("📊 Impact Summary")
    c1, c2, c3 = st.columns(3)
    c1.metric("Kinetic Energy 💥", f"{KE:.2e} J")
    c2.metric("Asteroid Mass 🪨", f"{mass:.2e} kg")
    c3.metric("Crater Diameter 🌋", f"{crater_diameter:.2f} km")

    c4, c5, c6 = st.columns(3)
    c4.metric("TNT Equivalent 💣", f"{TNT:.2e} tons")
    c5.metric("Estimated Casualties ☠️", fatalities)
    c6.metric("Tsunami Height 🌊", tsunami)

    # ---------------------------
    # 🚨 EVACUATION PLAN
    # ---------------------------
    st.subheader("🚨 Evacuation & Safety Plan")
    if fatalities == "Billions":
        st.warning("Evacuate **all areas within 1000 km**. Global impact possible.")
    elif fatalities == "Millions":
        st.warning("Evacuate **coastal and populated areas within 500 km**. Severe atmospheric effects expected.")
    elif fatalities == "Thousands":
        st.info("Evacuate **nearest cities within 200 km**. Move inland and stay alert.")
    else:
        st.success("Minimal local impact. No major evacuation required.")

    st.success("✅ Simulation complete! Try changing parameters to explore more outcomes.")
    if st.button("🔁 Simulate Again"):
        st.experimental_rerun()
