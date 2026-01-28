# Architecture Documentation

## System Overview

The Audio Annotation Platform is a distributed system for managing audio transcription workflows. It bridges Label Studio (annotation platform) with external transcription agents through a FastAPI middleware layer.

## Components

### 1. Label Studio (Port 8080)
- **Technology**: Docker container with PostgreSQL backend
- **Purpose**: Web-based annotation platform and task management
- **Storage**: Audio files stored in `/opt/label-studio/media/project_X/`
- **Database**: PostgreSQL for tasks, annotations, and user management

### 2. Middleware (Port 8010)
- **Technology**: FastAPI with async Redis and PostgreSQL
- **Purpose**: Task distribution, audio streaming, and transcription collection
- **Key Features**:
  - Direct filesystem audio streaming (no proxying)
  - Redis-based task locking with skip cooldowns
  - Dual-layer caching for performance
  - Agent statistics tracking

### 3. Audio Import System
- **Technology**: Python scripts with librosa
- **Purpose**: Batch import audio files with metadata extraction
- **Features**: Duration calculation, hash-based deduplication, permission management

## Data Flow

```
┌─────────────────┐
│  Audio Files    │
└────────┬────────┘
         │ import_audio.py
         ↓
┌─────────────────────────────────────┐
│  Label Studio                       │
│  - Creates tasks                    │
│  - Stores metadata                  │
└────────┬───────────────────────────┘
         │ API queries
         ↓
┌─────────────────────────────────────┐
│  Middleware Assignment Queue        │
│  - Syncs unlabeled tasks (30s)      │
│  - Maintains Redis queue            │
│  - Tracks completed tasks           │
└────────┬───────────────────────────┘
         │ Task request
         ↓
┌─────────────────────────────────────┐
│  Task Locking System                │
│  - Checks skip cooldowns            │
│  - Creates Redis lock               │
│  - Logs to PostgreSQL               │
└────────┬───────────────────────────┘
         │ Audio streaming
         ↓
┌─────────────────────────────────────┐
│  Direct File Serving                │
│  - Validates agent access           │
│  - Serves from filesystem           │
│  - Supports HTTP range requests     │
└────────┬───────────────────────────┘
         │ Transcription submission
         ↓
┌─────────────────────────────────────┐
│  Completion Handler                 │
│  - Creates Label Studio annotation  │
│  - Updates agent stats              │
│  - Releases Redis lock              │
│  - Removes from queue               │
└─────────────────────────────────────┘
```

## Assignment Queue Architecture

The middleware uses a **dual-layer cache** for optimal performance:

### Layer 1: Redis Queue
- **Key**: `assignment_queue` (Redis list)
- **Content**: Task IDs of unlabeled tasks
- **Sync**: Every 30 seconds from Label Studio API
- **Purpose**: Fast O(1) task popping for assignment

### Layer 2: In-Memory Stats Cache
- **total_unlabeled**: Count of tasks in queue
- **total_locked**: Count of currently locked tasks
- **available**: Unlabeled minus locked
- **Purpose**: Dashboard stats without Redis overhead

### Completed Tasks Tracking
- **Memory set**: `assignment_queue["completed_tasks"]`
- **Purpose**: Prevents re-adding completed tasks during sync
- **Lifecycle**: Persists for session duration

## Task Locking System

### Lock Types

1. **Task Lock** (`task:locked:{task_id}`)
   - **Value**: `{agent_id}:{timestamp}`
   - **TTL**: 1 hour (prevents orphaned locks)
   - **Purpose**: Ensures one agent per task

2. **Skip Cooldown** (`task:skip:{task_id}:{agent_id}`)
   - **Value**: `1`
   - **TTL**: 30 minutes
   - **Purpose**: Prevents agents from repeatedly skipping same task

### Lock Flow

```python
# Assignment
1. Check skip cooldown for agent+task
2. Find first unlocked task in queue
3. Create task lock with agent ID
4. Log to transcription_sessions table
5. Return task to agent

# Skip
1. Release task lock
2. Create skip cooldown (30 min)
3. Log skip reason to database
4. Keep task in queue for other agents

# Completion
1. Create Label Studio annotation
2. Update agent stats (duration, earnings)
3. Release task lock
4. Remove task from queue permanently
5. Add to completed_tasks set
```

## Database Schema

### PostgreSQL Tables

#### `transcription_sessions`
Tracks individual transcription sessions for audit and analytics.

```sql
- id (PK, auto-increment)
- agent_id (indexed)
- task_id (indexed)
- assigned_at (timestamp)
- completed_at (timestamp, nullable)
- duration_seconds (float, nullable)
- status (assigned|completed|skipped)
- transcription_length (int, nullable)
- skip_reason (text, nullable)
```

#### `agent_stats`
Cumulative statistics per agent.

```sql
- agent_id (PK)
- total_duration_seconds (float)
- total_tasks_completed (int)
- total_tasks_skipped (int)
- total_earnings (float)
- last_active (timestamp)
- created_at (timestamp)
- updated_at (timestamp)
```

## Storage Architecture

```
/opt/label-studio/
├── data/              # Label Studio internal data
│   ├── media/         # Audio files (symlinked to ../media)
│   ├── export/        # Exports
│   └── test_data/     # Test files
├── media/             # Actual audio storage
│   └── project_1/     # Project-specific files
│       └── *.wav      # Audio files with hash-based names
├── export/            # Shared export directory
└── backups/           # PostgreSQL backups

Permissions:
- Container user: 1001:1001 (Label Studio)
- Middleware: Reads from media/ as deploy user
```

## Performance Optimizations

### 1. Direct File Serving
- **No proxy overhead**: Files served via FastAPI FileResponse
- **Range request support**: Enables audio seeking in browsers
- **Efficient**: Uses sendfile() system call when available

### 2. Assignment Queue Caching
- **Reduces API calls**: 30-second sync instead of per-request
- **Fast assignment**: O(1) Redis LPOP operation
- **Eventual consistency**: Stats may lag by up to 30 seconds

### 3. Async Architecture
- **Non-blocking I/O**: Redis and database operations are async
- **High concurrency**: Handles many simultaneous agent connections
- **Background sync**: Assignment queue syncs in separate task

## Security Model

### Authentication
- **Agent API Key**: `X-API-Key` header validated against `TZ_SYSTEM_API_KEY`
- **Label Studio API**: Token-based authentication for SDK calls

### Authorization
- **Task access**: Agents can only access tasks they've been assigned
- **Audio streaming**: Verified via Redis lock check before serving
- **File system**: Direct path traversal prevention

### Audit Trail
- All task assignments logged to `transcription_sessions`
- Skip actions logged with reasons
- Agent activity tracked with timestamps

## Scalability Considerations

### Current Limits
- Single Redis instance (can cluster if needed)
- Single PostgreSQL instance (can add read replicas)
- File system storage (can move to S3/object storage)

### Horizontal Scaling
- Multiple middleware instances can share Redis/PostgreSQL
- Assignment queue locking prevents double-assignment
- Stateless design enables load balancing

### Bottlenecks
1. **Label Studio API**: 30-second sync interval mitigates
2. **File I/O**: Direct serving is efficient, can add CDN
3. **Redis**: Single-threaded but fast, can cluster for high load
