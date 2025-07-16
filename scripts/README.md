# scripts/setup.sh — Google Speech-to-Text Docker Setup Script

## Purpose

This script automates the setup and deployment of the Google Speech-to-Text Docker service. It is designed to help you quickly get started with both Google Cloud and the local Dockerized backend.

## What It Does

- **Checks prerequisites:** Ensures Docker, Docker Compose, and (optionally) Google Cloud CLI are installed.
- **Google Cloud setup:** (If `gcloud` is available)
  - Authenticates with Google Cloud
  - Enables the Speech-to-Text API
  - Creates a service account and downloads its key
  - Grants the necessary permissions
- **Deploys the Docker service:** Builds and starts the backend using Docker Compose.
- **Tests the service:** Checks the health endpoint and tests transcription with a sample audio.
- **Prints helpful URLs and next steps.**

## How to Use

1. Make the script executable:
   ```sh
   chmod +x scripts/setup.sh
   ```

2. Run the script:
   ```sh
   ./scripts/setup.sh
   ```

3. Follow any prompts or instructions printed by the script.

## Flow

1. **Prerequisite Check:**  
   - Docker, Docker Compose, and gcloud (optional) must be installed.

2. **Google Cloud Setup:**  
   - If `gcloud` is installed, the script will:
     - Authenticate you (if needed)
     - Enable the Speech-to-Text API
     - Create a service account and download its key
     - Grant permissions

3. **Docker Deployment:**  
   - Builds and starts the service with Docker Compose.

4. **Testing:**  
   - Waits for the service to start
   - Checks `/health`
   - Optionally tests transcription

5. **Completion:**  
   - Prints URLs for the web interface and health check
   - Provides commands to stop the service and view logs

## Notes

- If you do not have `gcloud` installed, you must set up Google Cloud and download your service account key manually.
- The script is idempotent and can be run multiple times.
- For troubleshooting, check the output and logs.

---

**This script is ideal for quickly onboarding new developers or deploying the service on a new machine!** 