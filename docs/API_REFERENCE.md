# API Reference

## Authentication

All API endpoints require authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:8010/api/health
```

The API key is configured in the middleware's `config.env` file as `TZ_SYSTEM_API_KEY`.

## Endpoints

### Health Check

**GET** `/api/health`

Check system health and connectivity.

**Response:**
```json
{
  "status": "healthy",
  "label_studio": "connected",
  "redis": "connected",
  "project_id": 1,
  "postgres": "connected"
}
```

**Status Codes:**
- `200 OK`: System healthy
- `500 Internal Server Error`: Component failure

---

### Request Task

**POST** `/api/tasks/request`

Request the next available task for an agent.

**Request Body:**
```json
{
  "agent_id": 123
}
```

**Response (Success):**
```json
{
  "task_id": 456,
  "audio_url": "http://localhost:8010/api/audio/stream/456/123",
  "duration": 12.5,
  "file_name": "audio_abc123.wav"
}
```

**Response (No Tasks):**
```json
{
  "task_id": null,
  "message": "No tasks available"
}
```

**Status Codes:**
- `200 OK`: Task assigned or no tasks available
- `401 Unauthorized`: Invalid API key
- `500 Internal Server Error`: Server error

**Notes:**
- Automatically checks skip cooldowns
- Skips tasks the agent has skipped in the last 30 minutes
- Creates Redis lock for assigned task
- Logs assignment to database

---

### Stream Audio

**GET** `/api/audio/stream/{task_id}/{agent_id}`

Stream audio file for a specific task.

**Path Parameters:**
- `task_id`: Integer task ID
- `agent_id`: Integer agent ID

**Headers (Optional):**
- `Range`: Byte range for partial content (e.g., `bytes=0-1023`)

**Response:**
- Audio file stream with appropriate MIME type
- Supports range requests for seeking

**Status Codes:**
- `200 OK`: Full file
- `206 Partial Content`: Range request
- `401 Unauthorized`: Invalid API key
- `403 Forbidden`: Task not assigned to agent
- `404 Not Found`: Audio file not found
- `500 Internal Server Error`: Server error

**Example:**
```bash
curl -H "X-API-Key: your_key" \
  http://localhost:8010/api/audio/stream/456/123 \
  --output audio.wav
