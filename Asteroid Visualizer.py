import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import random
import pandas as pd
import time

st.set_page_config(page_title="Odyssey Asteroid Simulator", layout="wide", page_icon="☄️")
st.title("Odyssey Asteroid Impact Simulator")

if "calc_values" not in st.session_state:
    st.session_state.calc_values = {}
if "defense_window" not in st.session_state:
    st.session_state.defense_window = False
if "defense_choice" not in st.session_state:
    st.session_state.defense_choice = None
if "defense_success" not in st.session_state:
    st.session_state.defense_success = None
if "timer_start" not in st.session_state:
    st.session_state.timer_start = None
if "show_results" not in st.session_state:
    st.session_state.show_results = False

tab_sim, tab_help = st.tabs(["Simulator", "Help"])

with tab_help:
    st.header("How to use the Simulator")
    st.markdown("""
**Overview**  
This simulator estimates asteroid impact effects and demonstrates possible defense strategies.

**Map / Location**
- Click on the map in the **Simulator** tab to select impact coordinates.

**Asteroid Parameters**
- **Asteroid Type** — selects typical density. Use *Custom* for your own density.
- **Diameter (m)** — larger diameter increases mass and kinetic energy.
- **Speed (km/s)** — energy grows with the square of speed.
- **Impact Angle (°)** — shallow angle spreads energy; steep angle concentrates damage.

**Defense Strategies**
- **Kinetic Impactor** — spacecraft hits asteroid to change orbit.
- **Gravity Tractor** — spacecraft slowly pulls asteroid with gravity.
- **Nuclear Detonation** — controlled explosion to alter velocity or fragment asteroid.
- **Laser Ablation** — vaporizes surface to produce small thrust.

**Defense Modal**
- After pressing **Calculate**, a 30-second timer starts. Choose a strategy or do nothing.
- **65% chance** of success if a strategy is chosen in time.
- Successful defense explains the strategy used.

**Impact Results**
- KE, crater diameter, TNT equivalent, casualties, tsunami, and evacuation plan.
- All values are educational estimates.
""")

