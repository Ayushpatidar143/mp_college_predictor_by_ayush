import pandas as pd
import streamlit as st
st.set_page_config(
    page_title="Ayush MP Engineering College Predictor",
    page_icon="🎓",
    layout="wide"
)

st.set_page_config(
    page_title="MP Engineering College Predictor 2026", layout="wide"
)
st.markdown("""
    <style>
    /* Global App Theme - Deep Dark with Vibrant Pink Vibe */
    .stApp {
        background: #09060b;
        color: #fce7f3;
        font-family: 'Inter', sans-serif;
    }
    
    /* Modern Sleek Sidebar */
    [data-testid="stSidebar"] {
        background-color: #120914;
        border-right: 1px solid rgba(236, 72, 153, 0.15);
    }
    
    /* Sidebar Headings & Labels */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #fbcfe8 !important;
        font-weight: 600 !important;
    }

    /* Input Fields - Dark Box with Pink Focus Glow */
    [data-testid="stSidebar"] .stTextInput input, 
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1a0f1e !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #4a1d5e !important;
    }
    [data-testid="stSidebar"] .stTextInput input:focus, 
    [data-testid="stSidebar"] .stNumberInput input:focus {
        border-color: #ec4899 !important;
        box-shadow: 0 0 12px rgba(236, 72, 153, 0.4);
    }

    /* Main Area Headers with Pink Gradient */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    /* Premium Neon Pink Gradient Action Button */
    .stButton>button {
        background: linear-gradient(135deg, #ec4899 0%, #be185d 100%);
        color: white;
        border-radius: 10px;
        padding: 0.6rem 1.4rem;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 20px rgba(236, 72, 153, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #db2777 0%, #9d174d 100%);
        box-shadow: 0 6px 25px rgba(236, 72, 153, 0.7);
        transform: translateY(-1px);
        color: white;
    }

    /* Glassmorphic Tables & Cards */
    [data-testid="stDataFrame"] {
        background-color: #120914;
        border-radius: 12px;
        border: 1px solid rgba(236, 72, 153, 0.2);
        padding: 5px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("<h1>🎓 Ayush MP Engineering College Predictor</h1>", unsafe_allow_html=True)
st.write(
    "Find eligible colleges and branches based on your JEE rank, category, and"
    " preferred branch!"
)


# Load the extracted CSV data
@st.cache_data
def load_data():
  try:
    df = pd.read_csv("mp_cutoff.csv", header=None, on_bad_lines="skip")
    return df
  except Exception as e:
    return None


df = load_data()

if df is not None:
  # Clean columns and set proper headers based on PDF structure
  col_names = [
      "S.No",
      "Institute Name",
      "Inst Type",
      "FW",
      "Branch",
      "Choice Code",
      "Opening Rank",
      "Closing Rank",
      "Category",
  ]
  if len(df.columns) >= len(col_names):
    df = df.iloc[:, : len(col_names)]
    df.columns = col_names
  else:
    df.columns = [f"Col_{i}" for i in range(len(df.columns))]

  # --- CLEANING JUNG/HEADER ROWS ---
  df = df[df["Category"].notna() & df["Branch"].notna()]
  # Remove header leaks and garbage text
  df = df[~df["Category"].astype(str).str.contains("YROGETAC|Category|S.No", case=False, na=False)]
  df = df[~df["Branch"].astype(str).str.contains("Branch|Course|S.No|Institute", case=False, na=False)]
  
  # Remove rows where branch name is too short or just junk characters
  df = df[df["Branch"].astype(str).str.len() > 3]

  # Clean Closing Ranks (Remove commas and convert to numeric)
  df["Closing Rank Numeric"] = pd.to_numeric(
      df["Closing Rank"].astype(str).str.replace(",", ""), errors="coerce"
  )

  # --- SIDEBAR FOR PREDICTOR INPUTS & BRANCH FILTER ---
  st.sidebar.header("🎯 Enter Your Details")

  user_rank = st.sidebar.number_input(
      "Enter Your JEE Main Rank", min_value=1, max_value=2000000, value=50000
  )

  # Category selection (clean unique categories)
  categories = df["Category"].dropna().unique().tolist() if "Category" in df.columns else []
  selected_category = st.sidebar.selectbox("Select Your Category", categories)

  st.sidebar.markdown("---")
  st.sidebar.subheader("🔍 Branch Filter")

  # Branch selection dropdown (sorted clean branches)
  branches = df["Branch"].dropna().unique().tolist() if "Branch" in df.columns else []
  selected_branch = st.sidebar.selectbox(
      "Select Branch", ["All Branches"] + sorted(branches)
  )

  predict_btn = st.sidebar.button("Predict Colleges 🚀")

  # --- MAIN CONTENT AREA ---
  if predict_btn:
    st.subheader(
        f"🎯 Matching Colleges for Rank ({user_rank}), Category"
        f" ({selected_category})"
    )

    # Filter: Category match and Closing Rank >= User Rank
    result_df = df[
        (df["Category"] == selected_category)
        & (df["Closing Rank Numeric"] >= user_rank)
    ]

    # Apply Branch filter if a specific branch is selected
    if selected_branch != "All Branches":
      result_df = result_df[result_df["Branch"] == selected_branch]

    # Sort by closing rank so closest matching ranks appear first
    result_df = result_df.sort_values(
        by="Closing Rank Numeric", ascending=True
    )

    if not result_df.empty:
      st.success(
          f"Found {len(result_df)} matching options available for your criteria!"
      )
      display_cols = [
          "Institute Name",
          "Inst Type",
          "FW",
          "Branch",
          "Opening Rank",
          "Closing Rank",
      ]
      st.dataframe(result_df[display_cols], use_container_width=True)
    else:
      st.warning(
          "No matching colleges found for this combination. Try selecting 'All"
          " Branches' or checking another rank."
      )
  else:
    st.info(
        "👈 Enter your Rank, Category, and choose a branch in the sidebar, then"
        " click **'Predict Colleges'**!"
    )

    # General raw data explorer below
    with st.expander("🔍 Or browse through all raw cutoff data records"):
      search_query = st.text_input("Search college or branch:")
      if search_query:
        mask = df.astype(str).apply(
            lambda x: x.str.contains(search_query, case=False, na=False)
        ).any(axis=1)
        st.dataframe(df[mask], use_container_width=True)

else:
  st.error(
      "Error: 'mp_cutoff.csv' file not found. Please run the extraction script"
      " first."
  )