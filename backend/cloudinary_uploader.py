import os

import cloudinary
import cloudinary.uploader
import cloudinary.api


def configure_cloudinary() -> bool:
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not cloud_name or not api_key or not api_secret:
        return False

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )
    return True


def upload_profile_picture(file_storage):
    if not configure_cloudinary():
        return None

    try:
        response = cloudinary.uploader.upload(
            file_storage,
            folder="secure-it/profiles",
            resource_type="image",
            unique_filename=True,
            overwrite=False,
        )
    except Exception:
        return None

    return response.get("secure_url")