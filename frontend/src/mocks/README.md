# Mock Data Documentation

This directory contains comprehensive mock data for Phase 1 frontend development.

## Files

- **mockProjects.ts**: 5 sample projects in various states (setup, schema, review, processing, complete)
- **mockDocuments.ts**: 20+ sample documents (PDF, DOCX, TXT) across multiple projects
- **mockSchemas.ts**: 2 sample extraction schemas with different variable configurations
- **mockExtractions.ts**: 5+ extraction results with varying confidence scores
- **mockProcessingJobs.ts**: 3 processing jobs (sample, full, various statuses)

## Coverage

### Success Cases
- Complete workflow (Climate Protests Study - project 001)
- Sample processing completed
- Full processing completed
- High confidence extractions (85-99%)

### In-Progress Cases
- Large-scale processing (Social Media Sentiment - project 002, 250 documents)
- Mid-progress job (45% complete)

### Edge Cases
- New project with no documents (Legal Case Summary - project 005)
- Low confidence extractions (70-75%)
- Various document types (PDF, DOCX, TXT)
- Different project scales (small vs large)

## Usage

Import mock data in mock API service:

```typescript
import { mockProjects } from '@/mocks/mockProjects';
import { mockDocuments } from '@/mocks/mockDocuments';
import { mockSchemas } from '@/mocks/mockSchemas';
import { mockExtractionResults } from '@/mocks/mockExtractions';
import { mockProcessingJobs } from '@/mocks/mockProcessingJobs';
```

## Phase 2 Migration

All mock data structures match the real API response types defined in `/types/`. When switching to the real backend, only the service layer (`services/mockApi.ts` → `services/realApi.ts`) needs to change.
