import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import random
import pandas as pd
import time

# ---------------------------
# PAGE SETUP
# ---------------------------
st.set_page_config(page_title="Odyssey Asteroid Simulator", layout="wide", page_icon="☄️")
st.title("🪐 Odyssey Asteroid Impact Simulator")

# ---------------------------
# SESSION STATE INIT
# ---------------------------
if "calc_values" not in st.session_state:
    st.session_state.calc_values = {}
if "defense_choice" not in st.session_state:
    st.session_state.defense_choice = None
if "defense_success" not in st.session_state:
    st.session_state.defense_success = None
if "timer_start" not in st.session_state:
    st.session_state.timer_start = None
if "awaiting_defense" not in st.session_state:
    st.session_state.awaiting_defense = False

# ---------------------------
# HELP & INFO TAB
# ---------------------------
tab_sim, tab_help = st.tabs(["🧭 Simulator", "ℹ️ Help & Info"])
with tab_help:
    st.header("How to use Odyssey Asteroid Impact Simulator")
    st.markdown("""
**Overview**  
This simulator estimates asteroid impact consequences and demonstrates defense strategies.

**Map / Location**
- Click on the map to select the impact location. Last clicked coordinates are used.

**Asteroid Parameters**
- **Asteroid Type** — selects typical density. "Custom" allows manual density input.
- **Diameter (m)** — larger diameter → more mass → more energy.
- **Speed (km/s)** — energy grows with velocity squared.
- **Impact Angle (°)** — shallow angles spread energy; steep angles concentrate it.

**Defense Strategies**
- **Kinetic Impactor** — spacecraft collides to nudge asteroid.
- **Gravity Tractor** — spacecraft slowly alters asteroid orbit via gravity.
- **Nuclear Detonation** — extreme, high-risk trajectory change.
- **Laser Ablation** — vaporizes surface to create thrust and alter path.

**Defense Window**
- After **Calculate**, you have **30 seconds** to choose a defense.
- If time expires or you choose "Do not defend", asteroid hits Earth.
- Success probability = 65%. If successful, explanation is shown.

**Impact & Safety**
- KE, crater, TNT, casualties, tsunami, evacuation plan are shown.
- Educational estimates only.
""")

