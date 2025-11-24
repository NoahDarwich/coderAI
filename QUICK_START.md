# Quick Start Guide - Research Automation Tool

**Status**: Foundation Complete (28/130 tasks) - 21.5% ✅
**Time to MVP**: 12-15 hours remaining
**Last Updated**: 2025-11-23

---

## 🎯 What's Built

### ✅ Complete Foundation (Ready to Use)

1. **Type System** (`/frontend/src/types/`) - ALL DONE
   - All entity types defined and exported
   - API request/response types complete
   - Import: `import { Project, Document, Schema } from '@/types'`

2. **Mock Data** (`/frontend/src/mocks/`) - ALL DONE
   - 5 projects in various workflow states
   - 20+ documents (PDF, DOCX, TXT)
   - 2 complete schemas
   - 5 extraction results
   - 3 processing jobs
   - Comprehensive edge cases covered

3. **Mock API** (`/frontend/src/services/newMockApi.ts`) - ALL DONE
   - 700+ lines, production-ready
   - All 6 API modules implemented:
     - Projects (CRUD operations)
     - Documents (upload, list, delete)
     - Schema (wizard operations)
     - Processing (sample & full)
     - Results (pagination, filtering)
     - Export (CSV generation)
   - Network delay simulation
   - Error handling
   - In-memory persistence

4. **Project Setup** - ALL DONE
   - Next.js 15 + React 19
   - TypeScript strict mode
   - Tailwind CSS 4.0
   - shadcn/ui components
   - All dependencies installed

---

## 🚀 Get Started (2 minutes)

```bash
# 1. Navigate to project
cd /home/noahdarwich/code/coderAI/frontend

# 2. Install dependencies (if not already done)
npm install

# 3. Start development server
npm run dev

# 4. Open browser
# http://localhost:3000
```

---

## 📋 Next Steps (Pick Any Task)

### Priority 1: Stores & Utils (2 hours) - T029-T036
**Required before any UI work**

```bash
# Create these files (templates in IMPLEMENTATION_GUIDE.md):
frontend/src/store/projectStore.ts
frontend/src/store/workflowStore.ts
frontend/src/store/schemaWizardStore.ts
frontend/src/lib/utils.ts
frontend/src/lib/validations.ts
frontend/src/components/layout/WorkflowProgress.tsx
frontend/src/components/layout/ErrorBoundary.tsx
frontend/src/components/layout/DashboardNav.tsx
```

**Copy-paste templates** from IMPLEMENTATION_GUIDE.md sections T029-T036

### Priority 2: User Story 1 (3 hours) - T037-T048
**First working feature: Project setup & document upload**

Components to build:
```
frontend/src/components/workflow/step1/
  ├── ProjectSetupForm.tsx      (T037)
  ├── DocumentUploader.tsx      (T038)
  └── DocumentList.tsx          (T039)
```

Pages to build:
```
frontend/src/app/(dashboard)/projects/
  ├── page.tsx                  (T040) Projects list
  ├── new/page.tsx              (T041) Create project
  └── [id]/
      ├── page.tsx              (T042) Project overview
      └── documents/page.tsx    (T043) Upload documents
```

**Full code** in IMPLEMENTATION_GUIDE.md sections T037-T043

### Priority 3: User Stories 2-5 (10 hours) - T049-T113
Schema wizard → Review → Processing → Results & Export

---

## 💻 Development Workflow

### 1. Pick a Task
Open `specs/001-complete-user-workflow/tasks.md` and choose next unchecked task

### 2. Copy Template
Go to `IMPLEMENTATION_GUIDE.md` and find the task section (e.g., "T037: ProjectSetupForm")

### 3. Create File
```bash
# Example for T037
touch frontend/src/components/workflow/step1/ProjectSetupForm.tsx
```

### 4. Paste Code
Copy the complete template from IMPLEMENTATION_GUIDE.md

### 5. Test It
```bash
npm run build  # Check TypeScript errors
# Navigate to page in browser and test manually
```

