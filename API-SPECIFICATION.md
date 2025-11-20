# API Specification - Research Automation Tool

**Version:** 1.0
**Base URL:** `https://api.yourapp.com/v1`
**Authentication:** JWT Bearer Token
**Last Updated:** November 18, 2025

---

## Table of Contents

1. [Authentication](#authentication)
2. [Projects](#projects)
3. [Documents](#documents)
4. [Schema (Conversation)](#schema-conversation)
5. [Extraction](#extraction)
6. [Export](#export)
7. [WebSocket Events](#websocket-events)
8. [Error Handling](#error-handling)

---

## Authentication

### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-01-15T10:30:00Z",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe"
  }
}
```

---

### Get Current User

```http
GET /auth/me
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

## Projects

### List Projects

```http
GET /projects
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "projects": [
    {
      "id": "uuid",
      "name": "Climate Protests Study",
      "description": "Analyzing climate protests in Europe 2023-2024",
      "status": "draft",
      "document_count": 127,
      "created_at": "2025-01-10T08:00:00Z",
      "updated_at": "2025-01-15T14:30:00Z"
    }
  ],
  "total": 1
}
```

---

### Create Project

```http
POST /projects
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Climate Protests Study",
  "description": "Analyzing climate protests in Europe 2023-2024"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "name": "Climate Protests Study",
  "description": "Analyzing climate protests in Europe 2023-2024",
  "status": "draft",
  "document_count": 0,
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

---

### Get Project

```http
GET /projects/{project_id}
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "name": "Climate Protests Study",
  "description": "Analyzing climate protests in Europe 2023-2024",
  "status": "draft",
  "document_count": 127,
  "schema_status": "completed",
  "extraction_status": null,
  "created_at": "2025-01-10T08:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z"
}
```

---

### Update Project

```http
PATCH /projects/{project_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Project Name",
  "description": "Updated description"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "draft",
  "updated_at": "2025-01-15T15:00:00Z"
}
```

---

### Delete Project

```http
DELETE /projects/{project_id}
Authorization: Bearer {token}
```

**Response (204 No Content)**

---

## Documents

### Upload Documents

```http
POST /projects/{project_id}/documents
Authorization: Bearer {token}
Content-Type: multipart/form-data

files: [File, File, ...]
```

**Response (201 Created):**
```json
{
  "uploaded": [
    {
      "id": "uuid",
      "filename": "protest_article_01.pdf",
      "file_type": "pdf",
      "size_bytes": 245632,
      "status": "parsing",
      "uploaded_at": "2025-01-15T10:30:00Z"
    }
  ],
  "failed": []
}
```

---

### List Documents

```http
GET /projects/{project_id}/documents
Authorization: Bearer {token}

Query Parameters:
  - status: uploaded|parsed|processing|completed|error
  - page: 1
  - limit: 50
```

**Response (200 OK):**
```json
{
  "documents": [
    {
      "id": "uuid",
      "filename": "protest_article_01.pdf",
      "file_type": "pdf",
      "size_bytes": 245632,
      "status": "parsed",
      "uploaded_at": "2025-01-15T10:30:00Z",
      "parsed_at": "2025-01-15T10:30:15Z"
    }
  ],
  "total": 127,
  "page": 1,
  "limit": 50
}
```

---

### Get Document

```http
GET /projects/{project_id}/documents/{document_id}
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "filename": "protest_article_01.pdf",
  "file_type": "pdf",
  "size_bytes": 245632,
  "status": "parsed",
  "content_preview": "First 500 characters of parsed text...",
  "word_count": 1250,
  "uploaded_at": "2025-01-15T10:30:00Z",
  "parsed_at": "2025-01-15T10:30:15Z"
}
```

---

### Get Document Content

```http
GET /projects/{project_id}/documents/{document_id}/content
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "filename": "protest_article_01.pdf",
  "content": "Full parsed text content of the document..."
}
```

---

### Delete Document

```http
DELETE /projects/{project_id}/documents/{document_id}
Authorization: Bearer {token}
```

**Response (204 No Content)**

---

### Delete Multiple Documents

```http
DELETE /projects/{project_id}/documents
Authorization: Bearer {token}
Content-Type: application/json

{
  "document_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response (200 OK):**
```json
{
  "deleted": 3,
  "failed": []
}
```

---

## Schema (Conversation)

### Start Conversation

```http
POST /projects/{project_id}/schema/conversation
Authorization: Bearer {token}
```

**Response (201 Created):**
```json
{
  "conversation_id": "uuid",
  "message": {
    "id": "uuid",
    "role": "assistant",
    "content": "Hello! I'll help you define what data to extract from your documents. What is your research about? What are you trying to understand?",
    "timestamp": "2025-01-15T10:00:00Z",
    "metadata": {
      "suggestions": [
        "I'm studying political events",
        "I'm analyzing social movements",
        "I'm researching policy changes"
      ]
    }
  }
}
```

---

### Send Message

```http
POST /projects/{project_id}/schema/conversation/messages
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "I'm studying climate protests in Europe"
}
```

**Response (200 OK):**
```json
{
  "user_message": {
    "id": "uuid",
    "role": "user",
    "content": "I'm studying climate protests in Europe",
    "timestamp": "2025-01-15T10:01:00Z"
  },
  "assistant_message": {
    "id": "uuid",
    "role": "assistant",
    "content": "Great! Climate protests in Europe. What specific information do you need to extract from your documents? For example: dates, locations, participants, demands, outcomes?",
    "timestamp": "2025-01-15T10:01:02Z",
    "metadata": {
      "extracted_context": {
        "research_domain": "social_movements",
        "topic": "climate_protests",
        "region": "europe"
      }
    }
  }
}
```

---

### Get Conversation History

```http
GET /projects/{project_id}/schema/conversation
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "conversation_id": "uuid",
  "messages": [
    {
      "id": "uuid",
      "role": "assistant",
      "content": "Hello! What is your research about?",
      "timestamp": "2025-01-15T10:00:00Z"
    },
    {
      "id": "uuid",
      "role": "user",
      "content": "I'm studying climate protests",
      "timestamp": "2025-01-15T10:01:00Z"
    }
  ],
  "schema_draft": {
    "research_context": {
      "domain": "social_movements",
      "topic": "climate_protests"
    },
    "variables": [
      {
        "name": "date",
        "type": "date",
        "description": "Date of the protest",
        "status": "confirmed"
      }
    ],
    "classifications": []
  }
}
```

---

### Get Generated Schema

```http
GET /projects/{project_id}/schema
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "status": "draft",
  "version": 1,
  "research_context": {
    "domain": "social_movements",
    "topic": "climate_protests",
    "region": "europe"
  },
  "variables": [
    {
      "name": "date",
      "type": "date",
      "description": "Date when the protest occurred",
      "required": true,
      "extraction_prompt": "Extract the date when this protest took place..."
    },
    {
      "name": "location",
      "type": "string",
      "description": "City or location where protest happened",
      "required": true,
      "extraction_prompt": "Extract the specific location (city/region)..."
    },
    {
      "name": "participants",
      "type": "integer",
      "description": "Estimated number of participants",
      "required": false,
      "extraction_prompt": "Extract the estimated number of people who participated..."
    }
  ],
  "classifications": [
    {
      "name": "protest_type",
      "type": "categorical",
      "categories": ["Climate policy", "Fossil fuels", "Deforestation", "General environmental"],
      "description": "Primary focus of the protest",
      "classification_prompt": "Classify the main topic of this protest..."
    },
    {
      "name": "violence",
      "type": "binary",
      "categories": ["Yes", "No"],
      "description": "Whether the protest involved violence (physical confrontation or property damage)",
      "classification_prompt": "Determine if this protest involved violence..."
    }
  ],
  "created_at": "2025-01-15T10:15:00Z",
  "updated_at": "2025-01-15T10:15:00Z"
}
```

---

### Approve Schema

```http
POST /projects/{project_id}/schema/approve
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "status": "approved",
  "version": 1,
  "approved_at": "2025-01-15T10:20:00Z"
}
```

---

## Extraction

### Start Sample Extraction (Test)

```http
POST /projects/{project_id}/extraction/sample
Authorization: Bearer {token}
Content-Type: application/json

{
  "sample_size": 10,
  "random_selection": true
}
```

**Response (202 Accepted):**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "sample_size": 10,
  "estimated_duration_seconds": 120,
  "created_at": "2025-01-15T10:25:00Z"
}
```

---

### Start Full Extraction

```http
POST /projects/{project_id}/extraction/full
Authorization: Bearer {token}
```

**Response (202 Accepted):**
```json
{
  "job_id": "uuid",
  "status": "queued",
  "total_documents": 127,
  "estimated_duration_seconds": 1800,
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### Get Extraction Job Status

```http
GET /projects/{project_id}/extraction/jobs/{job_id}
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": {
    "completed": 45,
    "total": 127,
    "percentage": 35.4,
    "current_document": "protest_article_046.pdf"
  },
  "started_at": "2025-01-15T10:30:15Z",
  "estimated_completion": "2025-01-15T11:00:00Z",
  "errors": []
}
```

**Possible status values:**
- `queued` - Job waiting to start
- `processing` - Currently extracting data
- `completed` - Finished successfully
- `failed` - Job failed
- `cancelled` - User cancelled

---

### Get Extraction Results

```http
GET /projects/{project_id}/extraction/results
Authorization: Bearer {token}

Query Parameters:
  - confidence_min: 0.0-1.0 (filter by confidence)
  - flagged_only: true|false
  - page: 1
  - limit: 50
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": "uuid",
      "document_id": "uuid",
      "document_name": "protest_article_01.pdf",
      "extracted_data": {
        "date": {
          "value": "2024-03-15",
          "confidence": 0.95,
          "source_text": "The protest took place on March 15, 2024"
        },
        "location": {
          "value": "Berlin",
          "confidence": 0.98,
          "source_text": "thousands gathered in Berlin"
        },
        "participants": {
          "value": 5000,
          "confidence": 0.72,
          "source_text": "approximately 5,000 people"
        },
        "protest_type": {
          "value": "Climate policy",
          "confidence": 0.89,
          "source_text": null
        },
        "violence": {
          "value": "No",
          "confidence": 0.96,
          "source_text": null
        }
      },
      "flagged": false,
      "low_confidence_fields": ["participants"],
      "extracted_at": "2025-01-15T10:45:23Z"
    }
  ],
  "total": 127,
  "page": 1,
  "limit": 50,
  "statistics": {
    "average_confidence": 0.87,
    "flagged_count": 12,
    "low_confidence_count": 23
  }
}
```

---

### Flag Result for Review

```http
POST /projects/{project_id}/extraction/results/{result_id}/flag
Authorization: Bearer {token}
Content-Type: application/json

{
  "reason": "Date seems incorrect",
  "field": "date"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "flagged": true,
  "flag_reason": "Date seems incorrect",
  "flagged_field": "date",
  "flagged_at": "2025-01-15T11:00:00Z"
}
```

---

### Unflag Result

```http
DELETE /projects/{project_id}/extraction/results/{result_id}/flag
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "flagged": false
}
```

---

## Export

### Export to CSV

```http
POST /projects/{project_id}/export
Authorization: Bearer {token}
Content-Type: application/json

{
  "format": "csv",
  "structure": "wide",
  "include_confidence": true,
  "include_source_text": false,
  "filters": {
    "confidence_min": 0.7,
    "exclude_flagged": false
  }
}
```

**Structure options:**
- `wide` - One row per document (default)
- `long` - One row per extracted field

**Response (200 OK):**
```json
{
  "export_id": "uuid",
  "status": "processing",
  "format": "csv",
  "estimated_duration_seconds": 30,
  "created_at": "2025-01-15T11:05:00Z"
}
```

---

### Get Export Status

```http
GET /projects/{project_id}/exports/{export_id}
Authorization: Bearer {token}
```

**Response (200 OK):**
```json
{
  "export_id": "uuid",
  "status": "completed",
  "format": "csv",
  "download_url": "https://api.yourapp.com/v1/projects/{project_id}/exports/{export_id}/download",
  "file_size_bytes": 156789,
  "expires_at": "2025-01-16T11:05:00Z",
  "created_at": "2025-01-15T11:05:00Z",
  "completed_at": "2025-01-15T11:05:25Z"
}
```

---

### Download Export

```http
GET /projects/{project_id}/exports/{export_id}/download
Authorization: Bearer {token}
```

**Response (200 OK):**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="climate_protests_export_20250115.csv"

document_name,date,date_confidence,location,location_confidence,...
protest_article_01.pdf,2024-03-15,0.95,Berlin,0.98,...
protest_article_02.pdf,2024-03-20,0.88,Paris,0.96,...
```

---

## WebSocket Events

### Connect to WebSocket

```javascript
const socket = io('wss://api.yourapp.com', {
  auth: { token: 'your_jwt_token' }
});
```

---

### Subscribe to Job Updates

**Client → Server:**
```javascript
socket.emit('subscribe:job', { job_id: 'uuid' });
```

**Server → Client (Processing Updates):**
```javascript
socket.on('job:progress', (data) => {
  console.log(data);
  /*
  {
    job_id: "uuid",
    status: "processing",
    progress: {
      completed: 45,
      total: 127,
      percentage: 35.4,
      current_document: "protest_article_046.pdf"
    },
    timestamp: "2025-01-15T10:35:00Z"
  }
  */
});
```

**Server → Client (Completion):**
```javascript
socket.on('job:completed', (data) => {
  console.log(data);
  /*
  {
    job_id: "uuid",
    status: "completed",
    results_count: 127,
    average_confidence: 0.87,
    flagged_count: 12,
    completed_at: "2025-01-15T11:00:00Z"
  }
  */
});
```

**Server → Client (Error):**
```javascript
socket.on('job:error', (data) => {
  console.log(data);
  /*
  {
    job_id: "uuid",
    status: "failed",
    error: "LLM API rate limit exceeded",
    failed_at: "2025-01-15T10:45:00Z"
  }
  */
});
```

---

### Unsubscribe from Job

**Client → Server:**
```javascript
socket.emit('unsubscribe:job', { job_id: 'uuid' });
```

---

## Error Handling

### Standard Error Response

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    },
    "timestamp": "2025-01-15T10:00:00Z"
  }
}
```

---

### Common HTTP Status Codes

| Status | Meaning | Usage |
|--------|---------|-------|
| 200 | OK | Successful GET, PATCH, DELETE |
| 201 | Created | Successful POST (resource created) |
| 202 | Accepted | Long-running operation started |
| 204 | No Content | Successful DELETE (no body) |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid auth token |
| 403 | Forbidden | Valid token but no access |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (duplicate) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Temporary server issue |

---

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_CREDENTIALS` | 401 | Invalid email or password |
| `TOKEN_EXPIRED` | 401 | JWT token has expired |
| `VALIDATION_ERROR` | 422 | Request validation failed |
| `PROJECT_NOT_FOUND` | 404 | Project doesn't exist |
| `DOCUMENT_UPLOAD_FAILED` | 400 | File upload error |
| `SCHEMA_NOT_DEFINED` | 400 | Must define schema first |
| `EXTRACTION_IN_PROGRESS` | 409 | Extraction already running |
| `LLM_API_ERROR` | 503 | LLM provider error |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

---

### Example Error Responses

**Validation Error (422):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "email": "Invalid email format",
      "password": "Password must be at least 8 characters"
    },
    "timestamp": "2025-01-15T10:00:00Z"
  }
}
```

**Not Found (404):**
```json
{
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project with ID 'abc123' not found",
    "timestamp": "2025-01-15T10:00:00Z"
  }
}
```

**Rate Limit (429):**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in 60 seconds.",
    "details": {
      "retry_after": 60,
      "limit": 100,
      "window": "1 minute"
    },
    "timestamp": "2025-01-15T10:00:00Z"
  }
}
```

---

## Rate Limiting

### Limits (MVP)

| Endpoint | Limit | Window |
|----------|-------|--------|
| Auth (login/register) | 5 requests | 1 minute |
| General API | 100 requests | 1 minute |
| Document upload | 50 files | 10 minutes |
| Extraction start | 5 jobs | 1 hour |

### Headers

Response includes rate limit headers:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1642248600
```

---

## Pagination

All list endpoints support pagination:

**Request:**
```http
GET /projects/{project_id}/documents?page=2&limit=50
```

**Response:**
```json
{
  "documents": [...],
  "pagination": {
    "page": 2,
    "limit": 50,
    "total": 127,
    "pages": 3,
    "has_next": true,
    "has_prev": true
  }
}
```

---

## Versioning

API is versioned via URL path:
- Current: `/v1/...`
- Future: `/v2/...`

Breaking changes will increment version number.

---

## Authentication Flow

```
1. User registers/logs in
   POST /auth/register or /auth/login
   ↓
2. Server returns JWT token
   { "token": "eyJ..." }
   ↓
3. Client stores token (localStorage/cookie)
   localStorage.setItem('token', token)
   ↓
4. Client includes token in all requests
   Authorization: Bearer eyJ...
   ↓
5. Server validates token
   - Valid: Process request
   - Expired: Return 401, client refreshes
   - Invalid: Return 401, redirect to login
```

---

## Request Examples (cURL)

### Create Project
```bash
curl -X POST https://api.yourapp.com/v1/projects \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Research Project",
    "description": "Description here"
  }'
```

### Upload Documents
```bash
curl -X POST https://api.yourapp.com/v1/projects/PROJECT_ID/documents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

### Start Extraction
```bash
curl -X POST https://api.yourapp.com/v1/projects/PROJECT_ID/extraction/full \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Results
```bash
curl -X GET "https://api.yourapp.com/v1/projects/PROJECT_ID/extraction/results?page=1&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## TypeScript Types

### For Frontend Integration

```typescript
// types/api.ts

export interface User {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'draft' | 'processing' | 'completed';
  document_count: number;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  filename: string;
  file_type: 'pdf' | 'docx' | 'txt';
  size_bytes: number;
  status: 'uploaded' | 'parsed' | 'processing' | 'completed' | 'error';
  uploaded_at: string;
  parsed_at?: string;
}

export interface Variable {
  name: string;
  type: 'string' | 'integer' | 'float' | 'date' | 'boolean';
  description: string;
  required: boolean;
  extraction_prompt: string;
}

export interface Classification {
  name: string;
  type: 'binary' | 'categorical';
  categories: string[];
  description: string;
  classification_prompt: string;
}

export interface Schema {
  id: string;
  project_id: string;
  status: 'draft' | 'approved';
  version: number;
  research_context: {
    domain?: string;
    topic?: string;
    region?: string;
  };
  variables: Variable[];
  classifications: Classification[];
  created_at: string;
  updated_at: string;
}

export interface ExtractionResult {
  id: string;
  document_id: string;
  document_name: string;
  extracted_data: {
    [key: string]: {
      value: any;
      confidence: number;
      source_text?: string;
    };
  };
  flagged: boolean;
  low_confidence_fields: string[];
  extracted_at: string;
}

export interface Job {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  progress?: {
    completed: number;
    total: number;
    percentage: number;
    current_document?: string;
  };
  started_at?: string;
  completed_at?: string;
  estimated_completion?: string;
  errors: string[];
}
```

---

**Document Status:** READY FOR IMPLEMENTATION

**Next Steps:**
1. Backend: Implement FastAPI endpoints following this spec
2. Frontend: Create API client using these types
3. Test: Verify all endpoints match specification
4. Document: Update if any changes during implementation
