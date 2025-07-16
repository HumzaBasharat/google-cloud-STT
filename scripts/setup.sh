#!/bin/bash

# Google Speech-to-Text Docker Setup Script
# This script helps set up the Google Cloud project and deploy the Docker service

set -e

echo "🚀 Google Speech-to-Text Docker Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        print_warning "Google Cloud CLI is not installed. You'll need to set up Google Cloud manually."
        return 1
    fi
    
    print_success "All prerequisites are met!"
    return 0
}

# Setup Google Cloud project
setup_google_cloud() {
    print_status "Setting up Google Cloud project..."
    
    # Check if user is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_warning "You are not authenticated with Google Cloud. Please run:"
        echo "gcloud auth login"
        echo "gcloud config set project YOUR_PROJECT_ID"
        return 1
    fi
    
    # Get current project
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        print_error "No project is set. Please run:"
        echo "gcloud config set project YOUR_PROJECT_ID"
        return 1
    fi
    
    print_status "Using project: $PROJECT_ID"
    
    # Enable Speech-to-Text API
    print_status "Enabling Speech-to-Text API..."
    gcloud services enable speech.googleapis.com --project="$PROJECT_ID"
    
    # Create service account if it doesn't exist
    SERVICE_ACCOUNT_NAME="speech-stt-service"
    SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
    
    if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" &>/dev/null; then
        print_status "Creating service account..."
        gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
            --display-name="Speech-to-Text Service Account" \
            --project="$PROJECT_ID"
    else
        print_status "Service account already exists"
    fi
    
    # Grant Speech-to-Text permissions
    print_status "Granting Speech-to-Text permissions..."
    gcloud projects add-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="roles/speech.admin"
    
    # Create credentials directory
    mkdir -p credentials
    
    # Download service account key
    print_status "Downloading service account key..."
    gcloud iam service-accounts keys create "credentials/service-account-key.json" \
        --iam-account="$SERVICE_ACCOUNT_EMAIL" \
        --project="$PROJECT_ID"
    
    print_success "Google Cloud setup completed!"
    return 0
}

# Build and run Docker service
deploy_docker() {
    print_status "Building and deploying Docker service..."
    
    # Create uploads directory
    mkdir -p uploads
    
    # Build and start the service
    docker-compose up --build -d
    
    print_success "Docker service deployed successfully!"
    print_status "Service is running at: http://localhost:5000"
}

# Test the service
test_service() {
    print_status "Testing the service..."
    
    # Wait for service to be ready
    sleep 10
    
    # Test health endpoint
    if curl -f http://localhost:5000/health &>/dev/null; then
        print_success "Service is healthy!"
    else
        print_error "Service health check failed"
        return 1
    fi
    
    # Test with sample audio
    print_status "Testing with sample audio..."
    RESPONSE=$(curl -s -X POST http://localhost:5000/test -F "language=en-US")
    
    if echo "$RESPONSE" | grep -q "transcript"; then
        print_success "Sample audio transcription successful!"
        echo "Transcript: $(echo "$RESPONSE" | grep -o '"transcript":"[^"]*"' | cut -d'"' -f4)"
    else
        print_warning "Sample audio transcription failed or returned error"
        echo "Response: $RESPONSE"
    fi
}

# Main execution
main() {
    echo ""
    
    # Check prerequisites
    if ! check_prerequisites; then
        exit 1
    fi
    
    # Setup Google Cloud (if gcloud is available)
    if command -v gcloud &> /dev/null; then
        if setup_google_cloud; then
            print_success "Google Cloud setup completed successfully!"
        else
            print_warning "Google Cloud setup failed. Please set up manually."
            echo "You'll need to:"
            echo "1. Create a Google Cloud project"
            echo "2. Enable Speech-to-Text API"
            echo "3. Create a service account with Speech-to-Text permissions"
            echo "4. Download the service account key to credentials/service-account-key.json"
        fi
    else
        print_warning "Google Cloud CLI not found. Please set up Google Cloud manually."
    fi
    
    # Check if credentials exist
    if [ ! -f "credentials/service-account-key.json" ]; then
        print_error "Service account key not found at credentials/service-account-key.json"
        echo "Please download your service account key and place it in the credentials directory."
        exit 1
    fi
    
    # Deploy Docker service
    deploy_docker
    
    # Test the service
    test_service
    
    echo ""
    print_success "Setup completed successfully!"
    echo ""
    echo "🎉 Your Google Speech-to-Text service is now running!"
    echo "📱 Web Interface: http://localhost:5000"
    echo "🔧 Health Check: http://localhost:5000/health"
    echo ""
    echo "To stop the service: docker-compose down"
    echo "To view logs: docker-compose logs -f"
    echo ""
}

# Run main function
main "$@" 