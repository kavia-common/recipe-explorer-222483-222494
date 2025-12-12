import os

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/images", tags=["images"])

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploaded_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", summary="Upload image", description="Upload an image and get back a URL path")
async def upload_image(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file")
    # Save file to UPLOAD_DIR
    dest_path = os.path.join(UPLOAD_DIR, file.filename)
    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)
    return {"url": f"/images/{file.filename}"}

@router.get("/{filename}", summary="Serve image", description="Return a previously uploaded image")
def get_image(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)
