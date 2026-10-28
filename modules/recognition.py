"""Module A logic: real Food-101 classification (Hugging Face) + nutrition lookup table."""
from functools import lru_cache
import pandas as pd
import config


class ModelUnavailable(RuntimeError):
    """Raised when the model or its dependencies cannot be loaded or run."""


@lru_cache(maxsize=1)
def load_classifier(model_id: str = config.FOOD_MODEL_ID):
    try:
        from transformers import pipeline  # imported lazily: heavy dependency
        return pipeline("image-classification", model=model_id)
    except Exception as exc:  # missing package, no network, out of memory...
        raise ModelUnavailable(f"Could not load model '{model_id}': {exc}") from exc


def classify(image, top_k: int = 3) -> list:
    """Return [{'label': 'apple_pie', 'score': 0.93}, ...] from the real model."""
    clf = load_classifier()
    try:
        return [{"label": r["label"], "score": float(r["score"])} for r in clf(image, top_k=top_k)]
    except Exception as exc:
        raise ModelUnavailable(f"Inference failed: {exc}") from exc


def normalize_label(label: str) -> str:
    return label.strip().lower().replace(" ", "_").replace("-", "_")


@lru_cache(maxsize=1)
def _table() -> pd.DataFrame:
    return pd.read_csv(config.DATA_DIR / "nutrition_facts.csv").set_index("label")


def known_foods() -> list:
    return list(_table().index)


def lookup_nutrition(label: str):
    """Approximate per-serving values from a small reference table; None if the food isn't covered."""
    key = normalize_label(label)
    t = _table()
    if key not in t.index:
        return None
    row = t.loc[key].to_dict()
    row["label"] = key
    row["kcal_mid"] = (row["kcal_low"] + row["kcal_high"]) / 2
    return row


def pretty(label: str) -> str:
    return normalize_label(label).replace("_", " ").title()
