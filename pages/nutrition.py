import pandas as pd
import streamlit as st
from modules import nutrition as nt
from utils import history
from utils.ui import hero, badge

hero("🥦 Personalized Nutrition Planner", "Estimate a daily calorie target and get a sample meal plan that respects diet and allergies.")
st.info("These are estimates for general information. They are not medical nutrition advice; see a registered dietitian or doctor for personal needs, "
        "medical conditions, pregnancy, or eating-disorder concerns.")
with st.form("plan"):
    c1, c2, c3, c4 = st.columns(4)
    age = c1.number_input("Age", 10, 100, 25)
    sex = c2.selectbox("Sex (for the formula)", ["Female", "Male"])
    height = c3.number_input("Height (cm)", 120, 220, 168)
    weight = c4.number_input("Weight (kg)", 30, 250, 65)
    d1, d2, d3 = st.columns(3)
    activity = d1.selectbox("Activity level", list(nt.ACTIVITY), index=1)
    goal = d2.selectbox("Goal", list(nt.GOALS))
    diet = d3.selectbox("Dietary preference", ["No preference", "Vegetarian", "Vegan"])
    allergies = st.text_input("Food allergies (comma separated)", placeholder="peanut, dairy, gluten")
    go = st.form_submit_button("Generate plan")

if go:
    t = nt.daily_target(sex, weight, height, age, activity, goal)
    for n in t["notes"]:
        st.warning(n)
    badge("rule")
    m = st.columns(4)
    m[0].metric("Daily target", f"{t['kcal']} kcal")
    m[1].metric("Protein", f"{t['protein_g']} g")
    m[2].metric("Carbs", f"{t['carbs_g']} g")
    m[3].metric("Fat", f"{t['fat_g']} g")
    st.caption(f"Estimated maintenance energy: {t['tdee']} kcal/day (Mifflin-St Jeor x activity factor). Goal used: {t['goal']}.")
    allergy_list = [a for a in allergies.split(",") if a.strip()]
    plan = nt.build_plan(t["kcal"], diet, allergy_list)
    if plan["missing_slots"]:
        st.error("No safe dish in our small library for: " + ", ".join(plan["missing_slots"]) +
                 ". Please plan these meals with a professional. Allergies are matched by keyword only, so always read labels.")
    if plan["rows"]:
        df = pd.DataFrame(plan["rows"])
        st.dataframe(df, hide_index=True)
        tot = plan["totals"]
        st.caption(f"Plan total: {tot['kcal']} kcal | {tot['Protein (g)']} g protein | {tot['Carbs (g)']} g carbs | {tot['Fat (g)']} g fat "
                   "(close to, not exactly, the target because the dish library is small).")
        st.download_button("Download plan (CSV)", df.to_csv(index=False), "meal_plan.csv", "text/csv")
        history.add("Nutrition", f"{t['goal']} plan", diet, tot["kcal"], "rule-based", f"allergies: {allergies or 'none'}")
    st.caption("Allergy matching checks ingredient keywords in a tiny demo library. It is not a substitute for label reading or medical guidance.")
