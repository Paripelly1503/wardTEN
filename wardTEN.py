import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Ward 10 Search Engine", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        # Assumes voters_data.xlsx is in the SAME GitHub folder as this script
        df = pd.read_excel("voters_word10.xlsx")
        # Cleaning column names (removes hidden spaces)
        df.columns = df.columns.str.strip()
        # Mapping gender for the chart
        if 'Sex' in df.columns:
            df['Sex'] = df['Sex'].replace({'M': 'Male', 'F': 'Female'})
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return pd.DataFrame()

df = load_data()

# --- INTERFACE ---
st.title("🗳️ Ward 10 Search & Analytics")

if df.empty:
    st.warning("Please ensure 'voters_ward10.xlsx' is uploaded to your GitHub repository.")
else:
    # Sidebar Global Stats
    st.sidebar.header("Global Stats")
    total_voters = len(df)
    st.sidebar.metric("Total Voters", total_voters)
    
    # Global Pie Chart
    gen_counts = df['Sex'].value_counts().reset_index()
    fig_gen = px.pie(gen_counts, values='count', names='Sex', 
                     title="Overall Gender Split", color='Sex',
                     color_discrete_map={'Male':'#1f77b4', 'Female':'#e377c2'})
    st.sidebar.plotly_chart(fig_gen)

    # --- SEARCH ENGINE ---
    search = st.text_input("Enter Name, Door No, or EPIC No to search:")

    # --- INSERT THIS NEW BLOCK ---
if search:
    # This checks only the Name, EPIC, and Door No columns. 
    # It will NOT search the Relation Name column unless you add it here.
    mask = (
        df['Name'].str.contains(search, case=False, na=False) | 
        df['EPIC'].str.contains(search, case=False, na=False) |
        df['Door No.'].str.contains(search, case=False, na=False)
    )
    results = df[mask]
        
        if not results.empty:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.success(f"Found {len(results)} matches")
                st.dataframe(results, use_container_width=True)
                
            with col2:
                # Dynamic Pie Chart for the Search Result
                st.subheader("Search Analytics")
                search_gen = results['Sex'].value_counts().reset_index()
                fig_search = px.pie(search_gen, values='count', names='Sex', 
                                   title=f"Gender % for '{search}'",
                                   color='Sex',
                                   color_discrete_map={'Male':'#1f77b4', 'Female':'#e377c2'})
                st.plotly_chart(fig_search, use_container_width=True)
        else:
            st.error("No records found.")
    else:
        st.info("👆 Enter a search term above to see specific charts.")


