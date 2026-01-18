import streamlit as st
import pandas as pd


@st.cache_data
def load_data(path: str = "bmw.csv") -> pd.DataFrame:
	"""Load and preprocess the BMW CSV file.

	- strips whitespace from string columns
	- converts numeric columns to appropriate dtypes
	- returns a clean DataFrame
	"""
	df = pd.read_csv(path)

	# Strip leading/trailing whitespace in string columns
	str_cols = df.select_dtypes(include=["object"]).columns
	for c in str_cols:
		df[c] = df[c].astype(str).str.strip()

	# Convert numeric columns
	for col in ["year", "price", "mileage", "tax"]:
		if col in df.columns:
			df[col] = pd.to_numeric(df[col], errors="coerce")

	# Ensure mpg and engineSize numeric
	for col in ["mpg", "engineSize"]:
		if col in df.columns:
			df[col] = pd.to_numeric(df[col], errors="coerce")

	return df


def get_summary(df: pd.DataFrame) -> dict:
	"""Return a small summary dictionary used by the dashboard."""
	return {
		"count": int(len(df)),
		"avg_price": float(df["price"].median()) if "price" in df.columns else None,
		"median_mileage": float(df["mileage"].median()) if "mileage" in df.columns else None,
		"avg_mpg": float(df["mpg"].median()) if "mpg" in df.columns else None,
	}
