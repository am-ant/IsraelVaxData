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


# --- Global Legend for the Bullet Charts ---
st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; gap: 25px; direction: rtl; margin-bottom: 20px; padding: 10px; background-color: #f9f9f9; border-radius: 10px;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 30px; height: 12px; background-color: #1f77b4; border-radius: 2px;"></div>
            <span style="font-size: 14px; font-weight: bold;">כיסוי ביישוב ({selected_town})</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 30px; height: 0px; border-top: 3px dashed Red;"></div>
            <span style="font-size: 14px; font-weight: bold;">ממוצע ארצי</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* 1. Reduce the gap between ALL elements in the main body */
    [data-testid="stVerticalBlock"] {
        gap: 0rem !important;
    }
    /* 2. Reduce padding around the main container */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    /* 3. Force Plotly charts to have zero bottom margin */
    iframe {
        margin-bottom: -40px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Loop through the vaccines in chunks
for i in range(0, len(items), charts_per_row):

    # Create the row of columns
    cols = st.columns(charts_per_row, gap=None)
    chunk = items[i : i + charts_per_row]
    
    for j, (index, row) in enumerate(chunk):
        vax_type_raw = row["Vaccine type"]
        vax_display_name = VAX_MAP.get(vax_type_raw, vax_type_raw)
        town_rate = int(round(row["Vaccine coverage"]))
        avg_rate = global_averages.get(vax_type_raw, 0)
        
        # USE THE SPECIFIC COLUMN [j]
        with cols[j]:
            fig = go.Figure()

            # 1. The Main Town Bar
            fig.add_trace(go.Bar(
                y=[vax_display_name],
                x=[town_rate],
                orientation='h',
                marker_color='#1f77b4',
                # Keep the percentage exactly as before
                text=f"{town_rate}%",
                textposition='outside', # Or 'inside' if you prefered that look
                cliponaxis=False,        # Ensures text doesn't get cut off
                width=0.6
            ))

            # 2. Add the Vaccine Name INSIDE the bar as an annotation
            fig.add_annotation(
                x=5,                   # Place it near the start (5% mark)
                y=0,
                text=vax_display_name, # The Hebrew Vaccine Name
                showarrow=False,
                font=dict(color="white", size=14),
                xanchor="left"         # Anchor to the left for RTL feel
            )

            # 3. The Average Line (Keep as is)
            fig.add_shape(
                type="line",
                x0=avg_rate, x1=avg_rate,
                y0=-0.4, y1=0.4,
                line=dict(color="Red", width=3, dash="dash")
            )

            fig.update_layout(
                height=110, # Can be even shorter now
                margin=dict(l=5, r=40, t=10, b=10), # Extra right margin for % text
                xaxis_range=[0, 115],
                showlegend=False,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True}, key=f"vax_{vax_type_raw}")
        
        
            
            
st.divider()
st.markdown('<div style="text-align: right; direction: rtl;"><h3>טבלת סיכום: כיסוי חיסוני לעומת ממוצע</h3></div>', unsafe_allow_html=True)

# 1. Prepare the data for the table
# We use the town_data we already filtered and sorted
summary_df = town_data[["Vaccine type", "Vaccine coverage"]].copy()

# 2. Add the average column by mapping the values
summary_df["ממוצע ארצי"] = summary_df["Vaccine type"].map(global_averages)

# 3. Calculate the difference (Gap)
summary_df["הפרש"] = summary_df["Vaccine coverage"] - summary_df["ממוצע ארצי"]

# 4. Clean up names for display
summary_df["חיסון"] = summary_df["Vaccine type"].map(lambda x: VAX_MAP.get(x, x))
summary_df = summary_df[["חיסון", "Vaccine coverage", "ממוצע ארצי", "הפרש"]]
summary_df.columns = ["סוג חהיסון", "כיסוי ביישוב", "ממוצע ארצי", "הפרש"]

# 5. Format the numbers to look like percentages
formatted_df = summary_df.style.format({
    "כיסוי ביישוב": "{:.0f}%",
    "ממוצע ארצי": "{:.0f}%",
    "הפרש": "{:+.0f}%" # Adds a + or - sign
})

# 6. Display the table
st.dataframe(formatted_df, hide_index=True, use_container_width=True)