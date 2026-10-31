import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="MP Engineering College Predictor 2026", layout="wide"
)
st.markdown("""
    <style>
    /* Global App Styling - Clean White & Dark Modern Combo */
    .stApp {
        background-color: #f8fafc;
        color: #1e293b;
    }
    
    /* Modern Dark Sidebar (Black/Dark Slate with Blue accents) */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] label {
        color: #f8fafc !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] .stTextInput input, [data-testid="stSidebar"] .stNumberInput input {
        background-color: #1e293b;
        color: white;
        border-radius: 6px;
        border: 1px solid #334155;
    }

    /* Stunning Blue Primary Button with Shadow */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 700;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
        color: white;
    }

    /* Professional Headers */
    h1, h2, h3 {
        color: #0f172a;
        font-weight: 800;
    }

    /* Clean Dataframe / Table styling */
    dataframe {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
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