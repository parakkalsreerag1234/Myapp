import streamlit as st
import folium
from streamlit_folium import st_folium
import math
import random
import pandas as pd
import time

# PAGE SETUP
st.set_page_config(page_title="Odyssey Asteroid Simulator", layout="wide", page_icon="☄️")
st.title("🪐 Odyssey Asteroid Impact Simulator")
# INITIALIZE session_state
if "awaiting_defense" not in st.session_state:
    st.session_state.awaiting_defense = False
if "timer_end" not in st.session_state:
    st.session_state.timer_end = None
if "defense_choice" not in st.session_state:
    st.session_state.defense_choice = None
if "defense_success" not in st.session_state:
    st.session_state.defense_success = None
if "calc_values" not in st.session_state:
    st.session_state.calc_values = {}
# TABS: Simulator and Help
tab_sim, tab_help = st.tabs(["🧭 Simulator", "ℹ️ Help & Info"])

with tab_help:
    st.header("How to use Odyssey Asteroid Impact Simulator")
    st.markdown(
        """
**Overview**  
This simulator estimates the consequences of an asteroid impact based on user-set parameters and demonstrates possible defense strategies.

**Map / Location**
- Click on the map in the **Simulator** tab to select an impact location. The app will show the last clicked coordinates.

**Asteroid Parameters**
- **Asteroid Type** — selects a typical density for the object. If you choose *Custom*, enter your own density (kg/m³).
- **Diameter (meters)** — bigger diameter -> more mass -> dramatically more energy on impact (energy ∝ mass).
- **Speed (km/s)** — kinetic energy grows with the square of speed. Doubling speed quadruples kinetic energy.
- **Impact Angle (°)** — shallow angles (small degree) spread energy over a larger area, often creating wider but shallower damage; steep angles focus energy and create deeper craters.

**What the sliders affect**
- **Mass** = density × volume (volume ∝ diameter³) — diameter is the strongest factor for mass.
- **Kinetic Energy (KE)** = 0.5 × mass × velocity² — both mass (diameter) and velocity matter.
- **Crater size** and **TNT equivalent** scale with KE (using simplified empirical relationships here).
- **Tsunami**: if an ocean impact is simulated (or low angle + high energy), the app estimates likely tsunami height.

**Defense Strategies (available in the Simulator modal after pressing Calculate)**
- **Kinetic Impactor** — crash a spacecraft into the asteroid to nudge it off course (quick, proven concept).
- **Gravity Tractor** — a spacecraft flies alongside and slowly alters the asteroid's path using gravity (slow, precise).
- **Nuclear Detonation** — a sub-surface or near-surface blast to change trajectory or fragment the body (extreme, risky).
- **Laser Ablation** — concentrate energy to vaporize surface, creating thrust that redirects the object (future-tech).
  
**Defense modal & timing**
- After pressing **Calculate**, a 30-second defense modal appears automatically. Choose a defense within 30s or do nothing — if time runs out the asteroid impacts.
- If a defense is chosen in time, there's a **65% chance** the defense succeeds (simulated probabilistically). If it succeeds, the app will explain how the chosen strategy worked.

**Impact Results and Safety**
- The app provides KE, crater diameter, TNT equivalent, estimated casualties band, tsunami estimate, and a multi-level evacuation & safety plan with practical advice.
- Results are **illustrative educational estimates** and are not a substitute for real hazard modeling.

---
"""
    )

