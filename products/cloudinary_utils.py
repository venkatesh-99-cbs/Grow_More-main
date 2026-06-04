import os
from dataclasses import dataclass

from django.conf import settings


class CloudinaryUploadError(Exception):
    """Raised when a product image cannot be uploaded to Cloudinary."""


@dataclass(frozen=True)
class CloudinaryUploadResult:
    secure_url: str
    public_id: str


def cloudinary_is_configured():
    return bool(
        os.environ.get("CLOUDINARY_URL")
        or (
            os.environ.get("CLOUDINARY_CLOUD_NAME")
            and os.environ.get("CLOUDINARY_API_KEY")
            and os.environ.get("CLOUDINARY_API_SECRET")
        )
    )


def upload_product_image(file_obj, *, public_id=None):
    """Upload a product image with server-side credentials and return display metadata."""
    if not file_obj:
        return None

    if not cloudinary_is_configured():
        return None

    try:
        import cloudinary
        import cloudinary.uploader
    except ImportError as exc:
        raise CloudinaryUploadError("Cloudinary dependencies are not installed.") from exc

    if not os.environ.get("CLOUDINARY_URL"):
        cloudinary.config(
            cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
            api_key=os.environ.get("CLOUDINARY_API_KEY"),
            api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
            secure=True,
        )

    folder = os.environ.get("CLOUDINARY_PRODUCT_FOLDER", "grow-more/products")
    options = {
        "folder": folder,
        "resource_type": "image",
        "overwrite": True,
        "quality": "auto",
        "fetch_format": "auto",
    }
    if public_id:
        options["public_id"] = public_id

    try:
        result = cloudinary.uploader.upload(file_obj, **options)
    except Exception as exc:
        raise CloudinaryUploadError("Image upload failed. Please try again.") from exc

    secure_url = result.get("secure_url")
    uploaded_public_id = result.get("public_id")
    if not secure_url or not uploaded_public_id:
        raise CloudinaryUploadError("Cloudinary did not return a usable image URL.")
    return CloudinaryUploadResult(secure_url=secure_url, public_id=uploaded_public_id)


def delete_product_image(public_id):
    """Delete a Cloudinary product image; failures are non-fatal for product deletion."""
    if not public_id or not cloudinary_is_configured():
        return False

    try:
        import cloudinary.uploader

        result = cloudinary.uploader.destroy(public_id, resource_type="image", invalidate=True)
        return result.get("result") in {"ok", "not found"}
    except Exception:
        if getattr(settings, "DEBUG", False):
            raise
        return False
