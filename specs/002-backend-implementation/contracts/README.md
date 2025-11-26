# API Contracts

This directory contains the API contract definitions for the backend service.

## Files

- **openapi.yaml**: OpenAPI 3.0 specification for REST API endpoints

## Using the OpenAPI Spec

### Viewing the Spec

You can view the API documentation using:

1. **Swagger UI** (online): https://editor.swagger.io/ - paste the YAML content
2. **Redoc** (online): https://redocly.github.io/redoc/ - upload the YAML file
3. **VS Code**: Install "OpenAPI (Swagger) Editor" extension

### Generating Client Code

You can generate TypeScript client code for the frontend using OpenAPI Generator:

```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate TypeScript client
openapi-generator-cli generate \
  -i contracts/openapi.yaml \
  -g typescript-fetch \
  -o frontend/src/api-client
```

### Validating Requests

The OpenAPI spec includes validation rules for all request/response schemas. Backend should validate all incoming requests against these schemas using Pydantic.

## API Endpoints Summary

### Projects
- `GET /projects` - List projects
- `POST /projects` - Create project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Variables
- `GET /projects/{id}/variables` - List variables
- `POST /projects/{id}/variables` - Create variable
- `GET /variables/{id}` - Get variable details
- `PUT /variables/{id}` - Update variable
- `DELETE /variables/{id}` - Delete variable

### Documents
- `GET /projects/{id}/documents` - List documents
- `POST /projects/{id}/documents` - Upload document
- `GET /documents/{id}` - Get document details
- `DELETE /documents/{id}` - Delete document

### Processing
- `GET /projects/{id}/jobs` - List jobs
- `POST /projects/{id}/jobs` - Create processing job
- `GET /jobs/{id}` - Get job status
- `DELETE /jobs/{id}` - Cancel job
- `GET /jobs/{id}/results` - Get job results
- `POST /extractions/{id}/feedback` - Submit feedback

### Exports
- `POST /projects/{id}/export` - Generate export file

## Authentication (Future)

Authentication is not implemented in Phase 1. Future versions will use:
- **Method**: Bearer token (JWT)
- **Header**: `Authorization: Bearer <token>`
- **Endpoints**: All endpoints except health check

## Error Handling

All errors follow RFC 7807 Problem Details format:

```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Request validation failed",
  "instance": "/api/v1/projects",
  "errors": [
    {"field": "name", "message": "Name is required"}
  ]
}
```

## CORS Configuration

Development:
- Allow all origins: `http://localhost:*`

Production:
- Allow frontend origin only: `https://app.example.com`

## Rate Limiting (Future)

Not implemented in Phase 1. Future versions will use:
- **Rate**: 100 requests per minute per IP
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **Response**: 429 Too Many Requests when exceeded
