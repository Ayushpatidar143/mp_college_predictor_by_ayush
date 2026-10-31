import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="MP Engineering College Predictor 2026", layout="wide"
)
st.markdown("""
    <style>
    /* Global App Theme - Deep Dark SaaS Dashboard Vibe */
    .stApp {
        background-color: #030712;
        color: #f3f4f6;
    }
    
    /* Modern Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid #1f2937;
    }
    
    /* Sidebar Text & Label Visibility Fix */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #f9fafb !important;
        font-weight: 600 !important;
    }

    /* Input Fields Modern Box Style */
    [data-testid="stSidebar"] .stTextInput input, 
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #111827 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #374151 !important;
    }

    /* Main Content Headers */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    /* SaaS Style Glowing Primary Button */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 25px rgba(37, 99, 235, 0.6);
        border-color: rgba(255, 255, 255, 0.2);
        color: white;
    }

    /* Glassmorphism Cards for Metrics / Tables */
    [data-testid="stDataFrame"], div.stMetric {
        background-color: #0b0f19;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    </style>
""", unsafe_allow_html=True)
st.title("🎓 MP Engineering College Predictor 2026")
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