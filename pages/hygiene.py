import os
import tempfile
import streamlit as st
import config
from modules import hygiene as hy
from utils import history
from utils.ui import hero, badge
from utils.validation import validate_upload, load_image

hero("🧼 Hygiene Monitoring (prototype)", "Samples frames from food-prep footage and reports what a basic detector can see.")
st.warning("This prototype cannot certify hygiene or detect bacteria, handwashing, gloves, hairnets or unsafe handling. "
           "It only checks whether a person is visible and whether the footage is bright and sharp enough.")
with st.expander("Unsupported checks (not implemented)"):
    st.markdown("\n".join(f"- {u}" for u in hy.UNSUPPORTED))

tab_v, tab_i = st.tabs(["Video", "Image sequence"])
results, stamps = [], []
with tab_v:
    vid = st.file_uploader("Short video", type=config.VIDEO_TYPES, key="hy_vid", help=f"MP4/AVI/MOV/MKV up to {config.MAX_VIDEO_MB} MB")
    n = st.slider("Frames to analyze", 4, 20, 10)
    if vid is None:
        st.info("Upload a short clip (under ~1 minute) to begin.")
    elif (err := validate_upload(vid.name, vid.size, config.VIDEO_TYPES, config.MAX_VIDEO_MB)):
        st.error(err)
    elif st.button("Analyze video", type="primary"):
        path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix="." + vid.name.rsplit(".", 1)[-1]) as tmp:
                tmp.write(vid.getvalue())
                path = tmp.name
            with st.spinner("Sampling and analyzing frames..."):
                frames = hy.sample_frames(path, n)
                results = [hy.analyze_frame(f) for _, f in frames]
                stamps = [f"{t}s" for t, _ in frames]
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
        finally:
            if path and os.path.exists(path):
                os.remove(path)
with tab_i:
    imgs = st.file_uploader("Images (in order)", type=config.IMAGE_TYPES, accept_multiple_files=True, key="hy_imgs")
    if imgs and st.button("Analyze images", type="primary"):
        loaded = []
        for f in imgs[:20]:
            err = validate_upload(f.name, f.size, config.IMAGE_TYPES, config.MAX_IMAGE_MB)
            try:
                if err:
                    raise ValueError(f"{f.name}: {err}")
                loaded.append(load_image(f.getvalue(), 800))
            except ValueError as exc:
                st.error(str(exc))
        if loaded:
            results = [hy.analyze_frame(fr_[1]) for fr_ in hy.frames_from_images(loaded)]
            stamps = [f"image {i + 1}" for i in range(len(results))]

if results:
    rep = hy.build_report(results)
    badge("model", "rule")
    c1, c2, c3 = st.columns(3)
    c1.metric("Frames analyzed", rep["frames"])
    c2.metric("Frames with a person", rep["person_frames"])
    c3.metric("Dark / blurry frames", f"{rep['dark_frames']} / {rep['blurry_frames']}")
    st.markdown("**Report**\n\n" + "\n".join(f"- {o}" for o in rep["observations"]))
    st.caption("Green boxes = face detected, orange = upper body (OpenCV Haar cascades; can miss or misfire).")
    cols = st.columns(4)
    for i, (r, s) in enumerate(zip(results, stamps)):
        cols[i % 4].image(r["annotated"], caption=f"{s}: faces {r['faces']}, bodies {r['bodies']}")
    history.add("Hygiene", f"{rep['frames']} frames", "Video check", None, "OpenCV Haar cascades", f"person in {rep['person_frames']} frames")
