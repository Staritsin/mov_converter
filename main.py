from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os, uuid, subprocess

app = FastAPI()
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def cleanup_files(*paths):
    for path in paths:
        if os.path.exists(path):
            os.remove(path)

@app.get("/")
def root():
    return {"message": "🔥 FFMPEG API is working!"}

@app.post("/convert")
async def convert_mov_to_mp4(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext != ".mov":
            return JSONResponse(content={"error": "❌ Только .mov поддерживается"}, status_code=400)

        uid = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{uid}.mov")
        output_path = os.path.join(OUTPUT_DIR, f"{uid}.mp4")

        with open(input_path, "wb") as f:
            f.write(await file.read())

        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vcodec", "libx264",
            "-acodec", "aac",
            "-strict", "experimental",
            output_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)

        print("FFMPEG Output:", result.stdout)
        print("FFMPEG Error:", result.stderr)

        background_tasks.add_task(cleanup_files, input_path, output_path)
        return FileResponse(output_path, media_type="video/mp4", filename="converted.mp4")

    except subprocess.CalledProcessError as e:
        return JSONResponse(content={"error": f"💥 FFMPEG ошибка: {e.stderr}"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": f"💥 Ошибка: {str(e)}"}, status_code=500)
