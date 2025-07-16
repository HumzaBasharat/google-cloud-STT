# Mock Google Speech-to-Text Service

This mock service simulates the Google Cloud Speech-to-Text API for local development and testing. No Google credentials or real Google Cloud account are required.

## Included Files
- `app_mock.py` — Flask app that mocks the Google STT API.
- `Dockerfile.mock` — Dockerfile to build the mock service.
- `docker-compose.mock.yml` — Docker Compose file to run the mock service.
- `requirements.txt` — Python dependencies for the mock app.

## How to Set Up and Run

### 1. Build and Run with Docker Compose

From this directory, run:

```sh
docker-compose -f docker-compose.mock.yml up --build
```

- This will build the mock service and run it on [http://localhost:5002](http://localhost:5002).
- The mock service exposes the same endpoints as the real service:
  - `/transcribe`
  - `/test`
  - `/health`

### 2. Usage
- You can POST audio files to `/transcribe` just like the real API.
- The service will return a fake/mock transcription.
- Useful for frontend/backend integration testing, CI/CD, or local development.

### 3. Stopping the Service
To stop the mock service, press `Ctrl+C` in the terminal where it’s running, or run:

```sh
docker-compose -f docker-compose.mock.yml down
```

## Endpoints
- `POST /transcribe` — Upload and transcribe audio file (returns mock result)
- `POST /test` — Test with sample audio (returns mock result)
- `GET /health` — Health check

## Notes
- No Google Cloud credentials are required.
- No real transcription is performed.
- If you want to use the real Google STT service, use your main Docker Compose and Flask app. 