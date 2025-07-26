import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="VRL Consignment Tracker", layout="wide")

st.title("📦 VRL Consignment Tracker")

uploaded_file = st.file_uploader("Upload LRNO CSV", type="csv")

@st.cache_data(show_spinner=False)
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
        return f"Error: {str(e)}"

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        if "LRNO" not in df.columns:
            st.error("CSV must have a column named 'LRNO'")
        else:
            lrnos = df["LRNO"].astype(str).tolist()

            st.info(f"Tracking {len(lrnos)} consignments... Please wait ⏳")

            # Show progress bar
            status_data = []
            progress = st.progress(0)
            for idx, lrno in enumerate(lrnos):
                status = track_vrl(lrno)
                status_data.append({"LRNO": lrno, "Status": status})
                progress.progress((idx + 1) / len(lrnos))

            st.success("✅ Tracking complete!")
            result_df = pd.DataFrame(status_data)
            st.dataframe(result_df, use_container_width=True)

            csv_download = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Results", data=csv_download, file_name="vrl_tracking_results.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
else:
    st.warning("👆 Please upload a CSV file with a column named 'LRNO'")
