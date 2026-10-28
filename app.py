"""Food Verse AI: entry point and sidebar navigation. Run with: streamlit run app.py"""
import streamlit as st
import config

st.set_page_config(page_title=config.APP_NAME, page_icon="🥗", layout="wide")

from utils.ui import inject_css  # noqa: E402  (after set_page_config)

inject_css()
st.sidebar.markdown("### 🥗 Food Verse AI")
st.sidebar.caption("Multimodal food intelligence prototype")

pages = [
    st.Page("pages/home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/food_recognition.py", title="Food Recognition", icon="📷"),
    st.Page("pages/freshness.py", title="Freshness Check", icon="🍎"),
    st.Page("pages/hygiene.py", title="Hygiene Monitoring", icon="🧼"),
    st.Page("pages/cooking.py", title="Cooking Assistant", icon="🍳"),
    st.Page("pages/nutrition.py", title="Nutrition Planner", icon="🥦"),
    st.Page("pages/dashboard.py", title="Dashboard & Reports", icon="📊"),
]
st.navigation(pages).run()
