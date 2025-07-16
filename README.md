# Google Speech-to-Text Docker Implementation

This project provides a Docker-based implementation of Google Cloud Speech-to-Text API with a Flask web interface for easy audio transcription.

## Features

- 🎤 **Audio File Upload**: Upload and transcribe audio files through a web interface
- 🌍 **Multi-language Support**: Support for 15+ languages including English, Spanish, French, German, and more
- ☁️ **Google Cloud Integration**: Direct integration with Google Cloud Speech-to-Text API
- 🐳 **Docker Ready**: Complete Docker implementation for easy deployment
- 🔍 **Health Checks**: Built-in health monitoring
- 📊 **Sample Testing**: Test with Google Cloud Storage sample audio

## Prerequisites

1. **Google Cloud Project**: You need a Google Cloud project with Speech-to-Text API enabled
2. **Service Account**: Create a service account with Speech-to-Text permissions
3. **Docker & Docker Compose**: Installed on your system

## Setup Instructions

### 1. Google Cloud Setup

1. **Create a Google Cloud Project** (if you don't have one):
   ```bash
   # Install Google Cloud CLI
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   ```

2. **Enable Speech-to-Text API**:
   ```bash
   gcloud services enable speech.googleapis.com
   ```

3. **Create a Service Account**:
   ```bash
   gcloud iam service-accounts create speech-stt-service \
     --display-name="Speech-to-Text Service Account"
   ```

4. **Grant Speech-to-Text permissions**:
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:speech-stt-service@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/speech.admin"
   ```

5. **Download Service Account Key**:
   ```bash
   gcloud iam service-accounts keys create credentials/service-account-key.json \
     --iam-account=speech-stt-service@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

### 2. Project Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd /path/to/your/STT/folder
   ```

2. **Create credentials directory**:
   ```bash
   mkdir -p credentials
   ```

3. **Place your service account key** in `credentials/service-account-key.json`

### 3. Docker Deployment

#### Option A: Using Docker Compose (Recommended)

```bash
# Build and start the service
docker-compose up --build

# Run in background
docker-compose up -d --build

# Stop the service
docker-compose down
```

#### Option B: Using Docker directly

```bash
# Build the image
docker build -t google-stt-service .

# Run the container
docker run -p 5000:5000 \
  -v $(pwd)/credentials:/app/credentials:ro \
  -v $(pwd)/uploads:/app/uploads \
  google-stt-service
```

## Usage

### Web Interface

1. **Access the web interface**: Open your browser and go to `http://localhost:5000`

2. **Upload Audio File**:
   - Click "Choose File" and select an audio file
   - Choose the language from the dropdown
   - Click "Transcribe Audio"

3. **Test with Sample Audio**:
   - Use the "Test with Sample Audio" section to test with Google's sample audio

### API Endpoints

#### Health Check
```bash
curl http://localhost:5000/health
```

#### Transcribe Audio File
```bash
curl -X POST http://localhost:5000/transcribe \
  -F "audio_file=@/path/to/your/audio.wav" \
  -F "language=en-US"
```

#### Test with Sample Audio
```bash
curl -X POST http://localhost:5000/test \
  -F "language=en-US"
```

## Supported Audio Formats

- **Encoding**: LINEAR16, FLAC, MULAW, AMR, AMR_WB
- **Sample Rates**: 8000 Hz, 16000 Hz, 32000 Hz, 48000 Hz
- **File Formats**: WAV, FLAC, MP3, M4A, OGG

## Supported Languages

- English (US/UK)
- Spanish
- French
- German
- Italian
- Portuguese (Brazil)
- Russian
- Japanese
- Korean
- Chinese (Simplified)
- Arabic
- Hindi
- Urdu
- And many more...

## Configuration

### Environment Variables

- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key file
- `PORT`: Application port (default: 5000)

### Docker Compose Configuration

You can modify `docker-compose.yml` to:
- Change the exposed port
- Add additional environment variables
- Configure volumes for persistent storage

## Troubleshooting

### Common Issues

1. **"Speech client not initialized"**:
   - Check if service account key is properly mounted
   - Verify Google Cloud Speech-to-Text API is enabled
   - Ensure service account has proper permissions

2. **"Authentication failed"**:
   - Verify service account key is valid
   - Check if key file is properly mounted in Docker

3. **"Audio format not supported"**:
   - Convert audio to supported format (WAV recommended)
   - Check audio encoding and sample rate

4. **"Docker build fails"**:
   - Ensure Docker is running
   - Check internet connection for downloading dependencies

### Debug Commands

```bash
# Check container logs
docker-compose logs google-stt-service

# Access container shell
docker-compose exec google-stt-service bash

# Check health status
curl http://localhost:5000/health

# Test with sample audio
curl -X POST http://localhost:5000/test
```

## Development

### Local Development (without Docker)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variable**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

### Adding New Features

1. **Add new language support**: Modify the language dropdown in `app.py`
2. **Add new audio formats**: Update the `RecognitionConfig` in transcription functions
3. **Add new endpoints**: Create new Flask routes in `app.py`

## Security Considerations

- **Service Account Key**: Keep your service account key secure and never commit it to version control
- **Network Security**: Consider using HTTPS in production
- **File Uploads**: Implement file size limits and type validation for production use
- **Authentication**: Add user authentication for production deployments

## License

This project is for educational and development purposes. Please ensure compliance with Google Cloud terms of service.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues related to:
- **Google Cloud Speech-to-Text**: Check [Google Cloud Documentation](https://cloud.google.com/speech-to-text/docs)
- **Docker**: Check [Docker Documentation](https://docs.docker.com/)
- **Flask**: Check [Flask Documentation](https://flask.palletsprojects.com/) 