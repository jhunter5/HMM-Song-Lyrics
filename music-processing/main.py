from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from processor import process_audio

app = FastAPI(title="Music Processing Service")


@app.post("/process-audio")
async def upload_audio(audio: UploadFile = File(...)) -> JSONResponse:
    data = await audio.read()
    result = process_audio(data, audio.filename or "upload.mp3")
    return JSONResponse(result)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
