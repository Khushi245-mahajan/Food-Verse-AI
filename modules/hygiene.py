"""Module C logic: OpenCV frame sampling + Haar-cascade person visibility + image quality checks.

Supported: sampling frames, face/upper-body visibility (classic Haar cascades, error-prone),
brightness and blur checks. NOT supported: gloves, hairnets, handwashing, cross-contamination,
bacteria, or any hygiene certification.
"""
from functools import lru_cache
import cv2
import numpy as np

UNSUPPORTED = ["Hand-washing detection", "Glove / hairnet / apron detection", "Cross-contamination or unsafe-handling detection",
               "Surface cleanliness or pest detection", "Any hygiene certification or food-safety verdict"]


@lru_cache(maxsize=1)
def _cascades():
    base = cv2.data.haarcascades
    face = cv2.CascadeClassifier(base + "haarcascade_frontalface_default.xml")
    body = cv2.CascadeClassifier(base + "haarcascade_upperbody.xml")
    if face.empty():
        raise RuntimeError("OpenCV face cascade file is missing from this installation.")
    return face, body


def _shrink(bgr, width=640):
    h, w = bgr.shape[:2]
    return cv2.resize(bgr, (width, int(h * width / w))) if w > width else bgr


def analyze_frame(bgr: np.ndarray) -> dict:
    bgr = _shrink(bgr)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    face, body = _cascades()
    faces = face.detectMultiScale(gray, 1.1, 5, minSize=(40, 40))
    bodies = body.detectMultiScale(gray, 1.1, 3, minSize=(80, 80)) if not body.empty() else []
    out = bgr.copy()
    for (x, y, w, h) in faces:
        cv2.rectangle(out, (x, y), (x + w, y + h), (60, 170, 80), 2)
    for (x, y, w, h) in bodies:
        cv2.rectangle(out, (x, y), (x + w, y + h), (230, 150, 40), 2)
    return {"faces": len(faces), "bodies": len(bodies), "brightness": float(gray.mean()),
            "sharpness": float(cv2.Laplacian(gray, cv2.CV_64F).var()),
            "annotated": cv2.cvtColor(out, cv2.COLOR_BGR2RGB)}


def sample_frames(path: str, max_frames: int = 12) -> list:
    """Return [(timestamp_seconds, bgr_frame)] evenly spaced across the video."""
    cap = cv2.VideoCapture(path)
    try:
        if not cap.isOpened():
            raise ValueError("Could not open the video. Try an MP4 (H.264) file.")
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        if total <= 0:
            raise ValueError("The video has no readable frames.")
        frames = []
        for i in np.linspace(0, total - 1, min(max_frames, total)).astype(int):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(i))
            ok, frame = cap.read()
            if ok:
                frames.append((round(i / fps, 1), frame))
        if not frames:
            raise ValueError("No frames could be decoded from this video.")
        return frames
    finally:
        cap.release()


def frames_from_images(pil_images) -> list:
    return [(float(i), cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)) for i, im in enumerate(pil_images)]


def build_report(results: list) -> dict:
    n = len(results)
    person = sum(1 for r in results if r["faces"] or r["bodies"])
    dark = sum(1 for r in results if r["brightness"] < 60)
    blur = sum(1 for r in results if r["sharpness"] < 50)
    obs = [f"Analyzed {n} frame(s).",
           f"A person (face or upper body) was detected in {person} of {n} frame(s) ({100 * person / n:.0f}%).",
           f"{dark} frame(s) were very dark and {blur} were blurry; detection is less reliable on those."]
    if person == 0:
        obs.append("No person detected. The detector only finds fairly frontal, well-lit faces/upper bodies.")
    return {"frames": n, "person_frames": person, "dark_frames": dark, "blurry_frames": blur, "observations": obs}
