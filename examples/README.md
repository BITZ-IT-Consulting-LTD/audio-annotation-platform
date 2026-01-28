# Examples

This directory contains example configurations and client implementations for the Audio Annotation Platform.

## Configuration Examples

### `middleware-config.env`
Example configuration file for the middleware service. Copy to `/opt/ls-middleware/config.env` and update with your values:

```bash
cp examples/middleware-config.env /opt/ls-middleware/config.env
# Edit the file with your actual values
nano /opt/ls-middleware/config.env
```

Key settings to update:
- `LABEL_STUDIO_API_KEY`: Get from Label Studio Account & Settings → API
- `POSTGRES_PASSWORD`: Must match Label Studio PostgreSQL password
- `TZ_SYSTEM_API_KEY`: Generate with `openssl rand -hex 32`

### `label-studio.env`
Example Label Studio environment configuration. The `setup.sh` script will create this for you, but you can also manually configure:

```bash
cp examples/label-studio.env /opt/label-studio/.env
# Edit with your values
nano /opt/label-studio/.env
```

Important settings:
- `LABEL_STUDIO_HOST`: **Must** be your public IP or domain (not localhost for remote access)
- `POSTGRES_PASSWORD`: Generate a secure password
- `SECRET_KEY`: Generate with `openssl rand -hex 50`

## Client Examples

### `client_example.py`
Complete Python client demonstrating the full workflow:

```bash
# Install dependencies
pip install requests

# Set environment variables
export API_KEY="your_api_key_here"
export BASE_URL="http://localhost:8010"
export AGENT_ID="123"

# Run the example
python examples/client_example.py
```

Features demonstrated:
- Health check
- Task request
- Audio download
- Transcription submission
- Skip functionality
- Agent statistics

### Implementing Your Own Client

Use `client_example.py` as a template:

1. Replace the `mock_transcribe_audio()` function with your actual ASR implementation
2. Add quality checks to decide when to skip tasks
3. Implement error handling for your use case
4. Add retry logic if needed

Example integration with popular ASR libraries:

```python
# Using Whisper
import whisper

def transcribe_audio(audio_path: str) -> str:
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

# Using Google Speech-to-Text
from google.cloud import speech_v1

def transcribe_audio(audio_path: str) -> str:
    client = speech_v1.SpeechClient()

    with open(audio_path, "rb") as f:
        audio = speech_v1.RecognitionAudio(content=f.read())

    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)
    return " ".join(result.alternatives[0].transcript
                   for result in response.results)

# Using Azure Speech Service
import azure.cognitiveservices.speech as speechsdk

def transcribe_audio(audio_path: str) -> str:
    speech_config = speechsdk.SpeechConfig(
        subscription="YOUR_KEY",
        region="YOUR_REGION"
    )
    audio_config = speechsdk.AudioConfig(filename=audio_path)

    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    result = recognizer.recognize_once()
    return result.text
```

## Browser Testing

The repository includes a browser-based testing interface:

```bash
# Open in browser
firefox middleware/web/transcription_frontend_template.html

# Or Chrome
google-chrome middleware/web/transcription_frontend_template.html
```

Update the `serverUrl` in the HTML file to point to your middleware instance.

## Docker Compose Example

For running the entire stack with Docker Compose, see `label-studio/docker-compose.yml`.

To run Label Studio:

```bash
cd label-studio
./setup.sh  # First time only
docker compose up -d
```

## Testing Workflow

Complete end-to-end testing:

```bash
# 1. Start services
cd label-studio && docker compose up -d
sudo systemctl start ls-middleware

# 2. Import test audio
cd audio-import
source venv/bin/activate
python import_audio.py /path/to/test/audio

# 3. Test client
export API_KEY="your_key"
python examples/client_example.py

# 4. Verify in Label Studio
# Visit http://your-ip:8080 and check annotations
```

## API Testing with cURL

Quick API tests without writing code:

```bash
API_KEY="your_key"
BASE_URL="http://localhost:8010"

# Health check
curl -H "X-API-Key: $API_KEY" $BASE_URL/api/health

# Request task
curl -X POST $BASE_URL/api/tasks/request \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": 123}'

# Get available task count
curl -H "X-API-Key: $API_KEY" \
  "$BASE_URL/api/tasks/available/count?agent_id=123"

# Get agent stats
curl -H "X-API-Key: $API_KEY" \
  $BASE_URL/api/agents/123/stats
```

## Need More Help?

- Read the [API Reference](../docs/API_REFERENCE.md)
- Check the [Architecture Documentation](../docs/ARCHITECTURE.md)
- See the main [README](../README.md) for setup instructions
- Open an issue on GitHub for questions
