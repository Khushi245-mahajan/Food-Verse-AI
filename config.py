"""Central configuration. Secrets come from environment variables or Streamlit secrets."""
import os
from pathlib import Path

APP_NAME = "Food Verse AI"
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

IMAGE_TYPES = ["jpg", "jpeg", "png", "webp", "bmp"]
VIDEO_TYPES = ["mp4", "avi", "mov", "mkv"]
MAX_IMAGE_MB = int(os.getenv("MAX_IMAGE_MB", "8"))
MAX_VIDEO_MB = int(os.getenv("MAX_VIDEO_MB", "50"))

# Pretrained Food-101 image classifier from the Hugging Face Hub (ViT-base, ~340 MB).
FOOD_MODEL_ID = os.getenv("FOOD_MODEL_ID", "nateraw/food")
MIN_CONFIDENCE = 0.50  # below this, nutrition info is not shown
LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-6")


def get_secret(name: str, default: str = "") -> str:
    """Read from env first, then Streamlit secrets (if running inside Streamlit)."""
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(name, default))
    except Exception:
        return default