with tab_sim:
    # DARK MODE AND MAP + CONTROLS LAYOUT
    dark_mode = st.checkbox("🌙 Dark Mode", value=False)
    map_tile = "CartoDB dark_matter" if dark_mode else "CartoDB positron"

    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        st.subheader("🌍 Select Impact Location")
        st.write("Click the map to choose impact coordinates (last clicked location will be used).")
        m = folium.Map(location=[20, 0], zoom_start=2, tiles=map_tile)
        st_data = st_folium(m, width=520, height=420)
        location = None
        if st_data and st_data.get("last_clicked"):
            location = st_data.get("last_clicked")
            st.success(f"📍 Selected Location: {location}")

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

        st.subheader("🛡️ Defend Earth (will appear after Calculate)")
        st.write("Defense selection happens inside a 30s popup after you click **Calculate**.")
        # calculate and view data buttons
        calculate = st.button("🚀 Calculate Impact")
        show_data = st.button("🛰️ View 51 Real Asteroids")

    # FIXED ASTEROID DATA (51 rows) 
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
        ["2015 SO2", 50, 7.5, "2015-09-29", 123000, "N"]
    ]

    
    #  CALCULATION ON BUTTON
    if calculate:
        # --- compute physics and store in session_state ---
        radius = diameter / 2
        volume = (4 / 3) * math.pi * (radius ** 3)
        mass = density * volume
        velocity_mps = velocity * 1000
        KE = 0.5 * mass * (velocity_mps ** 2)
        crater_diameter = (KE / 1e12) ** 0.3
        TNT = KE / 4.184e9

        # improved tsunami estimate (illustrative):
        tsunami = "No significant tsunami"
        # Only estimate tsunami for large, energetic, shallow-angle impacts
        if impact_angle < 45 and KE > 1e15 and diameter > 50:
            # a heuristic estimate: increases with energy and diameter, decreases with angle
            tsunami_m = (KE / 1e18) ** 0.25 * (diameter / 1000) ** 0.5 * (45 / (impact_angle + 1))
            tsunami_m = max(1.0, tsunami_m) # minimum meaningful height
            tsunami = f"{tsunami_m:.2f} meters (approx.)"

        # casualties band (simple heuristics)
        if KE > 2e50:
            fatalities = "Billions"
        elif KE > 1e18:
            fatalities = "Millions"
        elif KE > 1e16:
            fatalities = "Thousands"
        else:
            fatalities = "Few hundreds"

        # store all computed values so they persist through modal interactions
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
            "location": location,
        }

        # set modal/timer state
        st.session_state.awaiting_defense = True
        st.session_state.timer_end = time.time() + 30 # 30-second countdown
        st.session_state.defense_choice = None
        st.session_state.defense_success = None

        # force rerun so modal will appear immediately
        st.experimental_rerun()

    # SHOW MODAL IF AWAITING DEFENSE
    if st.session_state.awaiting_defense:
        # use Streamlit modal (appears as centered pop-up)
        with st.modal("⚠️ DEFENSE ALERT — Choose a strategy (30s)"):
            st.markdown("**An incoming asteroid has been detected!** You have **30 seconds** to choose a defense strategy.\n\nIf no strategy is chosen before time runs out, the asteroid will impact Earth.")
            # show dynamic countdown and offer choice buttons
            countdown_placeholder = st.empty()
            btn_col = st.columns(2)
            choose_col_left = btn_col[0]
            choose_col_right = btn_col[1]

            # If timer expired, mark failure and close modal
            remaining = int(st.session_state.timer_end - time.time())
            if remaining <= 0:
                # time up: user missed the window
                st.session_state.awaiting_defense = False
                st.session_state.defense_choice = None
                st.session_state.defense_success = False
                st.experimental_rerun()

            # Show countdown
            countdown_placeholder.markdown(f"### ⏳ Time left: **{remaining}s**")

            # Four defense options + "Do not defend"
            if choose_col_left.button("🛰️ Kinetic Impactor"):
                st.session_state.defense_choice = "Kinetic Impactor"
                st.session_state.awaiting_defense = False
            if choose_col_right.button("🪐 Gravity Tractor"):
                st.session_state.defense_choice = "Gravity Tractor"
                st.session_state.awaiting_defense = False
            if choose_col_left.button("💣 Nuclear Detonation"):
                st.session_state.defense_choice = "Nuclear Detonation"
                st.session_state.awaiting_defense = False
            if choose_col_right.button("🔭 Laser Ablation"):
                st.session_state.defense_choice = "Laser Ablation"
                st.session_state.awaiting_defense = False
            if st.button("🚫 Do Not Defend"):
                st.session_state.defense_choice = None
                st.session_state.awaiting_defense = False

            # If user just chose a defense, determine outcome
            if st.session_state.defense_choice is not None and st.session_state.awaiting_defense is False:
                # roll success (65% chance)
                success = random.random() < 0.65
                st.session_state.defense_success = success
                # store which strategy used
                chosen = st.session_state.defense_choice
                # show immediate feedback in modal
                if success:
                    st.success(f"✅ Defense successful! Strategy used: {chosen}")
                    # explain the chosen strategy briefly
                    if chosen == "Kinetic Impactor":
                        st.info(
                            "Kinetic Impactor: A spacecraft collides with the asteroid to transfer momentum and change its orbit."
                        )
                    elif chosen == "Gravity Tractor":
                        st.info(
                            "Gravity Tractor: A spacecraft uses its gravitational pull over time to slowly tug the asteroid onto a safer trajectory."
                        )
                    elif chosen == "Nuclear Detonation":
                        st.info(
                            "Nuclear Detonation: A controlled detonation near or on the asteroid can change its velocity or fragment it. This method is high-risk and would be used only in critical scenarios."
                        )
                    elif chosen == "Laser Ablation":
                        st.info(
                            "Laser Ablation: Concentrated energy vaporizes surface material, producing a small thrust that can alter the asteroid's path over time."
                        )
                    # Close modal and rerun to show result page
                    st.session_state.awaiting_defense = False
                    st.experimental_rerun()
                else:
                    st.error(f"❌ Defense failed. Strategy: {chosen}")
                    # slight partial effect (reduce velocity somewhat depending on method)
                    if chosen == "Kinetic Impactor":
                        st.session_state.calc_values["velocity_mps"] *= 0.9
                    elif chosen == "Gravity Tractor":
                        st.session_state.calc_values["velocity_mps"] *= 0.95
                    elif chosen == "Nuclear Detonation":
                        st.session_state.calc_values["velocity_mps"] *= 0.85
                    elif chosen == "Laser Ablation":
                        st.session_state.calc_values["velocity_mps"] *= 0.97
                    st.session_state.awaiting_defense = False
                    st.experimental_rerun()

            # If no choice yet, sleep 1s then rerun to update countdown
            time.sleep(1)
            st.experimental_rerun()
    # AFTER DEFENSE WINDOW: SHOW RESULTS BASED ON OUTCOME
    if st.session_state.defense_success:
        chosen = st.session_state.defense_choice
        st.header("🛡️ Defense Outcome")
        st.success(f"Earth was protected by **{chosen}**.")
        if chosen == "Kinetic Impactor":
            st.info(
                "Kinetic Impactor succeeded: a spacecraft changed the asteroid's trajectory just enough to avoid impact. "
                "This works by transferring momentum to the object."
            )
        elif chosen == "Gravity Tractor":
            st.info(
                "Gravity Tractor succeeded: the spacecraft used continuous gravitational attraction to slowly alter the asteroid's orbit."
            )
        elif chosen == "Nuclear Detonation":
            st.info(
                "Nuclear Detonation succeeded: a controlled nuclear event altered the asteroid's motion (extreme and high-risk technique)."
            )
        elif chosen == "Laser Ablation":
            st.info(
                "Laser Ablation succeeded: vaporization produced thrust that nudged the asteroid off an impact trajectory."
            )

        st.balloons()
        # reset defense flags so user can run another sim if desired
        st.session_state.defense_success = None
        st.session_state.defense_choice = None
        st.session_state.calc_values = {}

    # If defense did not succeed (either failure or user chose not to defend or time expired), show full impact results
    elif (not st.session_state.defense_success) and st.session_state.calc_values:
        # recompute KE if velocity changed due to failed defense
        vals = st.session_state.calc_values
        mass = vals["mass"]
        velocity_mps = vals["velocity_mps"]
        KE = 0.5 * mass * (velocity_mps ** 2)
        crater_diameter = vals["crater_diameter"]
        TNT = KE / 4.184e9
        tsunami = vals["tsunami"]
        fatalities = vals["fatalities"]

        st.header("💥 Impact Result (Asteroid Impacted Earth)")
        st.write(f"**Asteroid Type:** {asteroid_type}")
        if vals["location"]:
            st.write(f"**Impact Coordinates:** {vals['location']}")
        st.metric("🌑 Kinetic Energy", f"{KE:.2e} J")
        st.metric("🌍 Asteroid Mass", f"{mass:.2e} kg")
        st.metric("☄️ Crater Diameter", f"{crater_diameter:.2f} km")
        st.metric("💣 TNT Equivalent", f"{TNT:.2e} tons")
        st.metric("👥 Estimated Casualties", fatalities)
        st.metric("🌊 Tsunami Estimate", tsunami)
        
        st.subheader("🚨 Evacuation & Safety Plan ")
        st.write("The following guidance is illustrative and educational — in a real event follow official agency instructions.")

        if fatalities == "Billions":
            st.warning("**Global Catastrophe:** Evacuate all coastal and low-lying regions immediately if safe. Expect long-term atmospheric effects and global infrastructure disruption.")
            st.write("- Move to higher ground if coastal. \n- Secure food, water, and medical supplies for long durations. \n- Expect agricultural impacts and global supply chain interruptions. \n- Follow official guidance for relocation and international aid.")
        elif fatalities == "Millions":
            st.warning("**Major Regional Disaster:** Evacuate coastal and densely populated zones within 500 km of the impact site.")
            st.write("- Urgently move inland and to higher ground if within 500 km of impact. \n- Prepare for atmospheric fallout and local fires. \n- Assist vulnerable populations and coordinate with emergency services.")
        elif fatalities == "Thousands":
            st.info("**Significant Local Damage:** Evacuate cities within ~200 km of impact and follow local authority instructions.")
            st.write("- Move to designated shelters and higher elevation if tsunami risk exists. \n- Expect infrastructure disruption and possible secondary hazards (fires, power outages).")
        else:
            st.success("**Minor Local Impact:** Local authorities will manage risks. No large-scale evacuation likely.")
            st.write("- Avoid the immediate impact zone. \n- Monitor official channels for updates and assistance.")

        st.write("**General safety tips:** \n- Have an emergency kit (water, canned food, radio, flashlight). \n- Stay away from windows during shockwaves. \n- Seek medical help for injuries and follow evacuation orders.")

        # after showing results, clear calc_values so user can run a new simulation
        st.session_state.calc_values = {}
    # SHOW 51 ASTEROID DATA 
    if show_data:
        st.header("🛰️ 51 Real Asteroids Near Earth (Fixed Dataset)")
        df = pd.DataFrame(
            asteroid_dataset,
            columns=["Name / Designation", "Diameter (m)", "Velocity (km/s)", "Close Approach Date", "Miss Distance (km)", "Hazardous (Y/N)"]
        )
        st.dataframe(df, hide_index=True, use_container_width=True)
