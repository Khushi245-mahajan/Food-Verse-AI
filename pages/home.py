import streamlit as st
from utils.ui import hero, card

hero("Food Verse AI", "A multimodal food intelligence prototype: recognize dishes from photos, get a rough visual quality hint, "
     "run a basic video check on food-prep footage, cook with what you have, and plan a day of meals.")

MODULES = [
    ("pages/food_recognition.py", "📷", "Food Recognition", "Pretrained Food-101 classifier with confidence scores and approximate calories."),
    ("pages/freshness.py", "🍎", "Freshness Check", "Color-based check for visible dark or brown areas. A hint, not a safety verdict."),
    ("pages/hygiene.py", "🧼", "Hygiene Monitoring", "Samples video frames with OpenCV and reports person visibility and image quality."),
    ("pages/cooking.py", "🍳", "Cooking Assistant", "Recipes from your ingredients, with optional LLM-written recipes."),
    ("pages/nutrition.py", "🥦", "Nutrition Planner", "Calorie target and an allergen-aware sample meal plan."),
    ("pages/dashboard.py", "📊", "Dashboard & Reports", "Session history, charts, and CSV / JSON downloads."),
]
for row in (MODULES[:3], MODULES[3:]):
    cols = st.columns(3)
    for col, (path, icon, title, text) in zip(cols, row):
        with col:
            card(f"{icon} {title}", text)
            st.page_link(path, label=f"Open {title}", icon=icon)

st.subheader("What is real and what is estimated")
st.markdown("""
| Module | Method | Status |
|---|---|---|
| Food Recognition | Pretrained ViT (Food-101) via Hugging Face | Real model, needs download on first run |
| Freshness | HSV color heuristic (OpenCV) | Rule-based, high uncertainty |
| Hygiene | Haar cascades + brightness/blur checks | Limited; no glove or handwashing detection |
| Cooking | Local recipe library; optional LLM | Rule-based; LLM only with an API key |
| Nutrition | Mifflin-St Jeor + small meal library | Estimates only |
""")
st.caption("Not medical or food-safety advice. Values are approximate.")
