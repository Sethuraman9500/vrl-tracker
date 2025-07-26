import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="VRL Consignment Tracker", layout="wide")

def track_vrl(lrno):
    url = f"https://www.vrlgroup.in/track_consignment.aspx?lrnos={lrno}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        result_div = soup.find("div", {"id": "divlrdata"})
        if result_div:
            return result_div.get_text(strip=True)
        else:
            return "Tracking info not found"
    except Exception as e:
        return f"Error: {e}"

st.title("📦 VRL Consignment Tracker")

uploaded_file = st.file_uploader("Upload LRNO CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if "LRNO" not in df.columns:
        st.error("CSV must contain a column named 'LRNO'")
    else:
        with st.spinner("Tracking..."):
            df["Status"] = df["LRNO"].astype(str).apply(track_vrl)
        st.success("Tracking complete!")
        st.dataframe(df)
        st.download_button("Download Results", df.to_csv(index=False), "results.csv", "text/csv")
else:
    st.info("Please upload a CSV file with LRNO column.")
