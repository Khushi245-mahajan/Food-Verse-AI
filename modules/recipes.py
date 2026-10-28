"""Module D logic: rule-based recipe matching over a small local recipe library."""
import json
import config

STAPLES = {"salt", "oil", "water", "pepper", "black pepper", "cooking oil"}


def _norm(word: str) -> str:
    w = word.strip().lower()
    return w[:-1] if len(w) > 3 and w.endswith("s") else w


def parse_ingredients(text: str) -> set:
    return {_norm(p) for p in text.replace("\n", ",").split(",") if p.strip()}


def load_recipes() -> list:
    return json.loads((config.DATA_DIR / "recipes.json").read_text(encoding="utf-8"))


def cuisines() -> list:
    return sorted({r["cuisine"] for r in load_recipes()})


def _has(ingredient: str, have: set) -> bool:
    ing = _norm(ingredient)
    return any(h == ing or h in ing or ing in h for h in have)


def suggest(have: set, diet="Any", cuisine_filter=None, max_time=None, difficulty=None) -> list:
    results = []
    for r in load_recipes():
        if diet == "Vegetarian" and not r["veg"]:
            continue
        if diet == "Non-vegetarian" and r["veg"]:
            continue
        if cuisine_filter and r["cuisine"] not in cuisine_filter:
            continue
        if max_time and r["time"] > max_time:
            continue
        if difficulty and difficulty != "Any" and r["difficulty"] != difficulty:
            continue
        needed = [i[0] for i in r["ingredients"] if _norm(i[0]) not in STAPLES]
        matched = [i for i in needed if _has(i, have)]
        if not matched:
            continue
        results.append({**r, "matched": matched, "missing": [i for i in needed if i not in matched],
                        "score": len(matched) / len(needed)})
    return sorted(results, key=lambda r: (-r["score"], r["time"]))
