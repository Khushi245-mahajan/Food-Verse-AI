"""Shared styling and small UI helpers."""
import streamlit as st

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
html, body, [class*="css"] {font-family:'Plus Jakarta Sans',sans-serif;}
.stApp {background:linear-gradient(180deg,#f1f8f3 0%,#ffffff 35%);}
[data-testid="stSidebar"] {background:#ffffff;border-right:1px solid #dcebdf;}
.fv-hero {background:linear-gradient(120deg,#1f7a4d,#43a86b);color:#fff;padding:1.8rem 2rem;border-radius:18px;margin-bottom:1.2rem;}
.fv-hero h1 {color:#fff;margin:0 0 .4rem;font-weight:800;letter-spacing:-.02em;padding:0;}
.fv-hero p {margin:0;max-width:62ch;line-height:1.55;}
.fv-card {background:#fff;border:1px solid #dcebdf;border-radius:14px;padding:1rem 1.1rem;box-shadow:0 1px 3px rgba(31,122,77,.08);margin-bottom:.6rem;}
.fv-card h4 {margin:.1rem 0 .3rem;color:#14532d;}
.fv-card p {margin:0;color:#34493c;font-size:.92rem;line-height:1.5;}
.fv-badge {display:inline-block;padding:.15rem .65rem;border-radius:999px;font-size:.78rem;font-weight:600;margin:0 .3rem .3rem 0;}
.b-model {background:#e0f3e7;color:#14532d;} .b-rule {background:#fff1c9;color:#6b4200;} .b-demo {background:#e3e7fb;color:#26307f;}
.stButton>button, .stDownloadButton>button {border-radius:10px;font-weight:600;}
.stButton>button[kind="primary"], .stFormSubmitButton>button {background:#1f7a4d;color:#fff;border:0;}
.stButton>button[kind="primary"]:hover, .stFormSubmitButton>button:hover {background:#17623e;color:#fff;}
@media (max-width:640px) {.fv-hero {padding:1.1rem;} .fv-hero h1 {font-size:1.6rem;}}
@media (prefers-reduced-motion:no-preference) {.fv-hero {animation:fvin .5s ease-out;} @keyframes fvin {from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}}
</style>"""

BADGES = {"model": ("b-model", "Actual model output"), "rule": ("b-rule", "Rule-based estimate"), "demo": ("b-demo", "Demo data (illustrative)")}


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def hero(title: str, text: str):
    st.markdown(f'<div class="fv-hero"><h1>{title}</h1><p>{text}</p></div>', unsafe_allow_html=True)


def badge(*kinds: str):
    st.markdown("".join(f'<span class="fv-badge {BADGES[k][0]}">{BADGES[k][1]}</span>' for k in kinds), unsafe_allow_html=True)


def card(title: str, text: str):
    st.markdown(f'<div class="fv-card"><h4>{title}</h4><p>{text}</p></div>', unsafe_allow_html=True)


def image_upload(label, types, max_mb, key, help_text):
    """Uploader + validation + decode. Returns a PIL image or None (errors are shown in the UI)."""
    import config
    from utils.validation import validate_upload, load_image
    f = st.file_uploader(label, type=types, key=key, help=help_text)
    if f is None:
        st.info(f"Upload a photo to begin. {help_text}")
        return None
    err = validate_upload(f.name, f.size, types, max_mb)
    if err:
        st.error(err)
        return None
    try:
        return load_image(f.getvalue())
    except ValueError as exc:
        st.error(str(exc))
        return None