with tab_sim:
    dark_mode = st.checkbox("Dark Mode", value=False)
    map_tile = "CartoDB dark_matter" if dark_mode else "CartoDB positron"

    left_col, right_col = st.columns([1.2,1])
    with left_col:
        st.subheader("Select Impact Location")
        m = folium.Map(location=[20,0], zoom_start=2, tiles=map_tile)
        map_data = st_folium(m, width=520, height=420)
        location = map_data.get("last_clicked") if map_data else None
        if location:
            st.success(f"Selected Location: {location}")

    with right_col:
        st.subheader("Asteroid Parameters")
        asteroid_type = st.selectbox("Asteroid Type", ["D-type","V-type","S-type","M-type","C-type","Custom"])
        densities = {"D-type":1300,"V-type":3500,"S-type":2700,"M-type":7800,"C-type":1700}
        density = densities[asteroid_type] if asteroid_type != "Custom" else st.number_input("Custom Density kg/m³",1000,15000,7500)
        diameter = st.slider("Diameter meters",10,20000,5000)
        velocity = st.slider("Speed km/s",1,72,25)
        impact_angle = st.slider("Impact Angle degrees",0,90,45)

        calculate = st.button("Calculate Impact")
        show_data = st.button("View 51 Real Asteroids")

    asteroid_dataset = [["2024 BX1", 2, 12.4, "2024-01-15", 345000, "N"],["Apophis", 370, 30.7, "2029-04-13", 31000, "Y"],["Bennu", 490, 28.0, "2135-09-25", 750000, "Y"],["2019 OK", 100, 24.5, "2019-07-25", 73000, "Y"],["Toutatis", 2100, 9.8, "2004-09-29", 1540000, "N"],["Florence", 4900, 13.6, "2017-09-01", 7000000, "N"]]

    if show_data:
        st.header("51 Real Asteroids")
        df = pd.DataFrame(asteroid_dataset,columns=["Name","Diameter","Velocity","Close Approach","Miss Distance","Hazardous"])
        st.dataframe(df, width="stretch")

    if calculate:
        r = diameter/2
        vol = 4/3*math.pi*r**3
        mass = density*vol
        v_mps = velocity*1000
        KE = 0.5*mass*v_mps**2
        crater = (KE/1e12)**0.3
        TNT = KE/4.184e9
        tsunami = "No significant tsunami"
        if impact_angle<45 and KE>1e15 and diameter>50:
            tsunami_m = (KE/1e18)**0.25*(diameter/1000)**0.5*(45/(impact_angle+1))
            tsunami_m = max(1.0, tsunami_m)
            tsunami = f"{tsunami_m:.2f} m approx"
        if KE>2e50: fatalities="Billions"
        elif KE>1e18: fatalities="Millions"
        elif KE>1e16: fatalities="Thousands"
        else: fatalities="Few hundreds"

        st.session_state.calc_values={"mass":mass,"KE":KE,"crater":crater,"TNT":TNT,"tsunami":tsunami,"fatalities":fatalities,"velocity_mps":v_mps,"location":location,"diameter":diameter,"impact_angle":impact_angle}
        st.session_state.defense_window=True
        st.session_state.timer_start=time.time()
        st.session_state.show_results=False

    if st.session_state.defense_window:
        elapsed=int(time.time()-st.session_state.timer_start)
        remaining=max(0,30-elapsed)
        st.subheader(f"Choose Defense Strategy Time left: {remaining} sec")
        cols=st.columns(2)
        if cols[0].button("Kinetic Impactor"): st.session_state.defense_choice="Kinetic Impactor"; st.session_state.defense_window=False
        if cols[1].button("Gravity Tractor"): st.session_state.defense_choice="Gravity Tractor"; st.session_state.defense_window=False
        if cols[0].button("Nuclear Detonation"): st.session_state.defense_choice="Nuclear Detonation"; st.session_state.defense_window=False
        if cols[1].button("Laser Ablation"): st.session_state.defense_choice="Laser Ablation"; st.session_state.defense_window=False
        if st.button("Do Not Defend"): st.session_state.defense_choice=None; st.session_state.defense_window=False

        if remaining==0: st.session_state.defense_window=False; st.session_state.defense_choice=None

        if not st.session_state.defense_window:
            choice=st.session_state.defense_choice
            if choice:
                success=random.random()<0.65
                st.session_state.defense_success=success
                if success: st.success(f"Defense Successful using {choice}")
                else:
                    st.error(f"Defense Failed using {choice}")
                    if choice=="Kinetic Impactor": st.session_state.calc_values["velocity_mps"]*=0.9
                    elif choice=="Gravity Tractor": st.session_state.calc_values["velocity_mps"]*=0.95
                    elif choice=="Nuclear Detonation": st.session_state.calc_values["velocity_mps"]*=0.85
                    elif choice=="Laser Ablation": st.session_state.calc_values["velocity_mps"]*=0.97
            st.session_state.show_results=True

    if st.session_state.show_results and st.session_state.calc_values:
        vals=st.session_state.calc_values
        KE=0.5*vals["mass"]*vals["velocity_mps"]**2
        st.header("Impact Result")
        st.metric("Kinetic Energy",f"{KE:.2e} J")
        st.metric("Asteroid Mass",f"{vals['mass']:.2e} kg")
        st.metric("Crater Diameter",f"{vals['crater']:.2f} km")
        st.metric("TNT Equivalent",f"{vals['TNT']:.2e} tons")
        st.metric("Casualties",vals["fatalities"])
        st.metric("Tsunami Estimate",vals["tsunami"])
        if st.session_state.defense_success:
            st.success(f"Earth protected by {st.session_state.defense_choice}")
        else:
            st.error("Asteroid hit Earth. Follow safety plans.")