# ---------------------------
# SIMULATOR TAB
# ---------------------------
with tab_sim:
    # Dark mode
    dark_mode = st.checkbox("🌙 Dark Mode", value=False)
    map_tile = "CartoDB dark_matter" if dark_mode else "CartoDB positron"

    left_col, right_col = st.columns([1.2, 1])

    # ---------------------------
    # LEFT: MAP
    # ---------------------------
    with left_col:
        st.subheader("🌍 Select Impact Location")
        st.write("Click the map to choose coordinates.")
        m = folium.Map(location=[20, 0], zoom_start=2, tiles=map_tile)
        st_data = st_folium(m, width=520, height=420)
        location = None
        if st_data and st_data.get("last_clicked"):
            location = st_data.get("last_clicked")
            st.success(f"📍 Selected Location: {location}")

    # ---------------------------
    # RIGHT: PARAMETERS
    # ---------------------------
    with right_col:
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

        calculate = st.button("🚀 Calculate Impact")
        show_data = st.button("🛰️ View 51 Real Asteroids")

    # ---------------------------
    # ASTEROID DATA
    # ---------------------------
    asteroid_dataset = [
        ["2024 BX1", 2, 12.4, "2024-01-15", 345000, "N"],
        ["Apophis", 370, 30.7, "2029-04-13", 31000, "Y"],
        ["Bennu", 490, 28.0, "2135-09-25", 750000, "Y"],
        ["2019 OK", 100, 24.5, "2019-07-25", 73000, "Y"],
        # ... add the remaining 47 asteroids ...
    ]

    # ---------------------------
    # CALCULATION
    # ---------------------------
    if calculate:
        radius = diameter / 2
        volume = (4/3)*math.pi*(radius**3)
        mass = density * volume
        velocity_mps = velocity * 1000
        KE = 0.5*mass*(velocity_mps**2)
        crater_diameter = (KE / 1e12)**0.3
        TNT = KE / 4.184e9

        # tsunami estimate
        tsunami = "No significant tsunami"
        if impact_angle < 45 and KE > 1e15 and diameter > 50:
            tsunami_m = (KE / 1e18)**0.25 * (diameter / 1000)**0.5 * (45 / (impact_angle+1))
            tsunami_m = max(1.0, tsunami_m)
            tsunami = f"{tsunami_m:.2f} meters (approx.)"

        # fatalities heuristic
        if KE > 2e50:
            fatalities = "Billions"
        elif KE > 1e18:
            fatalities = "Millions"
        elif KE > 1e16:
            fatalities = "Thousands"
        else:
            fatalities = "Few hundreds"

        # store values
        st.session_state.calc_values = {
            "radius": radius,
            "volume": volume,
            "mass": mass,
            "velocity_mps": velocity_mps,
            "KE": KE,
            "crater_diameter": crater_diameter,
            "TNT": TNT,
            "tsunami": tsunami,
            "fatalities": fatalities,
            "impact_angle": impact_angle,
            "diameter": diameter,
            "location": location
        }
        st.session_state.awaiting_defense = True
        st.session_state.timer_start = time.time()

    # ---------------------------
    # DEFENSE PANEL
    # ---------------------------
    if st.session_state.awaiting_defense:
        elapsed = int(time.time() - st.session_state.timer_start)
        remaining = max(0, 30 - elapsed)
        st.warning(f"⚠️ Incoming asteroid! Choose defense within 30 seconds. ⏳ {remaining}s left")
        col1, col2 = st.columns(2)
        if col1.button("🛰️ Kinetic Impactor"):
            st.session_state.defense_choice = "Kinetic Impactor"
        if col2.button("🪐 Gravity Tractor"):
            st.session_state.defense_choice = "Gravity Tractor"
        if col1.button("💣 Nuclear Detonation"):
            st.session_state.defense_choice = "Nuclear Detonation"
        if col2.button("🔭 Laser Ablation"):
            st.session_state.defense_choice = "Laser Ablation"
        if st.button("🚫 Do Not Defend"):
            st.session_state.defense_choice = None

        if remaining <= 0 or st.session_state.defense_choice is not None:
            choice = st.session_state.defense_choice
            st.session_state.awaiting_defense = False
            if choice is None:
                st.session_state.defense_success = False
            else:
                st.session_state.defense_success = random.random() < 0.65

            st.experimental_rerun()

    # ---------------------------
    # SHOW IMPACT RESULTS
    # ---------------------------
    if st.session_state.calc_values and not st.session_state.awaiting_defense:
        vals = st.session_state.calc_values
        mass = vals["mass"]
        velocity_mps = vals["velocity_mps"]
        KE = 0.5*mass*(velocity_mps**2)
        crater_diameter = vals["crater_diameter"]
        TNT = vals["TNT"]
        tsunami = vals["tsunami"]
        fatalities = vals["fatalities"]

        if st.session_state.defense_success:
            st.header("🛡️ Defense Outcome")
            st.success(f"Earth was protected by **{st.session_state.defense_choice}**!")
        else:
            st.header("💥 Impact Result (Asteroid Impacted Earth)")
            if vals["location"]:
                st.write(f"**Impact Coordinates:** {vals['location']}")
            st.metric("🌑 Kinetic Energy", f"{KE:.2e} J")
            st.metric("🌍 Mass", f"{mass:.2e} kg")
            st.metric("☄️ Crater Diameter", f"{crater_diameter:.2f} km")
            st.metric("💣 TNT Equivalent", f"{TNT:.2e} tons")
            st.metric("👥 Estimated Casualties", fatalities)
            st.metric("🌊 Tsunami Estimate", tsunami)

            # Evacuation
            st.subheader("🚨 Evacuation & Safety Plan")
            if fatalities == "Billions":
                st.warning("Global catastrophe: evacuate all coastal/low-lying regions immediately.")
            elif fatalities == "Millions":
                st.warning("Major regional disaster: evacuate densely populated zones within 500 km.")
            elif fatalities == "Thousands":
                st.info("Local damage: evacuate cities within ~200 km.")
            else:
                st.success("Minor local impact: local authorities manage risk.")

        # clear session for next run
        st.session_state.calc_values = {}
        st.session_state.defense_choice = None
        st.session_state.defense_success = None

    # ---------------------------
    # SHOW ASTEROID DATA
    # ---------------------------
    if show_data:
        st.header("🛰️ 51 Real Asteroids Near Earth (Fixed Dataset)")
        df = pd.DataFrame(asteroid_dataset, columns=["Name", "Diameter (m)", "Velocity (km/s)", "Close Approach Date", "Miss Distance (km)", "Hazardous"])
        st.dataframe(df, hide_index=True, use_container_width=True)