```

---

### Submit Transcription

**POST** `/api/tasks/{task_id}/submit`

Submit transcription for a task.

**Path Parameters:**
- `task_id`: Integer task ID

**Request Body:**
```json
{
  "agent_id": 123,
  "transcription": "The transcribed text here"
}
```

**Response:**
```json
{
  "status": "success",
  "annotation_id": 789
}
```

**Status Codes:**
- `200 OK`: Transcription submitted successfully
- `400 Bad Request`: Invalid request (missing fields, wrong agent)
- `401 Unauthorized`: Invalid API key
- `404 Not Found`: Task not found
- `500 Internal Server Error`: Server error

**Notes:**
- Validates agent owns the task lock
- Creates Label Studio annotation
- Updates agent statistics
- Releases task lock
- Removes task from assignment queue

---

### Skip Task

**POST** `/api/tasks/{task_id}/skip`

Skip a task (e.g., poor audio quality, unable to transcribe).

**Path Parameters:**
- `task_id`: Integer task ID

**Request Body:**
```json
{
  "agent_id": 123,
  "reason": "Audio quality too poor to transcribe"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Task skipped and released"
}
```

**Status Codes:**
- `200 OK`: Task skipped successfully
- `400 Bad Request`: Invalid request
- `401 Unauthorized`: Invalid API key
- `403 Forbidden`: Task not assigned to agent
- `500 Internal Server Error`: Server error

**Notes:**
- Releases task lock
- Sets 30-minute cooldown for this agent+task combination
- Logs skip reason to database
- Task remains available for other agents

---

### Get Available Task Count

**GET** `/api/tasks/available/count`

Get count of available tasks, optionally filtered by agent.

**Query Parameters:**
- `agent_id` (optional): Integer agent ID to exclude their skipped tasks

**Response:**
```json
{
  "available": 42,
  "total_unlabeled": 50,
  "total_locked": 8
}
```

**Status Codes:**
- `200 OK`: Success
- `401 Unauthorized`: Invalid API key

**Notes:**
- Stats updated every 30 seconds (eventual consistency)
- When `agent_id` provided, excludes tasks in that agent's skip cooldown

---

### Get Agent Statistics

**GET** `/api/agents/{agent_id}/stats`

Get detailed statistics for a specific agent.

**Path Parameters:**
- `agent_id`: Integer agent ID

**Response:**
```json
{
  "agent_id": 123,
  "total_tasks_completed": 150,
  "total_tasks_skipped": 5,
  "total_duration_seconds": 1250.5,
  "total_earnings": 62.53,
  "last_active": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

**Status Codes:**
- `200 OK`: Success (returns zeros if agent not found)
- `401 Unauthorized`: Invalid API key
- `500 Internal Server Error`: Server error

---

### Get System Statistics

**GET** `/api/stats`

Get overall system statistics.

**Response:**
```json
{
  "total_unlabeled": 50,
  "total_locked": 8,
  "available": 42,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

**Status Codes:**
- `200 OK`: Success
- `401 Unauthorized`: Invalid API key

**Notes:**
- Stats cached and updated every 30 seconds
- May have slight delay from actual state

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message here"
}
```

Common error scenarios:

### 401 Unauthorized
```json
{
  "detail": "Invalid API key"
}
```

### 403 Forbidden
```json
{
  "detail": "Task not assigned to this agent"
}
```

### 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: <details>"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. Consider implementing if needed for production use.

## CORS

CORS is enabled for all origins. Configure in production as needed:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Webhooks

No webhook support currently. Submit feature request if needed.

## Client Examples

### Python

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "http://localhost:8010"
AGENT_ID = 123

headers = {"X-API-Key": API_KEY}

# Request task
response = requests.post(
    f"{BASE_URL}/api/tasks/request",
    json={"agent_id": AGENT_ID},
    headers=headers
)
task = response.json()

if task["task_id"]:
    # Download audio
    audio_response = requests.get(
        task["audio_url"],
        headers=headers
    )

    # Process audio...
    transcription = "The transcribed text"

    # Submit transcription
    requests.post(
        f"{BASE_URL}/api/tasks/{task['task_id']}/submit",
        json={
            "agent_id": AGENT_ID,
            "transcription": transcription
        },
        headers=headers
    )
```

### cURL

```bash
# Request task
curl -X POST http://localhost:8010/api/tasks/request \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": 123}'

# Download audio
curl -H "X-API-Key: your_key" \
  http://localhost:8010/api/audio/stream/456/123 \
  -o audio.wav

# Submit transcription
curl -X POST http://localhost:8010/api/tasks/456/submit \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": 123, "transcription": "The text"}'

# Skip task
curl -X POST http://localhost:8010/api/tasks/456/skip \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": 123, "reason": "Poor audio quality"}'
```

### JavaScript/Fetch

```javascript
const API_KEY = "your_api_key";
const BASE_URL = "http://localhost:8010";
const AGENT_ID = 123;

// Request task
const response = await fetch(`${BASE_URL}/api/tasks/request`, {
  method: "POST",
  headers: {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ agent_id: AGENT_ID })
});

const task = await response.json();

if (task.task_id) {
  // Download audio
  const audioResponse = await fetch(task.audio_url, {
    headers: { "X-API-Key": API_KEY }
  });
  const audioBlob = await audioResponse.blob();

  // Process audio...
  const transcription = "The transcribed text";

  // Submit
  await fetch(`${BASE_URL}/api/tasks/${task.task_id}/submit`, {
    method: "POST",
    headers: {
      "X-API-Key": API_KEY,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      agent_id: AGENT_ID,
      transcription: transcription
    })
  });
}
```
