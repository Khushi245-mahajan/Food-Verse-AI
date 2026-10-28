import streamlit as st
from utils import history
from utils.ui import hero, badge

hero("📊 Dashboard & Reports", "Everything you analyzed in this browser session, with charts and downloads.")
st.caption("History lives in your browser session only. It resets on refresh and is never saved on the server.")

c1, c2 = st.columns(2)
if c1.button("Load demo data"):
    for module, item, cat, kcal in [("Recognition", "Pizza", "Fast food", 575), ("Recognition", "Greek Salad", "Salad", 225),
                                    ("Recognition", "Ice Cream", "Dessert", 325), ("Nutrition", "Maintain weight plan", "Vegetarian", 2000)]:
        history.add(module, item, cat, kcal, "demo", "DEMO DATA")
if c2.button("Clear history"):
    history.clear()
    st.success("History cleared.")

df = history.get_df()
if df.empty:
    st.info("No analyses yet. Run a module or click 'Load demo data'.")
    st.stop()
if (df["source"] == "demo").any():
    badge("demo")
a, b, c = st.columns(3)
a.metric("Analyses", len(df))
a.caption(f"Modules used: {df['module'].nunique()}")
kc = df["kcal_mid"].dropna()
b.metric("Avg estimated kcal", f"{kc.mean():.0f}" if len(kc) else "n/a")
c.metric("Latest", df.iloc[-1]["item"])

left, right = st.columns(2)
with left:
    st.markdown("**Estimated calories by item**")
    cal = df.dropna(subset=["kcal_mid"])
    if len(cal):
        st.bar_chart(cal.set_index(cal["item"] + " #" + cal.index.astype(str))["kcal_mid"])
    else:
        st.caption("No calorie data yet.")
with right:
    st.markdown("**Food categories**")
    st.bar_chart(df[df["category"] != ""]["category"].value_counts())
st.markdown("**History**")
st.dataframe(df, hide_index=True)
d1, d2 = st.columns(2)
d1.download_button("Download CSV", df.to_csv(index=False), "food_verse_history.csv", "text/csv")
d2.download_button("Download JSON", history.df_to_json(df), "food_verse_history.json", "application/json")
