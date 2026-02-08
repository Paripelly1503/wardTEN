import streamlit as st
import pandas as pd
import plotly.express as px

# Set page to wide mode
st.set_page_config(page_title="Voter Search Engine", layout="wide")


# 1. Load Data
@st.cache_data
def load_data():
    # Replace 'voters_data.xlsx' with your actual filename
    df = pd.read_excel("voters_data.xlsx")
    # Standardize Gender for charting
    df['Sex'] = df['Sex'].map({'M': 'Male', 'F': 'Female'}).fillna(df['Sex'])
    return df


df = load_data()

st.title("🗳️ Ward 10 Search Engine & Analytics")

# 2. Global Analytics Section (Sidebar)
st.sidebar.header("Global Ward Statistics")
if not df.empty:
    global_counts = df['Sex'].value_counts().reset_index()
    global_counts.columns = ['Gender', 'Count']

    fig_global = px.pie(
        global_counts,
        values='Count',
        names='Gender',
        title="Total Ward Gender Split",
        color='Gender',
        color_discrete_map={'Male': '#1f77b4', 'Female': '#e377c2'}
    )
    st.sidebar.plotly_chart(fig_global, use_container_width=True)
    st.sidebar.write(f"**Total Voters:** {len(df)}")

# 3. Search Interface
st.subheader("🔍 Search Voters")
search_query = st.text_input("Search by Name, Door No, or EPIC No:", placeholder="Type here...")

# 4. Search & Filter Logic
if search_query:
    # Search across all columns
    mask = df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
    filtered_df = df[mask]

    if not filtered_df.empty:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.write(f"Found {len(filtered_df)} results:")
            st.dataframe(filtered_df, use_container_width=True)

        with col2:
            # Local Pie Chart for the search results
            st.write("### Filtered Gender Split")
            local_counts = filtered_df['Sex'].value_counts().reset_index()
            local_counts.columns = ['Gender', 'Count']

            fig_local = px.pie(
                local_counts,
                values='Count',
                names='Gender',
                title=f"Gender for '{search_query}'",
                hole=0.4,  # Makes it a donut chart for style
                color='Gender',
                color_discrete_map={'Male': '#1f77b4', 'Female': '#e377c2'}
            )
            st.plotly_chart(fig_local, use_container_width=True)
    else:
        st.warning("No records found for that search.")
else:
    st.info("Enter a name or door number to see specific analytics.")
    st.write("### All Records Preview")
    st.dataframe(df.head(100), use_container_width=True)