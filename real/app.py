import os
import tempfile
from flask import Flask, request, jsonify, render_template_string
from google.cloud import speech
from google.cloud import storage
import logging
import mimetypes
from pydub import AudioSegment
import time
import wave

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize Google Cloud clients
try:
    speech_client = speech.SpeechClient()
    storage_client = storage.Client()
    logger.info("Google Cloud Speech and Storage clients initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Google Cloud clients: {e}")
    speech_client = None
    storage_client = None

def get_audio_encoding_and_rate(file_path):
    """Detect audio encoding and sample rate based on file extension or content."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.mp3':
        return speech.RecognitionConfig.AudioEncoding.MP3, 44100
    elif ext == '.flac':
        return speech.RecognitionConfig.AudioEncoding.FLAC, 44100
    elif ext == '.wav':
        # Detect actual sample rate from WAV header
        try:
            with wave.open(file_path, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
        except Exception as e:
            sample_rate = 44100  # fallback
        return speech.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate
    # Add more types as needed
    else:
        # Default to LINEAR16
        return speech.RecognitionConfig.AudioEncoding.LINEAR16, 16000

def get_audio_duration(file_path):
    """Get audio duration in seconds using pydub."""
    try:
        audio = AudioSegment.from_file(file_path)
        return len(audio) / 1000.0  # Convert milliseconds to seconds
    except Exception as e:
        logger.warning(f"Could not determine audio duration: {e}")
        return None

def upload_to_gcs(file_path, bucket_name="stt-audio-files-demo"):
    """Upload file to Google Cloud Storage and return the GCS URI. Only works if bucket exists."""
    try:
        if not storage_client:
            return None, "Storage client not initialized"
        
        # Only get the bucket, do not try to create it
        try:
            bucket = storage_client.get_bucket(bucket_name)
        except Exception as e:
            return None, f"Bucket '{bucket_name}' does not exist or is not accessible: {e}"
        
        # Generate unique blob name
        import uuid
        blob_name = f"audio/{uuid.uuid4()}_{os.path.basename(file_path)}"
        blob = bucket.blob(blob_name)
        
        # Upload file
        blob.upload_from_filename(file_path)
        
        # Return GCS URI
        gcs_uri = f"gs://{bucket_name}/{blob_name}"
        return gcs_uri, None
        
    except Exception as e:
        return None, str(e)

def transcribe_long_audio(gcs_uri, language_code="en-US"):
    """Transcribe long audio files using LongRunningRecognize."""
    try:
        if not speech_client:
            return {"error": "Speech client not initialized"}
        
        # Create the recognition audio object
        audio = speech.RecognitionAudio(uri=gcs_uri)
        
        # Configure the recognition
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        
        # Start long running operation
        operation = speech_client.long_running_recognize(config=config, audio=audio)
        
        # Wait for operation to complete
        logger.info("Waiting for long running operation to complete...")
        operation.result()  # This blocks until the operation is complete
        
        # Extract the transcript
        transcript = ""
        for result in operation.result().results:
            transcript += result.alternatives[0].transcript + " "
        
        return {"transcript": transcript.strip(), "success": True}
        
    except Exception as e:
        logger.error(f"Error transcribing long audio: {e}")
        return {"error": str(e), "success": False}

def transcribe_audio_file(audio_file_path, language_code="en-US"):
    """Transcribe audio file using Google Speech-to-Text, with MP3 fallback to WAV."""
    try:
        if not speech_client:
            return {"error": "Speech client not initialized"}
        
        # Check audio duration
        duration = get_audio_duration(audio_file_path)
        file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
        logger.info(f"Audio duration: {duration} seconds, file size: {file_size_mb:.2f} MB")
        
        # If audio is longer than 60 seconds, or duration can't be determined but file is large, use long running recognition
        if (duration and duration > 60) or (duration is None and file_size_mb > 1):
            logger.info("Audio is long or duration unknown but file is large; using long running recognition")
            
            # Upload to GCS
            gcs_uri, error = upload_to_gcs(audio_file_path)
            if error:
                return {"error": f"Failed to upload to GCS: {error}", "success": False}
            
            # Transcribe using long running recognition
            result = transcribe_long_audio(gcs_uri, language_code)
            
            # Clean up GCS file
            try:
                if storage_client:
                    bucket_name = gcs_uri.split('/')[2]
                    blob_name = '/'.join(gcs_uri.split('/')[3:])
                    bucket = storage_client.get_bucket(bucket_name)
                    blob = bucket.blob(blob_name)
                    blob.delete()
            except Exception as e:
                logger.warning(f"Failed to clean up GCS file: {e}")
            
            return result
        
        # For shorter files, use synchronous recognition
        # Read the audio file
        with open(audio_file_path, "rb") as audio_file:
            content = audio_file.read()
        
        # Detect encoding and sample rate
        encoding, sample_rate = get_audio_encoding_and_rate(audio_file_path)
        
        # Create the recognition audio object
        audio = speech.RecognitionAudio(content=content)
        
        # Configure the recognition
        config = speech.RecognitionConfig(
            encoding=encoding,
            sample_rate_hertz=sample_rate,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        
        response = None
        error_string = None
        try:
            # Try transcription with detected encoding
            response = speech_client.recognize(config=config, audio=audio)
        except Exception as e:
            error_string = str(e)
        logger.warning(f"DEBUG: response type: {type(response)}, value: {response}")
        logger.warning(f"DEBUG: error_string: {error_string}")
        # Fallback if error is MP3 or response is string 'MP3', or response is not a valid response object
        fallback_needed = False
        if (
            (error_string and (error_string.strip() == "MP3" or "MP3" in error_string)) or
            (isinstance(response, str) and (response.strip() == "MP3" or "MP3" in response)) or
            (response is None)
        ):
            fallback_needed = True
        # If response is a valid object but has no results, also fallback
        if hasattr(response, 'results') and (not response.results or len(response.results) == 0):
            logger.warning("DEBUG: Response object has no results, forcing fallback to WAV.")
            fallback_needed = True
        if fallback_needed:
            logger.warning(f"MP3 transcription failed ({error_string or response}), converting to WAV and retrying...")
            wav_path = audio_file_path + ".converted.wav"
            sound = AudioSegment.from_mp3(audio_file_path)
            sound = sound.set_frame_rate(16000).set_channels(1)
            sound.export(wav_path, format="wav")
            with open(wav_path, "rb") as wav_file:
                wav_content = wav_file.read()
            audio = speech.RecognitionAudio(content=wav_content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
                enable_automatic_punctuation=True,
            )
            try:
                response = speech_client.recognize(config=config, audio=audio)
            except Exception as e2:
                logger.error(f"WAV fallback also failed: {e2}")
                os.remove(wav_path)
                return {"error": f"WAV fallback failed: {e2}", "success": False}
            os.remove(wav_path)
        elif error_string:
            # If there was an error but not MP3, return it
            logger.error(f"Error transcribing audio: {error_string}")
            return {"error": error_string, "success": False}
        # Extract the transcript
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "
        
        return {"transcript": transcript.strip(), "success": True}
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return {"error": str(e), "success": False}

def transcribe_gcs_audio(gcs_uri, language_code="en-US"):
    """Transcribe audio from Google Cloud Storage"""
    try:
        if not speech_client:
            return {"error": "Speech client not initialized"}
        
        # Create the recognition audio object
        audio = speech.RecognitionAudio(uri=gcs_uri)
        
        # Configure the recognition
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            enable_automatic_punctuation=True,
        )
        
        # Perform the transcription
        response = speech_client.recognize(config=config, audio=audio)
        
        # Extract the transcript
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript + " "
        
        return {"transcript": transcript.strip(), "success": True}
        
    except Exception as e:
        logger.error(f"Error transcribing GCS audio: {e}")
        return {"error": str(e), "success": False}

@app.route('/')
def index():
    """Main page with upload form"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Google Speech-to-Text Service</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 8px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007cba; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #005a87; }
            .result { margin-top: 20px; padding: 15px; background: white; border-radius: 4px; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>Google Speech-to-Text Service</h1>
        
        <div class="container">
            <h2>Upload Audio File</h2>
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
                <button type="submit">Transcribe Audio</button>
            </form>
        </div>
        
        <div class="container">
            <h2>Test with Sample Audio</h2>
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
                <button type="submit">Test with Sample Audio</button>
            </form>
        </div>
        
        <div class="container">
            <h2>API Endpoints</h2>
            <p><strong>POST /transcribe</strong> - Upload and transcribe audio file</p>
            <p><strong>POST /test</strong> - Test with sample audio from Google Cloud Storage</p>
            <p><strong>GET /health</strong> - Health check</p>
        </div>
    </body>
    </html>
    """
    return html

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Handle audio file upload and transcription"""
    try:
        if 'audio_file' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        file = request.files['audio_file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        language_code = request.form.get('language', 'en-US')
        
        # Use the original file extension for temp file
        ext = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        # Transcribe the audio
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
    """Test with sample audio from Google Cloud Storage"""
    try:
        language_code = request.form.get('language', 'en-US')
        
        # Use the sample audio from Google Cloud Storage
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
        "speech_client_initialized": speech_client is not None,
        "storage_client_initialized": storage_client is not None
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 