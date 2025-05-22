from matplotlib import pyplot as plt
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scipy.stats as stats

# Load and clean data
df = pd.read_csv("data_airbnb.csv")
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["beds"] = pd.to_numeric(df["beds"], errors="coerce")
df = df.dropna(subset=["latitude", "longitude", "price", "beds"])

st.sidebar.markdown("## 🎛️ Filters")

# Price slider with fixed max 500, step 10, default 50-300
price_range = st.sidebar.slider("💵 Price Range (USD)", 0, 500, (50, 300), step=10)

beds_range = st.sidebar.slider("🛏️ Number of Beds", 1, 8, (1, 4), step=1)

# Filter the DataFrame based on the selected price and beds ranges
filtered_df = df[
    (df["price"] >= price_range[0])
    & (df["price"] <= price_range[1])
    & (df["beds"] >= beds_range[0])
    & (df["beds"] <= beds_range[1])
]

# Title
st.title("🏡 Airbnb NYC Accommodation Dashboard")
st.markdown("Explore accommodation data from Airbnb across NYC neighborhoods.")

st.subheader("🗺️ Accommodation Map")
map_fig = px.scatter_mapbox(
    filtered_df,
    lat="latitude",
    lon="longitude",
    color="price",
    size="price",
    hover_name="name",
    hover_data={
        "price": True,
        "beds": True,
        "room_type": True,
        "neighbourhood": True,
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
# Two-column layout
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("📊 Number of Listings by Borough")
    listings_count = (
        filtered_df.groupby("neighbourhood_group")["name"].count().reset_index()
    )
    listings_count.rename(columns={"name": "count"}, inplace=True)
    bar_fig = px.bar(
        listings_count,
        x="count",
        y="neighbourhood_group",
        orientation="h",
        title="🏷️ Number of Listings per Borough",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    st.plotly_chart(bar_fig, use_container_width=True)

with col2:
    st.subheader("🏆 Top 10 Most Expensive Listings")

    top10 = filtered_df.sort_values(by="price", ascending=False).head(10)

    expensive_fig = px.bar(
        top10,
        x="price",
        y="name",
        orientation="h",
        color="neighbourhood_group",
        title="💸 Top 10 Most Expensive Accommodations",
        color_discrete_sequence=px.colors.qualitative.Set1,
    )
    st.plotly_chart(expensive_fig, use_container_width=True)

st.subheader("📊 Avg Price by Number of Beds and Room Type")
st.markdown("Compare average prices across different numbers of beds and room types.")
avg_price_beds_room = (
    filtered_df.groupby(["beds", "room_type"])["price"].mean().reset_index()
)
grouped_bar_chart = px.bar(
    avg_price_beds_room,
    x="beds",
    y="price",
    color="room_type",
    barmode="group",
    title="💰 Average Price by Number of Beds and Room Type",
    labels={"beds": "Number of Beds", "price": "Average Price (USD)"},
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
st.plotly_chart(grouped_bar_chart)

st.subheader("⭐ Reviews vs Popularity Indicator")

st.markdown(
    "Explore how the number of reviews relates to how often listings are reviewed monthly."
)

# Scatter plot
fig = px.scatter(
    filtered_df,
    x="number_of_reviews",
    y="reviews_per_month",
    size="availability_365",
    color="room_type",
    hover_data=["name", "price"],
    title="📈 Number of Reviews vs Reviews Per Month",
    labels={
        "number_of_reviews": "Total Reviews",
        "reviews_per_month": "Reviews Per Month",
    },
    color_discrete_sequence=px.colors.qualitative.Safe,
)
st.plotly_chart(fig, use_container_width=True)

# Correlation coefficient
corr_val = filtered_df["number_of_reviews"].corr(filtered_df["reviews_per_month"])
st.markdown(
    f"📌 **Correlation coefficient (r)** between total reviews and reviews/month: `{corr_val:.2f}`"
)

st.subheader("📉 Distribution of Accommodation Prices")

fig_hist = px.histogram(
    filtered_df,
    x="price",
    nbins=40,
    title="💵 Price Distribution (Filtered Listings)",
    color_discrete_sequence=["#636EFA"],
    marginal="box",  # Adds boxplot for outlier detection
    labels={"price": "Price (USD)"},
)
st.plotly_chart(fig_hist, use_container_width=True)

with st.expander("📋 View Filtered Data Table"):
    st.dataframe(
        filtered_df[
            [
                "name",
                "neighbourhood",
                "room_type",
                "price",
                "beds",
                "latitude",
                "longitude",
            ]
        ]
    )
    st.markdown(
        "This table shows the filtered data based on your selections. You can scroll to see all columns."
    )