### 6. Mark Complete
In `tasks.md`, change `[ ]` to `[X]` for that task

---

## 🔑 Key Imports (Use These Everywhere)

```typescript
// Types (always use these)
import { Project, Document, Schema, ExtractionResult } from '@/types';

// API (only way to call backend)
import { api } from '@/services/api';

// UI Components
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

// Utilities
import { cn, formatDate, formatFileSize } from '@/lib/utils';

// Stores (after T029-T031)
import { useProjectStore } from '@/store/projectStore';
import { useWorkflowStore } from '@/store/workflowStore';
import { useSchemaWizardStore } from '@/store/schemaWizardStore';
```

---

## 📖 API Usage Examples

### Projects
```typescript
// List all projects
const response = await api.projects.list();
const projects = response.data;

// Get single project
const response = await api.projects.get(projectId);
const project = response.data;

// Create project
const response = await api.projects.create({
  name: 'My Project',
  scale: 'small'
});

// Update project
await api.projects.update(projectId, { status: 'schema' });

// Delete project
await api.projects.delete(projectId);
```

### Documents
```typescript
// List documents
const response = await api.documents.list(projectId);
const documents = response.data;

// Upload files
const files = [file1, file2]; // File objects from input
const response = await api.documents.upload(projectId, files);

// Delete document
await api.documents.delete(documentId);

// Get content
const response = await api.documents.getContent(documentId);
const text = response.data;
```

### Schema
```typescript
// Get schema
const response = await api.schema.get(projectId);
const schema = response.data;

// Save schema
const response = await api.schema.save(projectId, {
  variables: [
    { name: 'Date', type: 'date', instructions: '...' },
    { name: 'Location', type: 'text', instructions: '...' }
  ]
});

// Confirm schema (locks it for processing)
await api.schema.confirm(projectId);

// Add variable
await api.schema.addVariable(projectId, {
  name: 'New Variable',
  type: 'text',
  instructions: 'Extract...'
});
```

### Processing
```typescript
// Start sample processing
const response = await api.processing.startSample(projectId, 10);
const job = response.data;

// Start full processing
const response = await api.processing.startFull(projectId);
const job = response.data;

// Get job status
const response = await api.processing.getJob(jobId);
const job = response.data;

// Cancel job
await api.processing.cancelJob(jobId);
```

### Results
```typescript
// List results with pagination
const response = await api.results.list(projectId, {
  page: 1,
  pageSize: 50,
  minConfidence: 70
});
const { data, pagination } = response.data;

// Get single result
const response = await api.results.get(extractionId);
const extraction = response.data;

// Flag result (for sample testing)
await api.results.flag(extractionId, true); // true = correct
```

### Export
```typescript
// Generate CSV
const response = await api.export.generate(projectId, {
  format: 'csv',
  structure: 'wide', // or 'long'
  includeConfidence: true,
  includeSourceText: false,
  minConfidence: 70
});

const exportResult = response.data;
// Download using exportResult.downloadUrl (blob URL)

// Trigger download
window.open(exportResult.downloadUrl, '_blank');
```

---

## 🎨 Component Patterns

### Basic Page
```typescript
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/services/api';

export default function MyPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      const response = await api.projects.get(projectId);
      setData(response.data);
      setIsLoading(false);
    }
    loadData();
  }, [projectId]);

  if (isLoading) return <div>Loading...</div>;

  return <div>{/* Your UI */}</div>;
}
```

### Form with Validation
```typescript
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { projectSchema } from '@/lib/validations';

export function MyForm() {
  const form = useForm({
    resolver: zodResolver(projectSchema),
    defaultValues: { name: '', scale: 'small' }
  });

  async function onSubmit(data) {
    const response = await api.projects.create(data);
    // Handle response
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        {/* Form fields */}
      </form>
    </Form>
  );
}
```

