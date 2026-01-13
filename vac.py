import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- THE ENCODING DICTIONARY ---
VAX_MAP = {
    "אבעבועות רוח-VAR" : "VAR",
    "דלקת כבד A-HAV" : "HEP-A",
    "דלקת כבד B-HBV" : "HEP-B",
    "ה. אינפלואנזה b-Hib" : "Hib",
    "חצבת-חזרת-אדמת-MMR" : "MMR",
    "נגיף רוטה-Rota" : "Rota",
    "פלצת–אסכרה-שעלת-Tdap" : "DTaP",
    "פנוימוקוק-PCV" : "PCV",
    "שיתוק ילדים (IPV)-IPV" : "IPV",
    "שיתוק ילדים (OPV)-OPV" : "OPV",
}

# --- MANUAL AVERAGES ---
MANUAL_AVERAGES = {
    "אבעבועות רוח-VAR" : 79,
    "דלקת כבד A-HAV" : 50.8,
    "דלקת כבד B-HBV" : 91.2,
    "ה. אינפלואנזה b-Hib" : 91.9,
    "חצבת-חזרת-אדמת-MMR" : 80.4,
    "נגיף רוטה-Rota" : 87,
    "פלצת–אסכרה-שעלת-Tdap" : 91.9,
    "פנוימוקוק-PCV" : 87,
    "שיתוק ילדים (IPV)-IPV" : 92,
    "שיתוק ילדים (OPV)-OPV" : 62.3,
}
MANUAL_AVERAGES = {k: int(round(v)) for k, v in MANUAL_AVERAGES.items()}

CUSTOM_VAX_ORDER = [
    "חצבת-חזרת-אדמת-MMR",
    "פלצת–אסכרה-שעלת-Tdap",
    "דלקת כבד B-HBV",
    "פנוימוקוק-PCV",
    "אבעבועות רוח-VAR",
    "ה. אינפלואנזה b-Hib",
    "דלקת כבד A-HAV",
    "נגיף רוטה-Rota",
    "שיתוק ילדים (IPV)-IPV",
    "שיתוק ילדים (OPV)-OPV",
]

# 1. Load Data
@st.cache_data 
def load_data():
    df = pd.read_csv("vdata.csv", encoding='utf-8-sig')

    vax_col = "Vaccine coverage" 
    type_col = "Vaccine type"    
    
    df[vax_col] = df[vax_col].astype(str)
    df[vax_col] = df[vax_col].str.replace('%', '', regex=False)
    df[vax_col] = df[vax_col].str.replace(',', '.', regex=False) 
    df[vax_col] = df[vax_col].str.strip()
    df[vax_col] = pd.to_numeric(df[vax_col], errors='coerce')
    df = df.dropna(subset=[vax_col])
    
    #averages = df.groupby("Vaccine type")["Vaccine coverage"].mean().round(0).astype(int).to_dict()
    return df, MANUAL_AVERAGES

df, global_averages = load_data()

# 2. Sidebar/UI
#st.title("💉 נתוני התחסנות לפי ערים ")
st.markdown("""
    <style>
    /* Aggressively target Titles (h1) and Subheaders (h3) */
    [data-testid="stHeaderBlockContainer"] h1, 
    [data-testid="stVerticalBlock"] h1,
    [data-testid="stHeaderBlockContainer"] h3, 
    [data-testid="stVerticalBlock"] h3,
    .stMarkdown h1, 
    .stMarkdown h3 {
        text-align: right !important;
        direction: rtl !important;
        width: 100% !important;
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Now you can keep your original clean code:
st.title("💉 נתוני התחסנות לפי ערים ")

all_towns = sorted(df["Town"].unique())
# Find the index of Tel Aviv
# We use a try/except block just in case 'תל אביב' is spelled differently in your file
try:
    default_index = all_towns.index("תל אביב - יפו")
except ValueError:
    default_index = 0  # Fallback to the first town if not found

# 3. Pass the index to the selectbox
#st.markdown("בחר יישוב:")
st.markdown('<div style="text-align: right; direction: rtl;">בחר יישוב:</div>', unsafe_allow_html=True)
# label_visibility="collapsed" hides the default LTR label.
selected_town = st.selectbox(
    "", # Empty label
    all_towns, 
    index=default_index,
    label_visibility="collapsed" 
)


# 3. Logic: Filter data for the selected town
town_data = df[df["Town"] == selected_town].copy()

# Apply the custom sort order
town_data["Vaccine type"] = pd.Categorical(
    town_data["Vaccine type"], 
    categories=CUSTOM_VAX_ORDER, 
    ordered=True
)
town_data = town_data.sort_values("Vaccine type")

# --- 4. Display Results in a Clean Grid ---
st.subheader(f"נתונים עבור {selected_town}")

# Define how many charts per row (5 is usually the limit for readability)
charts_per_row = 1
items = list(town_data.iterrows())

# Loop through the vaccines in chunks
for i in range(0, len(items), charts_per_row):

    # Create a new row of columns
    cols = st.columns(charts_per_row)
    chunk = items[i : i + charts_per_row]
    
    for j, (_, row) in enumerate(chunk):
        vax_type_raw = row["Vaccine type"]
        vax_display_name = VAX_MAP.get(vax_type_raw, vax_type_raw)
        town_rate = int(round(row["Vaccine coverage"]))
        avg_rate = global_averages.get(vax_type_raw, 0)
            
        with cols[j]:
            # Metric header
            st.markdown(f'<div style="text-align: right; direction: rtl;"><b>{vax_display_name}</b></div>', unsafe_allow_html=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=['ממוצע', 'יישוב'], # The categories go on Y
                x=[avg_rate, town_rate], # The values go on X
                orientation='h',         # Horizontal orientation
                marker_color=['#d3d3d3', '#1f77b4'], 
                width=0.6,
                text=[f"{avg_rate}%", f"{town_rate}%"], 
                textposition='inside',   # Puts the % inside the bar to save space
                insidetextanchor='end'   # Aligns the text to the end of the bar
            ))

            fig.update_layout(
                height=140, # Much shorter height needed for horizontal bars
                margin=dict(l=10, r=40, t=10, b=10), # Space on the right for labels
                xaxis_range=[0, 115],
                showlegend=False,
                xaxis=dict(visible=False), # Hide the bottom axis
                yaxis=dict(
                    visible=True, 
                    tickfont=dict(size=12),
                    autorange="reversed" # Keeps 'יישוב' on top if desired
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True}, key=f"vax_{vax_type_raw}")