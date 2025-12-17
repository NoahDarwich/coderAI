# Data Extraction Workflow - Backend API

FastAPI backend service for the research data extraction tool.

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (optional for MVP)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration
```

### Database Setup

```bash
# Create database
createdb data_extraction

# Run migrations
alembic upgrade head
```

### Running the Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/api/test_projects.py -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current
```

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── routes/          # API endpoint definitions
│   │   ├── dependencies.py  # FastAPI dependencies
│   │   └── middleware.py    # CORS, error handling
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── database.py      # Database connection
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── services/            # Business logic layer
│   ├── workers/             # Background job processors
│   └── main.py              # FastAPI application entry point
├── tests/
│   ├── api/                 # API endpoint tests
│   ├── services/            # Service layer tests
│   └── integration/         # End-to-end tests
├── alembic/                 # Database migrations
├── docker/                  # Docker configuration
└── requirements.txt         # Python dependencies
```

## Docker

### Build and Run

```bash
# Build image
docker build -f docker/Dockerfile -t backend:latest .

# Run with docker-compose
docker-compose -f docker/docker-compose.yml up
```

### Environment Variables

See `.env.example` for all configuration options.

## API Endpoints

### Projects
- `GET /api/v1/projects` - List all projects
- `POST /api/v1/projects` - Create new project
- `GET /api/v1/projects/{id}` - Get project details
- `PUT /api/v1/projects/{id}` - Update project
- `DELETE /api/v1/projects/{id}` - Delete project

### Variables
- `GET /api/v1/projects/{id}/variables` - List project variables
- `POST /api/v1/projects/{id}/variables` - Create variable
- `GET /api/v1/variables/{id}` - Get variable details
- `PUT /api/v1/variables/{id}` - Update variable
- `DELETE /api/v1/variables/{id}` - Delete variable

### Documents
- `GET /api/v1/projects/{id}/documents` - List documents
- `POST /api/v1/projects/{id}/documents` - Upload document
- `DELETE /api/v1/documents/{id}` - Delete document

### Processing
- `POST /api/v1/projects/{id}/jobs` - Create processing job
- `GET /api/v1/jobs/{id}` - Get job status
- `GET /api/v1/jobs/{id}/results` - Get job results
- `DELETE /api/v1/jobs/{id}` - Cancel job

### Export
- `POST /api/v1/projects/{id}/export` - Generate export file

## Deployment

### Railway Deployment

Railway provides a simple deployment process for containerized applications.

#### Prerequisites
- Railway account (https://railway.app)
- Railway CLI installed: `npm install -g @railway/cli`
- Docker image built

#### Deployment Steps

1. **Login to Railway**:
```bash
railway login
```

2. **Create New Project**:
```bash
railway init
```

3. **Add PostgreSQL Database**:
```bash
railway add postgres
```

4. **Set Environment Variables**:
```bash
railway variables set OPENAI_API_KEY=sk-...
railway variables set ALLOWED_ORIGINS=https://your-frontend.vercel.app
railway variables set DEBUG=False
```

5. **Deploy**:
```bash
railway up
```

Railway will automatically:
- Build your Docker image
- Provision a PostgreSQL database
- Set DATABASE_URL environment variable
- Deploy to production

#### Database Migrations

Run migrations after deployment:
```bash
railway run alembic upgrade head
```

### Render Deployment

Render is another simple platform for deploying web services.

#### Prerequisites
- Render account (https://render.com)
- GitHub repository with your code

#### Deployment Steps

1. **Create Web Service**:
   - Go to Render dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: data-extraction-api
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

2. **Add PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - Create database
   - Copy Internal Database URL

3. **Set Environment Variables**:
   - In web service settings, add:
     - `DATABASE_URL` = <PostgreSQL Internal URL>
     - `OPENAI_API_KEY` = sk-...
     - `ALLOWED_ORIGINS` = https://your-frontend.vercel.app
     - `DEBUG` = False

4. **Deploy**:
   - Render will automatically deploy on push to main branch

5. **Run Migrations**:
   - In web service shell:
     ```bash
     alembic upgrade head
     ```

### Docker Deployment (Self-Hosted)

For self-hosted deployment on any server with Docker.

#### Prerequisites
- Docker and Docker Compose installed
- Server with public IP or domain

#### Steps

1. **Clone Repository**:
```bash
git clone <your-repo>
cd backend
```

2. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env with production values
```

3. **Build and Run**:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

4. **Run Migrations**:
```bash
docker-compose exec api alembic upgrade head
```

5. **Set Up Reverse Proxy** (nginx):
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

6. **Set Up SSL** (Let's Encrypt):
```bash
sudo certbot --nginx -d api.yourdomain.com
```

### Health Checks

All deployment platforms can use these endpoints for health monitoring:
- `/health` - Basic health check
- `/` - API info and status

### Monitoring and Logging

For production monitoring, consider integrating:
- **Sentry** for error tracking: https://sentry.io
- **Datadog** for metrics: https://www.datadoghq.com
- **Papertrail** for log aggregation: https://www.papertrail.com

Add to requirements.txt:
```
sentry-sdk[fastapi]==1.39.0
```

Configure in `src/main.py`:
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    traces_sample_rate=0.1,
)
```

### Scaling Considerations

For high-traffic production deployments:

1. **Database Connection Pooling**:
   - Increase pool_size in database.py
   - Use PgBouncer for connection pooling

2. **Background Jobs**:
   - Migrate from FastAPI BackgroundTasks to Arq + Redis
   - Run separate worker processes

3. **Caching**:
   - Add Redis for caching frequent queries
   - Cache prompt generation results

4. **Load Balancing**:
   - Run multiple API instances behind a load balancer
   - Use sticky sessions if needed

5. **Rate Limiting**:
   - Add rate limiting middleware
   - Prevent API abuse

## License

Proprietary
