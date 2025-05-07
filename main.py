from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
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
    try:
        # Проверка расширения
        input_ext = os.path.splitext(file.filename)[1].lower()
        if input_ext != ".mov":
            return JSONResponse(content={"error": "❌ Only .mov files supported"}, status_code=400)

        # Уникальные имена
        uid = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{uid}.mov")
        output_path = os.path.join(OUTPUT_DIR, f"{uid}.mp4")

        # Сохраняем загруженный файл
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Конвертация
        clip = VideoFileClip(input_path)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        clip.close()

        return FileResponse(output_path, media_type="video/mp4", filename="converted.mp4")

    except Exception as e:
        return JSONResponse(
            content={"error": f"💥 Ошибка сервера: {str(e)}"},
            status_code=500
        )
