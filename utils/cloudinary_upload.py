import cloudinary
import cloudinary.uploader
import cloudinary.api
from fastapi import HTTPException
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)



def UploadToCloudinary(images):
    image_urls = []

    # Upload images to Cloudinary
    if images:
        for image in images:
            try:
                upload_result = cloudinary.uploader.upload(image.file, folder="shops")
                image_url = upload_result.get("url")
                image_urls.append(image_url)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
    return image_urls


def UploadPdfToCloud(pdf):
    upload_result = cloudinary.uploader.upload(pdf.file, folder="shops", resource_type="raw")
    image_url = upload_result.get("url")
    return image_url
