"""Streamlit dashboard over the gold DuckDB marts.

Run: streamlit run serving/dashboard.py
"""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import streamlit as st

DB_PATH = os.environ.get(
    "DOCSTREAM_DUCKDB", str(Path(__file__).resolve().parents[1] / "data/gold/docstream.duckdb")
)

st.set_page_config(page_title="DocStream — Spend Analytics", layout="wide")
st.title("DocStream — Document Spend Analytics")
st.caption("Gold-layer marts built by dbt from OCR-extracted documents · Sam Kalaliya")

if not Path(DB_PATH).exists():
    st.warning("No gold database found. Run the pipeline and `dbt build` first.")
    st.stop()

con = duckdb.connect(DB_PATH, read_only=True)

monthly = con.execute("select * from fct_monthly_spend order by spend_month").pl()
vendors = con.execute("select * from dim_vendors order by lifetime_spend desc").pl()

total_spend = float(monthly["total_spend"].sum()) if monthly.height else 0.0
invoice_count = int(monthly["invoice_count"].sum()) if monthly.height else 0

c1, c2, c3 = st.columns(3)
c1.metric("Total spend", f"${total_spend:,.2f}")
c2.metric("Invoices processed", f"{invoice_count:,}")
c3.metric("Vendors", f"{vendors.height:,}")

st.subheader("Monthly spend")
if monthly.height:
    st.bar_chart(monthly.to_pandas(), x="spend_month", y="total_spend")

st.subheader("Top vendors")
st.dataframe(vendors.to_pandas(), use_container_width=True)
