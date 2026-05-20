from pathlib import Path

from django.core.exceptions import ValidationError

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def validate_store_image(file_obj):
    suffix = Path(file_obj.name).suffix.lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Only JPG, PNG, and WEBP images are allowed.")
    if file_obj.size > MAX_IMAGE_BYTES:
        raise ValidationError("Images must be 5MB or smaller.")
