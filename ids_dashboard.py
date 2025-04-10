import streamlit as st
import pandas as pd
import os
import time
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import datetime

# ------------------- CONFIG -------------------
st.set_page_config(page_title="🛡️ Intrusion Detection System", layout="wide", page_icon="🛜")


LOG_FILE = "prediction_log.txt"
BLOCKED_FILE = "blocked_log.txt"
UNBLOCKED_FILE = "unblocked_log.txt"

# ------------------- STYLE -------------------
# ------------------- STYLE -------------------
with open("style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ✨ Inject glowing + bigger sidebar radio buttons directly via Python
st.markdown("""
<style>
/* 🔱 Make sidebar radio options bold, big, and bright */
section[data-testid="stSidebar"] .stRadio > div {
    font-size: 18px !important;
    font-weight: bold !important;
    color: #ffffff !important;
    padding: 6px 0;
    transition: all 0.3s ease-in-out;
}

/* 🌈 Add glow on hover for each radio option */
section[data-testid="stSidebar"] .stRadio > div:hover {
    text-shadow: 0 0 8px #00f0ff;
    color: #00f0ff !important;
}
</style>
""", unsafe_allow_html=True)




# ------------------- HEADER -------------------
st.markdown("""
<div style='
    background: linear-gradient(90deg, #1c1f26, #2a2f3a);
    padding: 24px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 0 12px rgba(0, 188, 212, 0.4);
'>
    <h1 style='color:#e0f7fa; font-size: 32px; text-shadow: 0 0 4px rgba(0, 188, 212, 0.3);'>
        🛡️ Intrusion Detection System
    </h1>
    <p style='color: #b0bec5; font-size: 16px; margin-top: 5px;'>
        Monitoring, Detecting, and Neutralizing Threats in Real-Time
    </p>
</div>
""", unsafe_allow_html=True)


# ------------------- FUNCTIONS -------------------
def load_logs(filepath, limit=300):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()[-limit:]
    return []

def parse_logs(lines):
    data = []
    for line in lines:
        parts = line.strip().split("|")
        if len(parts) >= 3:
            data.append({
                "Time": parts[0].strip(),
                "Session": parts[1].strip(),
                "Prediction": parts[2].strip().split(":")[-1].strip()
            })
    return pd.DataFrame(data)

raw_logs = load_logs(LOG_FILE)
df = parse_logs(raw_logs)

# ------------------- SIDEBAR -------------------
st.sidebar.title(" 🛡️ IDS CONTROL CENTER")
page = st.sidebar.radio("Navigate", ["🌐 Overview", "📄 Logs", "🎯 Utilities", "🛡️ Actions"])
refresh_rate = st.sidebar.selectbox("🔁 Auto-Refresh", [5, 10, 30, 60], index=1)

# 🔥 Intrusion Heatmap


# ------------------- PAGE: OVERVIEW -------------------
if page == "🌐 Overview":
    st.title("🛡️ Intrusion Detection System - Realtime Defense Center")
    st.caption("👑 Professional AI-Powered Threat Response")

    if not df.empty:
        last = df.iloc[-1]
        total_logs = len(df)
        intrusions = df[df["Prediction"].str.lower() != "normal"]
        total_intrusions = len(intrusions)
        blocked_ips = len(load_logs(BLOCKED_FILE))
        unblocked_ips = len(load_logs(UNBLOCKED_FILE))

        col1, col2, col3, col4 = st.columns(4)

        col1.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_logs,
            title={'text': "🛰️ Total Logs"},
            gauge={'axis': {'range': [None, 500]}}
        )), use_container_width=True)

        col2.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_intrusions,
            title={'text': "⚠️ Intrusions"},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "blue"}}
        )), use_container_width=True)

        col3.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=blocked_ips,
            title={'text': "🔒 Blocked IPs"},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "lightblue"}}
        )), use_container_width=True)

        col4.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=unblocked_ips,
            title={'text': "🔓 Unblocked IPs"},
            gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "teal"}}
        )), use_container_width=True)

        st.markdown("### 📊 Attack Distribution")
        pred_counts = df["Prediction"].value_counts().reset_index()
        pred_counts.columns = ["Prediction", "Count"]
        fig = px.pie(pred_counts, names="Prediction", values="Count", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🧾 Latest Logs")
        st.dataframe(df[::-1], use_container_width=True)

        st.markdown("""
        <marquee behavior="scroll" direction="left" style="color:#00c6ff; font-weight:bold; font-size:16px;">
            📰 LIVE TICKER: """ + " | ".join([f"{row['Time']} 🚨 {row['Session']} → {row['Prediction']}" for _, row in intrusions[::-1].head(5).iterrows()]) + """
        </marquee>
        """, unsafe_allow_html=True)

        time.sleep(refresh_rate)
        st.rerun()

# ------------------- PAGE: LOGS -------------------
elif page == "📄 Logs":
    st.title("📂 All Logs")
    tabs = st.tabs(["📋 Predictions", "🚫 Blocked", "✅ Unblocked"])
    with tabs[0]:
        st.code("".join(raw_logs), language="text")
    with tabs[1]:
        st.code("".join(load_logs(BLOCKED_FILE)), language="text")
    with tabs[2]:
        st.code("".join(load_logs(UNBLOCKED_FILE)), language="text")

# ------------------- PAGE: UTILITIES -------------------
elif page == "🎯 Utilities":
    st.title("🛠️ Dev Tools Panel")
    st.markdown("Use these buttons to trigger test intrusions or clear logs.")

    col1, col2 = st.columns(2)
    if col1.button("🚨 Simulate Intrusion"):
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.ctime()} | 192.168.1.50 -> 10.0.0.1 | Prediction: DoS\n")
        st.success("✅ Intrusion simulated!")

    if col2.button("🧹 Clear Logs"):
        open(LOG_FILE, "w").close()
        open(BLOCKED_FILE, "w").close()
        open(UNBLOCKED_FILE, "w").close()
        st.warning("🗑️ All logs cleared!")

# ------------------- PAGE: ACTIONS -------------------
elif page == "🎯 Actions":
    st.title("🎯 Manual Controls & Dev Tools")

    col1, col2 = st.columns(2)
    with col1:
        ip_to_unblock = st.text_input("🔓 Enter IP to Unblock")

        if st.button("Unlock IP"):
            if ip_to_unblock.strip() == "":
                st.warning("⚠️ Please enter a valid IP address before unblocking.")
            else:
                with open(UNBLOCKED_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{time.ctime()} - UNBLOCKED: {ip_to_unblock}\n")
                st.success(f"{ip_to_unblock} marked as unblocked (Simulated).")


    with col2:
        if st.button("Force Unblock All"):
            blocked_ips = load_logs(BLOCKED_FILE)
            with open(UNBLOCKED_FILE, "a") as f:
                for entry in blocked_ips:
                    if "BLOCKED" in entry:
                        ip = entry.split("BLOCKED:")[-1].strip()
                        f.write(f"{time.ctime()} - UNBLOCKED: {ip}\n")
            open(BLOCKED_FILE, "w").close()
            st.warning("⚠️ All blocked IPs forcefully unblocked (Simulated).")

# ------------------- FOOTER -------------------
st.markdown("---")

