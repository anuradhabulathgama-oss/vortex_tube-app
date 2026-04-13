import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# -------------------------------------------------------------------------🌪⚙️🌀⚠✅⚠
# 1. PAGE CONFIGURATION
# -------------------------------------------------------------------------
# Set the page to wide mode so our graphs have room to breathe
st.set_page_config(page_title="Vortex Tube Simulator", layout="wide")
st.markdown("<style> .block-container { padding-top: 1rem; padding-bottom: 0rem; } </style>", unsafe_allow_html=True)

st.title("️ Theoretical Vortex Tube Model")
st.markdown("Analyzes the thermodynamic limits of a vortex tube using the First and Second Law of Thermodynamics. This model assumes adiabatic operation and equal outlet pressures.")


# -------------------------------------------------------------------------
# 2. THE UI CONTROLS (Sidebar)
# -------------------------------------------------------------------------
# st.sidebar puts these controls in a collapsible panel on the left
with st.sidebar:
    st.header(" Operating Parameters")
    
    # st.slider(label, min_value, max_value, default_value, step)
    T_in = st.slider("Inlet Temperature (K)", 250.0, 400.0, 295.0, step=1.0)
    T_H  = st.slider("Hot Outlet Temperature (K)", 250.0, 450.0, 320.0, step=1.0)
    f    = st.slider("Cold Fraction (f)", 0.1, 0.9, 0.5, step=0.01)
    
    st.divider() # Adds a visual line
    
    P_in  = st.slider("Inlet Pressure (kPa)", 20.0, 800.0, 500.0, step=10.0)
    P_out = st.slider("Outlet Pressure (kPa)", 20.0, 800.0, 101.325, step=1.0)

# -------------------------------------------------------------------------
# 3. THERMODYNAMIC CALCULATIONS
# -------------------------------------------------------------------------
Cp = 1005.0 
R  = 287.0  

# --- Calculate the Single Operating Point (Based on the 'f' slider) ---
T_C= (T_in - (1 - f) * T_H) / f

dS_cold = Cp * np.log(T_C / T_in) - R * np.log(P_out / P_in)
dS_hot  = Cp * np.log(T_H / T_in) - R * np.log(P_out / P_in)
s_gen = f * dS_cold + (1 - f) * dS_hot

# --- Calculate the Full Arrays (For the Plots) ---
f_array = np.linspace(0.1, 0.9, 100)
TC_array = (T_in - (1 - f_array) * T_H) / f_array

dS_cold_array = Cp * np.log(TC_array / T_in) - R * np.log(P_out / P_in)
dS_hot_array  = Cp * np.log(T_H / T_in) - R * np.log(P_out / P_in)
s_gen_array = (f_array * dS_cold_array) + ((1 - f_array) * dS_hot_array)

# Masking for physically possible states
valid_mask = s_gen_array >= 0
invalid_mask = s_gen_array < 0

TC_valid = np.where(valid_mask, TC_array, np.nan)
TC_invalid = np.where(invalid_mask, TC_array, np.nan)

# -------------------------------------------------------------------------
# 4. DASHBOARD METRICS (The Results)
# -------------------------------------------------------------------------
# st.columns splits the screen into vertical sections
col1, col2, col3 = st.columns(3)

with col1:
    # st.metric creates beautiful, large number callouts
    st.metric(label="Cold Outlet Temp (Tc)", value=f"{T_C:.2f} K")
    
with col2:
    st.metric(label="Entropy Generation Rate", value=f"{s_gen:.2f} J/kg·K")
    
with col3:
    # Use Streamlit's built-in alert boxes to show the 2nd Law status
    if s_gen < 0:
        st.error("️ Violates 2nd Law")
    else:
        st.success(" Theoretically Possible")

import matplotlib.patches as patches

# -------------------------------------------------------------------------
# 4.5 DYNAMIC SCHEMATIC DIAGRAM
# -------------------------------------------------------------------------
st.markdown("###  Process Schematic")
st.markdown('<div style="margin-top: -20px;"></div>', unsafe_allow_html=True)

# Create a wide, short figure for the schematic
fig_schem, ax_schem = plt.subplots(figsize=(10, 1))
fig_schem.patch.set_alpha(0.0)

ax_schem.axis('off') # Hide the grid and axes
fig_schem.subplots_adjust(left=0, right=1, top=1, bottom=0)

ax_schem.set_xlim(0, 1)
ax_schem.set_ylim(0.9, 1.2)

# Style Dictionary for Text Boxes


try:
    # Read the specific image file
    img = mpimg.imread('Ranque-Hilsch-Tube.png')
    
    # Place it centrally on the canvas. 
    # extent=[left, right, bottom, top] stretches it to fit nicely between our text
    ax_schem.imshow(img, extent=[0.09, 0.99, 0.93, 1.23], zorder=1)
    
except FileNotFoundError:
    st.error("️ 'Ranque-Hilsch-Tube.png' not found! Make sure the image is saved in the same folder as this Python script.")
    

# --- INLET (Text) ---

ax_schem.text(0.4, 1.12, f"Inlet\nT: {T_in:.1f} K\nP: {P_in:.1f} kPa", 
              ha='center', va='bottom', fontsize=5, fontweight='bold', color='#08BD1D',zorder=2)

# --- HOT EXIT (Text) ---

ax_schem.text(1, 1.02, f"Hot exit\nT: {T_H:.1f} K\nf hot: {1-f:.2f}", 
              ha='left', va='center', fontsize=5, fontweight='bold', color='#F54831', zorder=2)

# --- COLD EXIT (Left Arrow) ---

ax_schem.text(0.08, 1.02, f"Cold exit\nT: {T_C:.2f} K\nf cold: {f:.2f}", 
              ha='right', va='center', fontsize=5, fontweight='bold', color='#31F5F5', zorder=2)


# Render the schematic in Streamlit
st.pyplot(fig_schem,dpi=500)
# -------------------------------------------------------------------------
# 5. VISUALIZATIONS (Matplotlib integration)
# -------------------------------------------------------------------------

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
st.markdown('<div style="margin-top: -50px;"></div>', unsafe_allow_html=True)

# Plot 1: Temperature
ax1.plot(f_array, TC_valid, 'b-', linewidth=2, label='Possible (s_gen >= 0)')
ax1.plot(f_array, TC_invalid, 'r--', linewidth=2, label='Impossible (s_gen < 0)')
ax1.plot(f, T_C, 'ko', markersize=8, markerfacecolor='yellow', label='Current Point')
ax1.set_xlabel('Cold Fraction (f)')
ax1.set_ylabel('Cold Outlet Temperature [K]')
ax1.set_title('First Law: Temperature Separation')
ax1.grid(True)
ax1.legend()

# Plot 2: Entropy
ax2.plot(f_array, s_gen_array, 'g-', linewidth=2)
ax2.plot(f, s_gen, 'ko', markersize=8, markerfacecolor='yellow')
ax2.axhline(y=0, color='k', linestyle='--', linewidth=1)
ax2.set_xlabel('Cold Fraction (f)')
ax2.set_ylabel('Entropy Generation [J/kg*K]')
ax2.set_title('Second Law Analysis')
ax2.grid(True)

plt.tight_layout()

# st.pyplot is how you tell Streamlit to draw the matplotlib figure on the web page
st.pyplot(fig)
