# UpFlow 🚀  
**Production-Grade Resumable File Upload Backend**

UpFlow is a backend system that supports **resumable, chunked file uploads** with **server-side validation**, **asynchronous assembly**, and **real AWS S3 storage**.

---

## ✨ Key Features

- ✅ Chunked uploads for large files
- ✅ Upload interruption & resume
- ✅ Server-side tracking of upload state
- ✅ Idempotent chunk uploads
- ✅ Explicit upload lifecycle
- ✅ Background file assembly
- ✅ Real AWS S3 (no mocks)
- ✅ Dockerized local environment
- ✅ Minimal demo UI (HTML + JS)

---

## 🧠 Architecture Overview

UpFlow separates responsibilities cleanly:

- **API (FastAPI)**  
  Handles upload lifecycle, validation, and scheduling background work.

- **Database (PostgreSQL)**  
  Stores upload session metadata and acts as the source of truth.

- **Background Workers (Celery + Redis)**  
  Assemble uploaded chunks asynchronously and upload final files to S3.

- **Storage (AWS S3)**  
  Temporarily stores chunks and permanently stores final assembled files.

---

## 🔁 Upload Lifecycle

Each upload follows a strict and explicit state machine:

```
initialized
   ↓
uploading
   ↓
pending_assembly
   ↓
completed
```

The database is the **single source of truth** for upload state.

---

## 📦 Upload Flow

1. **Initialize upload**
   ```http
   POST /uploads/init
   ```

2. **Upload chunks (idempotent)**
   ```http
   PUT /uploads/{upload_id}/chunks/{chunk_index}
   ```

3. **Complete upload**
   ```http
   POST /uploads/{upload_id}/complete
   ```

4. **Background worker assembles file**
   - Downloads chunks from S3
   - Concatenates them in order
   - Uploads final file to S3
   - Cleans up chunk objects
   - Marks upload as `completed`

---

## 🗂️ S3 Object Layout

```text
uploads/
  └── {upload_id}/
       ├── chunks/
       │    ├── 0
       │    ├── 1
       │    └── ...
       └── final/
            └── original_filename.ext
```

---

## 🧾 Database Schema

### `upload_sessions`

| Column          | Type      | Description |
|-----------------|-----------|-------------|
| upload_id       | UUID (PK) | Unique upload identifier |
| filename        | string    | Original filename |
| total_chunks    | int       | Expected number of chunks |
| chunk_size      | int       | Size of each chunk |
| uploaded_chunks | JSON      | List of uploaded chunk indices |
| status          | string    | Upload lifecycle state |
| final_s3_key    | string    | S3 key of final assembled file |
| created_at      | timestamp | Created time |
| updated_at      | timestamp | Updated time |

All schema changes are managed via **Alembic migrations**.

---

## 🧑‍🏫 Why Client-Side Chunking?

UpFlow uses **client-side chunking**, which is the industry standard for resumable uploads.

**Why?**
- Network failures affect only a single chunk
- Uploads can resume without restarting
- Server never needs to accept large request bodies
- Scales conceptually to GB-size files

---

## 🧪 Demo UI

Available at:

```
http://localhost:8000/static/index.html
```

Allows:
- File selection
- Chunked upload
- Resume after refresh
- Status polling

---

## 🐳 Local Development (Docker)

### Requirements
- Docker
- Docker Compose
- AWS account with an S3 bucket

### Environment Variables

Create a `.env` file (not committed to git):

```env
APP_ENV=local
APP_NAME=UpFlow

DATABASE_URL=postgresql+psycopg2://upflow:upflow@db:5432/upflow

AWS_REGION=your-region
AWS_S3_BUCKET=your-bucket-name
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

REDIS_HOST=redis
REDIS_PORT=6379
```

### Start Services

```bash
docker compose up -d --build
```

---

## 📜 License

MIT
