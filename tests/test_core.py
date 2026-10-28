"""Unit tests for non-UI logic. Run: python -m unittest discover -s tests -v   (or: pytest)"""
import io, os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from PIL import Image
import cv2
from utils.validation import validate_upload, load_image
from utils import history
from modules import recognition, freshness, hygiene, recipes, nutrition


def png_bytes(color=(200, 30, 30), size=(64, 64)):
    buf = io.BytesIO(); Image.new("RGB", size, color).save(buf, "PNG"); return buf.getvalue()


class TestValidation(unittest.TestCase):
    def test_rejects_bad_extension(self):
        self.assertIn("Unsupported", validate_upload("a.exe", 10, ["jpg"], 5))
    def test_rejects_large_and_empty(self):
        self.assertIn("limit", validate_upload("a.jpg", 6 * 1048576, ["jpg"], 5))
        self.assertIn("empty", validate_upload("a.jpg", 0, ["jpg"], 5))
    def test_accepts_valid(self):
        self.assertIsNone(validate_upload("a.JPG", 100, ["jpg"], 5))
    def test_corrupt_image_raises(self):
        with self.assertRaises(ValueError):
            load_image(b"not an image")
    def test_loads_image(self):
        self.assertEqual(load_image(png_bytes()).mode, "RGB")


class TestRecognitionData(unittest.TestCase):
    def test_lookup(self):
        r = recognition.lookup_nutrition("Apple Pie")
        self.assertEqual(r["label"], "apple_pie"); self.assertGreater(r["kcal_high"], r["kcal_low"])
    def test_unknown_returns_none(self):
        self.assertIsNone(recognition.lookup_nutrition("zzz_unknown"))


class TestFreshness(unittest.TestCase):
    def test_blank_image_is_insufficient(self):
        self.assertEqual(freshness.analyze(Image.new("RGB", (100, 100), (255, 255, 255)))["status"], "insufficient")
    def test_clean_scores_higher_than_spotted(self):
        clean = Image.new("RGB", (200, 200), (220, 30, 30))
        arr = np.array(clean); arr[:100, :100] = (60, 30, 10); spotted = Image.fromarray(arr)
        a, b = freshness.analyze(clean), freshness.analyze(spotted)
        self.assertEqual(a["status"], "ok"); self.assertGreater(a["score"], b["score"])


class TestHygiene(unittest.TestCase):
    def test_frame_analysis_and_report(self):
        res = [hygiene.analyze_frame(np.zeros((240, 320, 3), np.uint8))]
        rep = hygiene.build_report(res)
        self.assertEqual(rep["frames"], 1); self.assertEqual(rep["person_frames"], 0); self.assertEqual(rep["dark_frames"], 1)
    def test_invalid_video_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            f.write(b"garbage"); f.flush()
            with self.assertRaises(ValueError):
                hygiene.sample_frames(f.name)
    def test_sample_frames_from_generated_video(self):
        path = os.path.join(tempfile.mkdtemp(), "t.avi")
        w = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"MJPG"), 10, (160, 120))
        for i in range(30):
            w.write(np.full((120, 160, 3), i * 8, np.uint8))
        w.release()
        self.assertEqual(len(hygiene.sample_frames(path, 5)), 5)


class TestRecipes(unittest.TestCase):
    def test_vegetarian_filter(self):
        out = recipes.suggest(recipes.parse_ingredients("rice, egg, onion, tomato"), diet="Vegetarian")
        self.assertTrue(out and all(r["veg"] for r in out))
    def test_plural_matching_and_ranking(self):
        out = recipes.suggest(recipes.parse_ingredients("tomatoes, pasta, garlic, basil"))
        self.assertEqual(out[0]["name"], "Tomato Basil Pasta")
    def test_no_match(self):
        self.assertEqual(recipes.suggest({"unobtainium"}), [])


class TestNutrition(unittest.TestCase):
    def test_bmr_known_value(self):
        self.assertAlmostEqual(nutrition.bmr("Male", 70, 175, 30), 1648.75, places=1)
    def test_safety_floor(self):
        t = nutrition.daily_target("Female", 40, 150, 60, "Sedentary", "Lose weight")
        self.assertGreaterEqual(t["kcal"], 1200); self.assertTrue(t["notes"])
    def test_minor_gets_maintenance(self):
        self.assertEqual(nutrition.daily_target("Male", 55, 165, 15, "Lightly active", "Lose weight")["goal"], "Maintain weight")
    def test_goal_ordering(self):
        k = {g: nutrition.daily_target("Male", 80, 180, 30, "Moderately active", g)["kcal"] for g in nutrition.GOALS}
        self.assertLess(k["Lose weight"], k["Maintain weight"]); self.assertLess(k["Maintain weight"], k["Gain weight"])
    def test_allergy_exclusion(self):
        plan = nutrition.build_plan(2000, "Vegetarian", ["dairy", "nuts", "gluten"])
        text = " ".join(r["Dish"].lower() for r in plan["rows"])
        for bad in ("paneer", "curd", "almond", "paratha", "oats", "roti", "yogurt", "poha"):
            self.assertNotIn(bad, text)
    def test_vegan_plan(self):
        plan = nutrition.build_plan(1800, "Vegan", [])
        self.assertEqual(len(plan["rows"]), 4)
        self.assertNotIn("chicken", " ".join(r["Dish"].lower() for r in plan["rows"]))


class TestHistory(unittest.TestCase):
    def test_df_and_json(self):
        df = history.records_to_df([history.make_record("A", "Pizza", "Fast food", 500, "model")])
        self.assertEqual(list(df.columns), history.COLUMNS); self.assertIn("Pizza", history.df_to_json(df))


if __name__ == "__main__":
    unittest.main()
