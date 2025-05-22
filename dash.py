import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Set Streamlit page config
st.set_page_config(page_title="New York Airbnb Dashboard 🏡", layout="wide")

# Load data
df = pd.read_csv("data_airbnb.csv")

# Sidebar filters
st.sidebar.header("🔍 Filter Listings")

# Valid filters
room_types = (
    df["room_type"].dropna().unique().tolist() if "room_type" in df.columns else []
)
min_price = int(df["price"].min()) if "price" in df.columns else 0
max_price = int(df["price"].max()) if "price" in df.columns else 1000
neighbourhood_groups = (
    df["neighbourhood_group"].dropna().unique().tolist()
    if "neighbourhood_group" in df.columns
    else []
)

# Custom CSS for purple gradient sidebar
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #232526 35%, #414345 65%);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

selected_neighbourhood_group = st.sidebar.multiselect(
    "🏘️ Select Neighbourhood Group",
    neighbourhood_groups,
    default=neighbourhood_groups[:1],
)
selected_room_type = st.sidebar.multiselect(
    "🛏️ Select Room Type", room_types, default=room_types[:1]
)
selected_price = st.sidebar.slider(
    "💵 Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
)

# Filter dataset
if "room_type" in df.columns:
    df = df[df["room_type"].isin(selected_room_type)]
if "price" in df.columns:
    df = df[(df["price"] >= selected_price[0]) & (df["price"] <= selected_price[1])]
if "neighbourhood_group" in df.columns:
    df = df[df["neighbourhood_group"].isin(selected_neighbourhood_group)]

st.markdown(
    """
    <h1 style='text-align: center; color: #FF5A5F; font-weight:700;'>New York Airbnb Dashboard</h1>
    <p style='text-align: center; font-size: 18px; color: #333;'>
        Gain insights into the New York Airbnb market with interactive analytics and visualizations.
    </p>
    """,
    unsafe_allow_html=True,
)

# KPIs
st.markdown("### 📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("🔢 Total Listings", len(df))
col2.metric(
    "💰 Average Price", f"${df['price'].mean():.2f}" if "price" in df.columns else "N/A"
)
col3.metric(
    "⭐ Average Rating",
    f"{pd.to_numeric(df['rating'], errors='coerce').mean():.2f}"
    if "rating" in df.columns
    else "N/A",
)

# Price Distribution
if "price" in df.columns:
    st.markdown("### 💵 Price Distribution")
    fig_price = px.histogram(
        df,
        x="price",
        nbins=50,
        title="Distribution of Listing Prices",
        color_discrete_sequence=["#FF5A5F"],
    )
    st.plotly_chart(fig_price, use_container_width=True)

# Listings by Room Type
if "room_type" in df.columns:
    st.markdown("### 🛏️ Listings by Room Type")
    room_counts = df["room_type"].value_counts()
    fig_room = px.pie(
        values=room_counts.values,
        names=room_counts.index,
        title="Room Type Proportion",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    st.plotly_chart(fig_room)

# Top 10 Hosts (if available)
if "host_name" in df.columns:
    st.markdown("### 👤 Top 10 Hosts by Number of Listings")
    top_hosts = df["host_name"].value_counts().head(10).reset_index()
    top_hosts.columns = ["host_name", "num_listings"]
    fig_hosts = px.bar(
        top_hosts,
        x="host_name",
        y="num_listings",
        labels={"host_name": "Host Name", "num_listings": "Number of Listings"},
        title="Top 10 Hosts",
        color_discrete_sequence=["#00A699"],
    )
    st.plotly_chart(fig_hosts)

# Average Ratings per Room Type (alternative to cities)
if "room_type" in df.columns and "rating" in df.columns:
    st.markdown("### ⭐ Average Ratings by Room Type")

    # Convert rating to numeric first
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    avg_rating = (
        df.groupby("room_type")["rating"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    avg_rating.columns = ["room_type", "avg_rating"]
    avg_rating = avg_rating[avg_rating["avg_rating"].notnull()]  # Remove NaN ratings
    avg_rating = avg_rating.sort_values(by="avg_rating", ascending=False).reset_index(
        drop=True
    )
    avg_rating.columns = ["room_type", "avg_rating"]
    fig_rating = px.bar(
        avg_rating,
        x="room_type",
        y="avg_rating",
        labels={"room_type": "Room Type", "avg_rating": "Average Rating"},
        title="Average Rating per Room Type",
        color_discrete_sequence=["#007A87"],
    )
    st.plotly_chart(fig_rating)

# Map visualization
if "latitude" in df.columns and "longitude" in df.columns:
    st.markdown("### 🗺️ Map of Listings")
    if not df[["latitude", "longitude"]].dropna().empty:
        map_fig = px.scatter_map(
            df.dropna(subset=["latitude", "longitude"]),
            lat="latitude",
            lon="longitude",
            color="price" if "price" in df.columns else None,
            size="price" if "price" in df.columns else None,
            hover_name="name" if "name" in df.columns else None,
            hover_data={
                "price": True if "price" in df.columns else False,
                "beds": True if "beds" in df.columns else False,
                "room_type": True if "room_type" in df.columns else False,
                "neighbourhood": True if "neighbourhood" in df.columns else False,
            },
            color_continuous_scale=px.colors.sequential.Viridis,
            size_max=10,
            zoom=10,
            height=500,
        )
        map_fig.update_layout(
            mapbox_style="carto-positron", margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )
        st.plotly_chart(map_fig, use_container_width=True)
    else:
        st.info("No map data available for the selected filters.")
