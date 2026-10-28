"""Upload validation and safe image loading."""
from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError


def validate_upload(name: str, size_bytes: int, allowed: list, max_mb: int):
    """Return an error message, or None if the upload is acceptable."""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if size_bytes == 0:
        return "The file is empty."
    if ext not in allowed:
        return f"Unsupported file type '.{ext}'. Please upload: {', '.join(allowed)}."
    if size_bytes > max_mb * 1024 * 1024:
        return f"File is {size_bytes / 1048576:.1f} MB; the limit is {max_mb} MB."
    return None


def load_image(data: bytes, max_side: int = 1024) -> Image.Image:
    """Decode bytes into an RGB image (EXIF-rotated, downscaled). Raises ValueError if unreadable."""
    try:
        Image.open(BytesIO(data)).verify()
        img = ImageOps.exif_transpose(Image.open(BytesIO(data))).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError) as exc:
        raise ValueError("Could not read this image. It may be corrupt or not an image file.") from exc
    img.thumbnail((max_side, max_side))
    return img