### Component with State
```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';

export function MyComponent({ projectId }) {
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  async function handleClick() {
    setIsLoading(true);
    try {
      const response = await api.projects.get(projectId);
      toast({ title: 'Success', description: 'Action completed' });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Action failed',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <Button onClick={handleClick} disabled={isLoading}>
      {isLoading ? 'Loading...' : 'Click Me'}
    </Button>
  );
}
```

---

## ✅ Testing Checklist

Before marking a task complete:

- [ ] TypeScript compiles: `npm run build`
- [ ] No console errors in browser
- [ ] Loading state shows while fetching
- [ ] Error state shows on API failure
- [ ] Success message/navigation works
- [ ] Works on desktop (1920x1080)
- [ ] Works on tablet (768px width)
- [ ] Keyboard navigation works (Tab, Enter)
- [ ] Forms validate correctly

---

## 🐛 Troubleshooting

### "Module not found" Error
```bash
# Check import path uses @ alias
import { api } from '@/services/api';  # ✅ Correct
import { api } from '../services/api'; # ❌ Wrong
```

### "Type X cannot be assigned to Y"
```bash
# Import types from @/types
import { Project } from '@/types';
```

### API not working
```bash
# Ensure using new mock API
import { api } from '@/services/api';

# Check newMockApi.ts is exporting 'api'
# See line 690+ in newMockApi.ts
```

### Component not rendering
```bash
# Ensure 'use client' at top of file
'use client';

import { useState } from 'react';
```

### Build errors
```bash
# Run TypeScript check
npm run build

# Check for:
# - Missing imports
# - Type mismatches
# - Syntax errors
```

---

## 📚 Documentation

- **IMPLEMENTATION_GUIDE.md**: Complete implementation guide (all 130 tasks)
- **tasks.md**: Task checklist (track progress here)
- **USER_WORKFLOW.md**: 5-step workflow specification
- **spec.md**: Feature requirements
- **data-model.md**: Entity relationships
- **plan.md**: Technical architecture

---

## 🎯 Success Metrics

### Phase 1 Foundation ✅ (28/130 tasks)
- [X] Types defined
- [X] Mock data created
- [X] Mock API implemented
- [X] Dependencies installed

### Next Milestone: MVP (48/130 tasks)
- [ ] Stores & utils (T029-T036)
- [ ] User Story 1 complete (T037-T048)
- [ ] Can create project
- [ ] Can upload documents
- [ ] Deploys to Vercel

### Final Goal: Complete Workflow (130/130 tasks)
- [ ] All 5 user stories complete
- [ ] All workflow steps functional
- [ ] End-to-end testing passed
- [ ] Accessibility audit passed
- [ ] Production deployment

---

## 🚢 Deployment

### Quick Deploy to Vercel

```bash
# 1. Commit changes
git add .
git commit -m "feat: Add component X"

# 2. Deploy
cd frontend
vercel

# 3. Follow prompts
# - Link to existing project or create new
# - Deploy!
```

### Build for Production

```bash
cd frontend
npm run build
npm run start  # Test production build locally
```

---

## 💡 Pro Tips

1. **Copy, don't write from scratch**: All templates are in IMPLEMENTATION_GUIDE.md
2. **Test incrementally**: Build one component, test it, then move to next
3. **Use TypeScript**: Let it catch errors before runtime
4. **Check mock data**: See `/mocks/` for available data
5. **Read API implementation**: `/services/newMockApi.ts` has all API patterns
6. **Follow the workflow**: Complete tasks in order (T001 → T130)
7. **Mark progress**: Update tasks.md as you go

---

## 🎉 You're Ready!

**Everything you need is built.** Just follow the templates in IMPLEMENTATION_GUIDE.md and you'll have a working MVP in 12-15 hours.

**Start here**: T029 (projectStore) in IMPLEMENTATION_GUIDE.md

**Questions?** Check IMPLEMENTATION_GUIDE.md - it has 100+ pages of detailed implementation guidance.

---

**Happy coding! 🚀**
