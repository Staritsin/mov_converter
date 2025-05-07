from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
import subprocess

app = FastAPI()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"message": "🔥 FFMPEG API is working!"}

@app.post("/convert")
async def convert_mov_to_mp4(file: UploadFile = File(...)):
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext != ".mov":
            return JSONResponse(content={"error": "❌ Только .mov поддерживается"}, status_code=400)

        uid = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{uid}.mov")
        output_path = os.path.join(OUTPUT_DIR, f"{uid}.mp4")

        # Сохраняем .mov
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # Конвертация через ffmpeg
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vcodec", "libx264",
            "-acodec", "aac",
            "-strict", "experimental",
            output_path
        ]
        subprocess.run(cmd, check=True)

        return FileResponse(output_path, media_type="video/mp4", filename="converted.mp4")

    except subprocess.CalledProcessError as e:
        return JSONResponse(content={"error": f"💥 Ошибка FFMPEG: {str(e)}"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": f"💥 Ошибка: {str(e)}"}, status_code=500)
