import os
import tempfile
from flask import Flask, request, jsonify, render_template_string
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Mock speech client for testing
class MockSpeechClient:
    def __init__(self):
        self.initialized = True
        logger.info("Mock Google Cloud Speech client initialized successfully")
    
    def recognize(self, config, audio):
        # Return mock transcription results
        class MockResult:
            def __init__(self, transcript, confidence=0.95):
                self.alternatives = [MockAlternative(transcript, confidence)]
                self.is_final = True
        
        class MockAlternative:
            def __init__(self, transcript, confidence):
                self.transcript = transcript
                self.confidence = confidence
        
        class MockResponse:
            def __init__(self):
                self.results = [
                    MockResult("This is a mock transcription of your audio file."),
                    MockResult("The speech recognition service is working correctly.")
                ]
        
        return MockResponse()

# Initialize mock speech client
speech_client = MockSpeechClient()

def transcribe_audio_file(audio_file_path, language_code="en-US"):
    """Mock transcribe audio file"""
    try:
        logger.info(f"Mock transcribing audio file: {audio_file_path}")
        logger.info(f"Language: {language_code}")
        
        # Simulate processing time
        import time
        time.sleep(1)
        
        # Return mock transcript
        transcript = f"Mock transcription in {language_code}: This is a simulated transcription of your audio file. The speech recognition service is working correctly."
        
        return {"transcript": transcript, "success": True}
        
    except Exception as e:
        logger.error(f"Error in mock transcription: {e}")
        return {"error": str(e), "success": False}

def transcribe_gcs_audio(gcs_uri, language_code="en-US"):
    """Mock transcribe audio from Google Cloud Storage"""
    try:
        logger.info(f"Mock transcribing GCS audio: {gcs_uri}")
        logger.info(f"Language: {language_code}")
        
        # Simulate processing time
        import time
        time.sleep(1)
        
        # Return mock transcript
        transcript = f"Mock GCS transcription in {language_code}: This is a simulated transcription from Google Cloud Storage. The speech recognition service is working correctly."
        
        return {"transcript": transcript, "success": True}
        
    except Exception as e:
        logger.error(f"Error in mock GCS transcription: {e}")
        return {"error": str(e), "success": False}

@app.route('/')
def index():
    """Main page with upload form"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mock Google Speech-to-Text Service</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #005a87; }
            .result { margin-top: 20px; padding: 15px; background: white; border-radius: 4px; }
            .error { color: red; }
            .success { color: green; }
            .warning { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 4px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>🎤 Mock Google Speech-to-Text Service</h1>
        
        <div class="warning">
            <strong>⚠️ Mock Mode:</strong> This is a simulation of Google Speech-to-Text. 
            No actual transcription is performed. For real transcription, set up Google Cloud credentials.
        </div>
        
        <div class="container">
            <h2>Upload Audio File (Mock)</h2>
            <form action="/transcribe" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="audio_file">Select Audio File:</label>
                    <input type="file" id="audio_file" name="audio_file" accept="audio/*" required>
                </div>
                <div class="form-group">
                    <label for="language">Language:</label>
                    <select id="language" name="language">
                        <option value="en-US">English (US)</option>
                        <option value="en-GB">English (UK)</option>
                        <option value="es-ES">Spanish</option>
                        <option value="fr-FR">French</option>
                        <option value="de-DE">German</option>
                        <option value="it-IT">Italian</option>
                        <option value="pt-BR">Portuguese (Brazil)</option>
                        <option value="ru-RU">Russian</option>
                        <option value="ja-JP">Japanese</option>
                        <option value="ko-KR">Korean</option>
                        <option value="zh-CN">Chinese (Simplified)</option>
                        <option value="ar-SA">Arabic</option>
                        <option value="hi-IN">Hindi</option>
                        <option value="ur-PK">Urdu</option>
                    </select>
                </div>
                <button type="submit">Transcribe Audio (Mock)</button>
            </form>
        </div>
        
        <div class="container">
            <h2>Test with Sample Audio (Mock)</h2>
            <form action="/test" method="post">
                <div class="form-group">
                    <label for="test_language">Language:</label>
                    <select id="test_language" name="language">
                        <option value="en-US">English (US)</option>
                        <option value="en-GB">English (UK)</option>
                        <option value="es-ES">Spanish</option>
                        <option value="fr-FR">French</option>
                        <option value="de-DE">German</option>
                        <option value="it-IT">Italian</option>
                        <option value="pt-BR">Portuguese (Brazil)</option>
                        <option value="ru-RU">Russian</option>
                        <option value="ja-JP">Japanese</option>
                        <option value="ko-KR">Korean</option>
                        <option value="zh-CN">Chinese (Simplified)</option>
                        <option value="ar-SA">Arabic</option>
                        <option value="hi-IN">Hindi</option>
                        <option value="ur-PK">Urdu</option>
                    </select>
                </div>
                <button type="submit">Test with Sample Audio (Mock)</button>
            </form>
        </div>
        
        <div class="container">
            <h2>API Endpoints</h2>
            <p><strong>POST /transcribe</strong> - Upload and transcribe audio file (Mock)</p>
            <p><strong>POST /test</strong> - Test with sample audio (Mock)</p>
            <p><strong>GET /health</strong> - Health check</p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Handle audio file upload and transcription (Mock)"""
    try:
        if 'audio_file' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        language_code = request.form.get('language', 'en-US')
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        # Mock transcribe the audio
        result = transcribe_audio_file(temp_file_path, language_code)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in transcribe endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['POST'])
def test():
    """Test with sample audio (Mock)"""
    try:
        language_code = request.form.get('language', 'en-US')
        
        # Mock sample audio from Google Cloud Storage
        gcs_uri = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"
        
        result = transcribe_gcs_audio(gcs_uri, language_code)
        
        if result.get("success"):
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "speech_client_initialized": speech_client.initialized,
        "mode": "mock"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 