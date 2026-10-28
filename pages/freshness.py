import streamlit as st
import config
from modules import freshness as fr
from utils import history
from utils.ui import hero, badge, image_upload

hero("🍎 Freshness Check", "A simple color analysis that highlights dark or brown areas on fruit, vegetables and other foods.")
st.warning("Preliminary visual assessment only. A photo cannot show spoilage, contamination or pathogens. "
           "Never decide whether food is safe to eat from this result; check smell, texture, dates and storage.")
img = image_upload("Food image", config.IMAGE_TYPES, config.MAX_IMAGE_MB, "fresh_img",
                   "Close-up, good light, plain background, food filling most of the frame.")
if img is not None:
    res = fr.analyze(img)
    if res["status"] == "insufficient":
        st.error(res["message"])
    else:
        a, b = st.columns(2)
        a.image(img, caption="Original")
        b.image(res["overlay"], caption="Red = dark/brown pixels flagged by the heuristic")
        badge("rule")
        st.subheader(res["band"])
        st.progress(res["score"] / 100, text=f"Visual condition score: {res['score']:.0f}/100 (higher = fewer flagged areas)")
        m1, m2, m3 = st.columns(3)
        m1.metric("Flagged area", f"{res['flag_ratio']:.0%}")
        m2.metric("Food area in frame", f"{res['coverage']:.0%}")
        m3.metric("Mean color saturation", f"{res['mean_saturation']:.0f}")
        st.info(f"Uncertainty: {res['uncertainty']} Naturally brown foods (bread, potato, banana peel patterns) will be flagged too.")
        if st.button("Save to history"):
            history.add("Freshness", res["band"], "Visual check", None, "rule-based heuristic", f"score {res['score']}")
            st.success("Saved.")
