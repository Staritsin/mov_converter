from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import os
import uuid
from moviepy.editor import VideoFileClip

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "✅ MOV to MP4 API is working"}

@app.post("/convert")
async def convert_video(file: UploadFile = File(...)):
    input_ext = os.path.splitext(file.filename)[1].lower()
    if input_ext != ".mov":
        return {"error": "❌ Only .mov files are supported"}

    input_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.mov")
    output_path = os.path.join(OUTPUT_DIR, input_path.replace(".mov", ".mp4"))

    # Сохраняем загруженный файл
    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Конвертируем в .mp4
    clip = VideoFileClip(input_path)
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    clip.close()

    return FileResponse(output_path, media_type="video/mp4", filename="converted.mp4")
