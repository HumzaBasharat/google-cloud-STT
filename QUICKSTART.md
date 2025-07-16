# Quick Start Guide - Google Speech-to-Text Docker

This guide will get you up and running with the Google Speech-to-Text service in under 10 minutes.

## 🚀 Quick Setup (Automated)

### Option 1: Automated Setup (Recommended)

```bash
# Make the setup script executable
chmod +x scripts/setup.sh

# Run the automated setup
./scripts/setup.sh
```

The script will:
- ✅ Check prerequisites (Docker, Docker Compose)
- ✅ Set up Google Cloud project (if gcloud is installed)
- ✅ Enable Speech-to-Text API
- ✅ Create service account and download credentials
- ✅ Build and deploy Docker container
- ✅ Test the service

### Option 2: Manual Setup

If you prefer manual setup or the automated script fails:

#### Step 1: Google Cloud Setup

1. **Create a Google Cloud Project**:
   ```bash
   gcloud init
   ```

2. **Enable Speech-to-Text API**:
   ```bash
   gcloud services enable speech.googleapis.com
   ```

3. **Create Service Account**:
   ```bash
   gcloud iam service-accounts create speech-stt-service \
     --display-name="Speech-to-Text Service Account"
   ```

4. **Grant Permissions**:
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:speech-stt-service@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/speech.admin"
   ```

5. **Download Credentials**:
   ```bash
   mkdir -p credentials
   gcloud iam service-accounts keys create credentials/service-account-key.json \
     --iam-account=speech-stt-service@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

#### Step 2: Deploy with Docker

```bash
# Build and start the service
docker-compose up --build -d

# Check if it's running
docker-compose ps

# View logs
docker-compose logs -f
```

#### Step 3: Test the Service

```bash
# Health check
curl http://localhost:5000/health

# Test with sample audio
curl -X POST http://localhost:5000/test -F "language=en-US"
```

## 🌐 Access the Web Interface

Open your browser and go to: **http://localhost:5000**

You'll see a web interface where you can:
- 📁 Upload audio files for transcription
- 🌍 Select different languages
- 🧪 Test with sample audio
- 📊 View API documentation

## 📱 API Usage

### Upload Audio File
```bash
curl -X POST http://localhost:5000/transcribe \
  -F "audio_file=@/path/to/your/audio.wav" \
  -F "language=en-US"
```

### Test with Sample Audio
```bash
curl -X POST http://localhost:5000/test \
  -F "language=en-US"
```

### Health Check
```bash
curl http://localhost:5000/health
```

## 🛠️ Development

### Run Without Docker
```bash
# Install dependencies
pip install -r requirements.txt

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="credentials/service-account-key.json"

# Run the app
python app.py
```

### Test Script
```bash
# Test with Google Cloud sample
python test_stt.py

# Test with local audio file
python test_stt.py /path/to/audio.wav
```

## 🐛 Troubleshooting

### Common Issues

1. **"Speech client not initialized"**
   - Check if credentials file exists: `ls -la credentials/`
   - Verify credentials path in Docker: `docker-compose exec google-stt-service ls -la /app/credentials/`

2. **"Authentication failed"**
   - Verify service account has Speech-to-Text permissions
   - Check if API is enabled: `gcloud services list --enabled | grep speech`

3. **"Docker build fails"**
   - Ensure Docker is running
   - Check internet connection
   - Try: `docker system prune -f`

4. **"Service not accessible"**
   - Check if container is running: `docker-compose ps`
   - View logs: `docker-compose logs google-stt-service`
   - Check port binding: `docker port google-stt-service`

### Debug Commands

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f google-stt-service

# Access container shell
docker-compose exec google-stt-service bash

# Check environment variables
docker-compose exec google-stt-service env | grep GOOGLE

# Test health endpoint
curl -v http://localhost:5000/health
```

## 🧹 Cleanup

```bash
# Stop the service
docker-compose down

# Remove containers and images
docker-compose down --rmi all --volumes --remove-orphans

# Clean up Docker system
docker system prune -f
```

## 📋 Next Steps

1. **Customize the application**:
   - Modify `app.py` to add new features
   - Update language support in the web interface
   - Add authentication for production use

2. **Deploy to production**:
   - Use HTTPS in production
   - Add proper authentication
   - Set up monitoring and logging
   - Configure auto-scaling

3. **Integrate with other services**:
   - Connect to your existing applications
   - Add webhook support
   - Implement real-time transcription

## 📞 Support

- **Google Cloud Speech-to-Text**: [Documentation](https://cloud.google.com/speech-to-text/docs)
- **Docker**: [Documentation](https://docs.docker.com/)
- **Flask**: [Documentation](https://flask.palletsprojects.com/)

---

🎉 **You're all set!** Your Google Speech-to-Text service is now running and ready to use. 