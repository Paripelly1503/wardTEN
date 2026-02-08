import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Ward 10 Voter Search", layout="wide")

# 2. Data Loading Function
@st.cache_data
def load_data():
    # Make sure this filename matches your Excel file exactly
    file_name = "voters_ward10.xlsx" 
    try:
        df = pd.read_excel(file_name)
        # Clean column names (remove hidden spaces)
        df.columns = df.columns.str.strip()
        # Standardize Gender labels for the charts
        df['Sex'] = df['Sex'].astype(str).str.strip().map({
            'M': 'Male', 'F': 'Female', 
            'Male': 'Male', 'Female': 'Female'
        }).fillna('Unknown')
        return df
    except Exception as e:
        st.error(f"Error: Could not find '{file_name}'. Please ensure it is in the same folder as this script.")
        st.stop()

df = load_data()

# --- SIDEBAR: OVERALL STATISTICS ---
st.sidebar.header("📊 Ward 10 Summary")
st.sidebar.metric("Total Registered Voters", len(df))

# Overall Gender Pie Chart
gen_total = df['Sex'].value_counts().reset_index()
gen_total.columns = ['Gender', 'Count']
fig_total = px.pie(
    gen_total, 
    values='Count', 
    names='Gender', 
    title="Ward-wide Gender Split",
    color='Gender',
    color_discrete_map={'Male': '#1f77b4', 'Female': '#e377c2'}
)
st.sidebar.plotly_chart(fig_total, use_container_width=True)

# --- MAIN AREA: SEARCH ENGINE ---
st.title("🗳️ Ward 10 Search Engine")
st.write("Search for individual voters using their Name, Door Number, or EPIC Number.")

# Search Input Box
search = st.text_input("🔍 Search Voter:", placeholder="Enter Name, Door No, or EPIC No...")

if search:
    # TARGETED SEARCH MASK
    # We only look in Name, Door_No, and EPIC columns. 
    # 'Relation' column is ignored so father/husband names don't trigger results.
    mask = (
        df['Name'].astype(str).str.contains(search, case=False, na=False) | 
        df['EPIC'].astype(str).str.contains(search, case=False, na=False) |
        df['Door_No'].astype(str).str.contains(search, case=False, na=False)
    )
    results = df[mask]

    if not results.empty:
        # Create two columns: Left for the table, Right for the chart
        col1, col2 = st.columns([2, 1])

        with col1:
            st.success(f"Found {len(results)} matches in Voter details.")
            st.dataframe(results, use_container_width=True)
            
            # Optional: Download Button for filtered results
            csv = results.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Search Results as CSV",
                data=csv,
                file_name=f"search_results_{search}.csv",
                mime="text/csv",
            )

        with col2:
            st.write("### 📈 Search Analytics")
            
            # Prepare data for the local chart (Fix for Line 57 error)
            local_gen = results['Sex'].value_counts().reset_index()
            local_gen.columns = ['Gender', 'Count'] # Explicitly name columns
            
            fig_local = px.pie(
                local_gen, 
                values='Count', 
                names='Gender', 
                title=f"Gender Split for search: '{search}'",
                hole=0.4,
                color='Gender',
                color_discrete_map={'Male': '#1f77b4', 'Female': '#e377c2'}
            )
            st.plotly_chart(fig_local, use_container_width=True)
    else:
        st.warning(f"No match found for '{search}' in Voter/EPIC/Door columns.")
        st.info("💡 Note: This search ignores Father/Husband names to improve accuracy.")
else:
    # Default view when no search is performed
    st.info("Enter details above to see specific charts.")
    st.write("### Preview of Records")
    st.dataframe(df.head(50), use_container_width=True)

