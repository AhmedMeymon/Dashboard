import streamlit as st
import pandas as pd
import numpy as np

from data import load_data, get_summary


st.set_page_config(page_title="BMW Analysis Dashboard", layout="wide")


def main():
    df = load_data("bmw.csv")

    # Sidebar filters
    st.sidebar.header("Filter listings")

    models = sorted(df["model"].unique())
    selected_models = st.sidebar.multiselect("Model", options=models, default=models[:6])

    year_min = int(df["year"].min())
    year_max = int(df["year"].max())
    selected_year = st.sidebar.slider("Year range", min_value=year_min, max_value=year_max, value=(year_min, year_max))

    price_min = int(df["price"].min())
    price_max = int(df["price"].max())
    selected_price = st.sidebar.slider("Price range", min_value=price_min, max_value=price_max, value=(price_min, price_max))

    transmissions = sorted(df["transmission"].dropna().unique())
    selected_trans = st.sidebar.multiselect("Transmission", options=transmissions, default=transmissions)

    fuels = sorted(df["fuelType"].dropna().unique())
    selected_fuel = st.sidebar.multiselect("Fuel type", options=fuels, default=fuels)

    # Apply filters
    mask = (
        df["model"].isin(selected_models)
        & df["year"].between(selected_year[0], selected_year[1])
        & df["price"].between(selected_price[0], selected_price[1])
        & df["transmission"].isin(selected_trans)
        & df["fuelType"].isin(selected_fuel)
    )

    filtered = df[mask].copy()

    # Header
    st.title("BMW Marketplace — Analysis Dashboard")
    st.markdown("Use the controls in the left panel to filter the listings. Charts and KPIs update automatically.")

    # KPIs
    summary = get_summary(filtered)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Listings", f"{summary['count']}")
    k2.metric("Median Price", f"£{summary['avg_price']:,.0f}")
    k3.metric("Median Mileage", f"{summary['median_mileage']:,.0f} mi")
    k4.metric("Median MPG", f"{summary['avg_mpg']:,.1f}")

    # Charts area
    c1, c2 = st.columns((2, 1))

    # Average price by year (line)
    if not filtered.empty:
        price_by_year = filtered.groupby("year")["price"].median().sort_index()
        price_by_year = price_by_year.rename("median_price").to_frame()
        c1.subheader("Median price by year")
        c1.line_chart(price_by_year)

        # Model counts
        model_counts = filtered["model"].value_counts().nlargest(15)
        c2.subheader("Top models (count)")
        c2.bar_chart(model_counts)

        # Price distribution (histogram)
        st.subheader("Price distribution")
        counts, bins = np.histogram(filtered["price"].dropna(), bins=20)
        bin_labels = [f"{int(bins[i])}-{int(bins[i+1])}" for i in range(len(bins)-1)]
        hist_df = pd.DataFrame({"count": counts}, index=bin_labels)
        st.bar_chart(hist_df)

        # Mileage vs price aggregated line (binned)
        st.subheader("Average price by mileage bucket")
        filtered["mileage_bucket"] = pd.cut(filtered["mileage"], bins=10)
        price_by_mileage = filtered.groupby("mileage_bucket")["price"].median().dropna()
        st.line_chart(price_by_mileage)

    else:
        st.info("No listings match the selected filters.")

    # Data table and download
    st.subheader("Filtered listings")
    st.dataframe(filtered.reset_index(drop=True))

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(label="Download CSV of filtered data", data=csv, file_name="bmw_filtered.csv", mime="text/csv")


if __name__ == "__main__":
    main()