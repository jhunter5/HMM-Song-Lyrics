FROM python:3.10-slim

# ffmpeg is required by Spleeter for audio decoding/encoding.
# libsndfile1 is required by soundfile (used by librosa).
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

ENV SPLEETER_DATA=/app/pretrained_models

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY processor.py main.py ./

EXPOSE 5001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
