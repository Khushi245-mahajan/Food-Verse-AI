"""Module E logic: Mifflin-St Jeor energy estimate + allergen-aware sample meal plan (estimates only)."""
import json
import config

ACTIVITY = {"Sedentary": 1.2, "Lightly active": 1.375, "Moderately active": 1.55, "Very active": 1.725}
GOALS = {"Maintain weight": 1.0, "Lose weight": 0.85, "Gain weight": 1.10}
MACRO_SPLIT = {"Maintain weight": (0.20, 0.50, 0.30), "Lose weight": (0.30, 0.40, 0.30), "Gain weight": (0.20, 0.50, 0.30)}
SLOTS = {"breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snack": 0.10}
ALLERGEN_TERMS = {"dairy": ["milk", "cheese", "paneer", "curd", "yogurt", "butter", "ghee", "cream"],
                  "milk": ["milk", "cheese", "paneer", "curd", "yogurt", "butter", "ghee", "cream"],
                  "nuts": ["almond", "cashew", "walnut", "pistachio", "peanut", "nut"],
                  "peanut": ["peanut"], "egg": ["egg"],
                  "gluten": ["wheat", "bread", "pasta", "roti", "oats", "flour", "barley", "semolina"],
                  "wheat": ["wheat", "bread", "pasta", "roti", "flour", "semolina"],
                  "soy": ["soy", "tofu"], "fish": ["fish", "salmon", "tuna"],
                  "shellfish": ["prawn", "shrimp", "crab"], "sesame": ["sesame"]}


def bmr(sex: str, weight_kg: float, height_cm: float, age: int) -> float:
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + 5 if sex == "Male" else base - 161


def daily_target(sex, weight_kg, height_cm, age, activity, goal) -> dict:
    notes = []
    if age < 18 and goal != "Maintain weight":
        goal = "Maintain weight"
        notes.append("Under 18: weight-change targets are not generated. Showing maintenance only; please consult a pediatrician or dietitian.")
    tdee = bmr(sex, weight_kg, height_cm, age) * ACTIVITY[activity]
    target = tdee * GOALS[goal]
    floor = 1500 if sex == "Male" else 1200
    if target < floor:
        target = floor
        notes.append(f"Target raised to the safety floor of {floor} kcal/day. Very low-calorie diets need medical supervision.")
    p, c, f = MACRO_SPLIT[goal]
    return {"goal": goal, "tdee": round(tdee), "kcal": round(target), "protein_g": round(target * p / 4),
            "carbs_g": round(target * c / 4), "fat_g": round(target * f / 9), "notes": notes}


def _blocked(meal: dict, allergies: list) -> bool:
    text = " ".join(meal["ing"]) + " " + meal["name"].lower()
    for a in allergies:
        terms = ALLERGEN_TERMS.get(a, [a])
        if any(t in text for t in terms):
            return True
    return False


def _diet_ok(meal: dict, diet: str) -> bool:
    return {"No preference": True, "Vegetarian": meal["diet"] in ("veg", "vegan"), "Vegan": meal["diet"] == "vegan"}[diet]


def build_plan(target_kcal: int, diet: str = "No preference", allergies=None) -> dict:
    allergies = [a.strip().lower() for a in (allergies or []) if a.strip()]
    meals = json.loads((config.DATA_DIR / "meals.json").read_text(encoding="utf-8"))
    rows, missing = [], []
    for slot, share in SLOTS.items():
        slot_target = target_kcal * share
        options = [m for m in meals if m["slot"] == slot and _diet_ok(m, diet) and not _blocked(m, allergies)]
        if not options:
            missing.append(slot)
            continue
        m = min(options, key=lambda x: abs(x["kcal"] - slot_target))
        k = max(0.6, min(1.6, slot_target / m["kcal"]))
        rows.append({"Meal": slot.title(), "Dish": m["name"], "Portion": f"{k:.1f}x", "kcal": round(m["kcal"] * k),
                     "Protein (g)": round(m["p"] * k), "Carbs (g)": round(m["c"] * k), "Fat (g)": round(m["f"] * k)})
    totals = {key: sum(r[key] for r in rows) for key in ("kcal", "Protein (g)", "Carbs (g)", "Fat (g)")}
    return {"rows": rows, "totals": totals, "missing_slots": missing}
