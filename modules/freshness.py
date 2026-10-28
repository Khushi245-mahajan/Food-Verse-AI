"""Module B logic: a transparent colour-based heuristic for visible blemishes.

This is NOT a trained freshness/spoilage model. It measures how much of the food region is
dark or brown, and how washed-out the colours are. Naturally brown foods (bread, potatoes)
will be flagged too, so the result is only a rough visual hint.
"""
import cv2
import numpy as np
from PIL import Image


def _resize(rgb: np.ndarray, side: int = 512) -> np.ndarray:
    h, w = rgb.shape[:2]
    scale = side / max(h, w)
    return cv2.resize(rgb, (int(w * scale), int(h * scale))) if scale < 1 else rgb


def band_for(score: float) -> str:
    if score >= 75:
        return "Few visible blemishes"
    if score >= 50:
        return "Some visible discoloration"
    return "Noticeable dark or discolored areas"


def analyze(image: Image.Image) -> dict:
    rgb = _resize(np.array(image.convert("RGB")))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    food = (s > 45) & (v > 35)  # coloured, non-black pixels ~ the food region (rough)
    coverage = float(food.mean())
    if coverage < 0.08:
        return {"status": "insufficient", "coverage": coverage,
                "message": "Not enough colored food area found. Use a close, well-lit photo on a plain background."}
    brown = food & (h >= 5) & (h <= 22) & (s > 60) & (v < 130)
    dark = food & (v < 60)
    flagged = brown | dark
    flag_ratio = float(flagged.sum() / food.sum())
    sat_mean = float(s[food].mean())
    score = float(np.clip(100 - 200 * flag_ratio - 0.3 * max(0.0, 100 - sat_mean), 0, 100))
    overlay = rgb.copy()
    overlay[flagged] = (0.4 * overlay[flagged] + 0.6 * np.array([220, 40, 40])).astype(np.uint8)
    return {"status": "ok", "score": round(score, 1), "band": band_for(score), "coverage": coverage,
            "flag_ratio": flag_ratio, "mean_saturation": sat_mean, "overlay": Image.fromarray(overlay),
            "uncertainty": "High: simple color heuristic, not a validated freshness model."}
