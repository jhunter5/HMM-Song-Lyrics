from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from processor import process

app = FastAPI(title="Text Processing Service")


@app.post("/upload")
async def upload(
    lyrics: UploadFile = File(...),
    audio:  UploadFile = File(None),   # forwarded by YARP but not used here
) -> JSONResponse:
    raw = await lyrics.read()
    text = raw.decode("utf-8", errors="replace")
    result = process(text)
    return JSONResponse(result)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
