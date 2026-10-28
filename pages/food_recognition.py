import streamlit as st
import config
from modules import recognition as rec
from utils import history
from utils.ui import hero, badge, image_upload

hero("📷 Food Recognition", "Upload a food photo. A pretrained Food-101 model predicts the dish and we look up approximate nutrition.")
mode = st.radio("Mode", ["Real model", "Demo mode (no model)"], horizontal=True,
                help="Demo mode skips the model and shows illustrative nutrition data for a food you pick.")

if mode == "Real model":
    st.caption(f"Model: `{config.FOOD_MODEL_ID}` (Food-101, 101 classes). The first run downloads the weights, which can take a minute.")
    img = image_upload("Food image", config.IMAGE_TYPES, config.MAX_IMAGE_MB, "rec_img",
                       f"JPG, PNG, WEBP or BMP up to {config.MAX_IMAGE_MB} MB. One dish, well lit.")
    if img is not None:
        left, right = st.columns(2)
        left.image(img, caption="Uploaded image")
        if right.button("Analyze food", type="primary"):
            try:
                with st.spinner("Running the model..."):
                    preds = rec.classify(img)
            except rec.ModelUnavailable as exc:
                right.error(f"{exc}")
                right.info("Switch to Demo mode above, or check the README troubleshooting section.")
                st.stop()
            top = preds[0]
            with right:
                badge("model")
                st.subheader(rec.pretty(top["label"]))
                st.progress(min(top["score"], 1.0), text=f"Confidence: {top['score']:.1%}")
                for p in preds[1:]:
                    st.caption(f"Also possible: {rec.pretty(p['label'])} ({p['score']:.1%})")
                info = rec.lookup_nutrition(top["label"])
                if top["score"] < config.MIN_CONFIDENCE:
                    st.warning("Confidence is below 50%, so nutrition details are not shown. Try a clearer photo.")
                elif info is None:
                    st.info("This food is not in the small nutrition table, so no estimate is shown.")
                else:
                    badge("rule")
                    st.metric("Estimated calories", f"{info['kcal_low']:.0f}-{info['kcal_high']:.0f} kcal", info["serving"], delta_color="off")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Protein", f"{info['protein_g']} g")
                    c2.metric("Carbs", f"{info['carbs_g']} g")
                    c3.metric("Fat", f"{info['fat_g']} g")
                history.add("Recognition", rec.pretty(top["label"]), info["category"] if info and top["score"] >= config.MIN_CONFIDENCE else "Unknown",
                            info["kcal_mid"] if info and top["score"] >= config.MIN_CONFIDENCE else None, f"model {config.FOOD_MODEL_ID}",
                            f"confidence {top['score']:.2f}")
else:
    badge("demo")
    st.warning("Demo mode: no image is analyzed. The values below come from the reference table for the food you select.")
    choice = st.selectbox("Pick a sample food", rec.known_foods(), format_func=rec.pretty)
    info = rec.lookup_nutrition(choice)
    st.subheader(rec.pretty(choice))
    st.metric("Estimated calories", f"{info['kcal_low']:.0f}-{info['kcal_high']:.0f} kcal", info["serving"], delta_color="off")
    if st.button("Add demo item to history"):
        history.add("Recognition (demo)", rec.pretty(choice), info["category"], info["kcal_mid"], "demo", "not a model prediction")
        st.success("Added. See the Dashboard.")
st.caption("Calorie values are rough per-serving estimates from a small reference table, not measurements.")
