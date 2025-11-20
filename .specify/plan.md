# Implementation Plan - Phase 1: Frontend Development

**Project:** Research Automation Tool - UI/Frontend Only
**Phase:** Phase 1 - Frontend + Mock Data
**Timeline:** 2-3 weeks
**Last Updated:** January 19, 2025

---

## Overview

Build a complete, deployable UI for the Research Automation Tool using Next.js 15, React 19, and TypeScript. All functionality will use **mock data** initially, with a clean service layer abstraction to enable seamless backend integration in Phase 2.

**Key Principle:** Ship a working UI fast → Get visual feedback → Connect to existing Python backend later.

---

## Goals & Success Criteria

### Primary Goals
1. ✅ **Deployable UI** - Live site on Vercel with public URL
2. ✅ **Full User Flow** - All MVP pages functional with mock data
3. ✅ **Type-Safe** - TypeScript strict mode, 0 build errors
4. ✅ **Accessible** - WCAG 2.1 AA compliance
5. ✅ **Backend-Ready** - Service layer abstraction for easy API swap

### Success Criteria
- [ ] User can complete full workflow: Create project → Upload docs → Define schema → View results → Export CSV
- [ ] Site loads in < 2 seconds (Lighthouse score > 90)
- [ ] Responsive on desktop (1280px+), tablet (768px+), mobile (480px+)
- [ ] `npm run build` succeeds with 0 TypeScript errors
- [ ] All pages accessible via keyboard navigation
- [ ] Deployed to Vercel with automatic CI/CD

---

## Architecture Overview

### Tech Stack
```yaml
Framework: Next.js 15 (App Router)
Language: TypeScript (strict mode)
Styling: Tailwind CSS v3+
UI Components: shadcn/ui
Icons: Lucide React
Deployment: Vercel (free tier)
```

### Project Structure
```
/
├── src/
│   ├── app/                    # Next.js 15 app directory
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Home page (login/landing)
│   │   ├── dashboard/         # Project dashboard
│   │   ├── projects/[id]/     # Project detail pages
│   │   │   ├── documents/     # Document upload
│   │   │   ├── schema/        # Chat UI for schema definition
│   │   │   ├── results/       # Results viewer
│   │   │   └── export/        # Export configuration
│   │   └── globals.css        # Tailwind imports
│   ├── components/
│   │   ├── ui/                # shadcn/ui components
│   │   ├── layout/            # Header, Sidebar, Footer
│   │   └── features/          # Feature-specific components
│   │       ├── projects/
│   │       ├── documents/
│   │       ├── chat/
│   │       ├── results/
│   │       └── export/
│   ├── lib/
│   │   ├── utils.ts           # Utility functions (cn, etc.)
│   │   └── constants.ts       # App constants
│   ├── services/
│   │   └── mockApi.ts         # Mock data service (Phase 1)
│   │   └── api.ts             # API service interface
│   ├── types/
│   │   ├── api.ts             # API response types
│   │   ├── models.ts          # Data models
│   │   └── index.ts           # Type exports
│   └── mocks/
│       ├── projects.ts        # Mock projects
│       ├── documents.ts       # Mock documents
│       ├── schema.ts          # Mock schema conversations
│       └── results.ts         # Mock extraction results
├── public/                     # Static assets
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### Data Flow (Phase 1 - Mock Data)
```
Component
    ↓
services/api.ts (imports mockApi)
    ↓
services/mockApi.ts
    ↓
mocks/*.ts (typed mock data)
```

**Phase 2:** Simply change `api.ts` to import `realApi` instead of `mockApi`

---

## Page Breakdown & Features

### 1. Home / Landing Page (`/`)
**Purpose:** Entry point - explain the tool, login (future)

**Components:**
- Hero section with tagline
- "Get Started" CTA (routes to `/dashboard`)
- Brief feature overview (3-4 key benefits)

**Mock Behavior:**
- No authentication for Phase 1
- CTA button → `/dashboard`

**Design Notes:**
- Simple, clean, professional
- Desktop-first design
- Use Tailwind gradient backgrounds

---

### 2. Dashboard (`/dashboard`)
**Purpose:** Project overview and management

**Components:**
- Project list (cards or table)
- "New Project" button
- Project search/filter
- Project stats (document count, status)

**Mock Data:**
- 3-5 sample projects with varying states (draft, processing, completed)
- Each project: name, description, created date, document count, status

**Actions:**
- Create new project (modal or separate page)
- Click project → `/projects/[id]/documents`
- Delete project (confirmation modal)

**UI Details:**
- Empty state when no projects ("Create your first project")
- Loading skeleton on initial render
- Status badges (Draft = gray, Processing = yellow, Completed = green)

---

### 3. Project - Documents (`/projects/[id]/documents`)
**Purpose:** Upload and manage documents

**Components:**
- Document upload dropzone (drag & drop)
- File input button (fallback)
- Document list table (filename, size, type, upload date, status)
- Delete document action
- "Next: Define Schema" button

**Mock Data:**
- 10-20 sample documents (PDF, DOCX, TXT)
- Simulated upload progress (instant for Phase 1, but show UI)

**Features:**
- Drag & drop area with visual feedback
- File type validation (accept .pdf, .docx, .txt)
- File size display (KB, MB)
- Remove documents before "upload"
- Upload status indicators (pending, uploading, success, error)

**Navigation:**
- Back to Dashboard
- Next → `/projects/[id]/schema`

---

### 4. Project - Schema Definition (`/projects/[id]/schema`)
**Purpose:** Conversational UI to define extraction schema

**Components:**
- Chat interface (messages list + input)
- AI avatar/icon for bot messages
- User avatar for user messages
- Typing indicator (when "AI is thinking")
- Generated schema preview (sidebar or collapsible panel)
- "Approve Schema" button (when conversation complete)

**Mock Behavior:**
- Predefined conversation flow (5-10 message exchanges)
- AI asks questions:
  1. "What is your research about?"
  2. "What information do you need to extract?"
  3. "How should I classify [variable]?"
  4. Etc.
- User types response → AI responds with next question
- After final question → Show generated schema preview
- "Approve Schema" → `/projects/[id]/results`

**Mock Data:**
- Conversation history (user + AI messages)
- Generated schema (variables, classifications, descriptions)

**UI Details:**
- Message bubbles (AI = left, User = right)
- Timestamp on messages
- Auto-scroll to latest message
- Input area with "Send" button
- "Regenerate" button on AI messages (Phase 2 feature)

---

### 5. Project - Results (`/projects/[id]/results`)
**Purpose:** View extracted data, filter/sort, flag errors

**Components:**
- Data table with extracted results
- Column headers (sortable)
- Filters (by confidence, status, etc.)
- Pagination
- "Flag for Review" action on rows
- Export button → `/projects/[id]/export`

**Mock Data:**
- 50-100 extracted rows
- Each row: document name, extracted variables (date, location, entities, custom), confidence scores

**Features:**
- Sortable columns (click header)
- Filter by confidence (slider: 0-100%)
- Search within results
- Highlight low-confidence cells (< 70% = yellow/red)
- Click row → Modal with full details (source text, confidence breakdown)
- Bulk actions: Select multiple rows, flag/unflag
- "Export Results" button

**UI Details:**
- Confidence badges/colors (🟢 90%+, 🟡 70-89%, 🔴 <70%)
- Striped rows for readability
- Sticky header on scroll
- Loading state (skeleton table)
- Empty state ("No results yet - run extraction")

---

### 6. Project - Export (`/projects/[id]/export`)
**Purpose:** Configure and download CSV export

**Components:**
- Export format selector (Wide vs Long - Phase 1: CSV only)
- Include/exclude options:
  - ☑ Confidence scores
  - ☑ Source text snippets
  - ☑ Flagged items only
- Filter options:
  - Minimum confidence threshold (slider)
  - Exclude flagged items (checkbox)
- Preview table (first 10 rows of export)
- "Download CSV" button

**Mock Behavior:**
- Configure options → Update preview
- Click "Download CSV" → Trigger browser download (mock CSV file)

**Mock Data:**
- Sample CSV content (50 rows)

**UI Details:**
- Two-column layout: Options (left) | Preview (right)
- Real-time preview updates
- Download icon on button
- File size estimate ("~2.5 MB")
- Success toast after download

---

## Shared Components

### Layout Components
1. **Header** (`components/layout/Header.tsx`)
   - Logo/branding
   - Navigation (Dashboard, Projects - if needed)
   - User menu (placeholder for Phase 2)

2. **Sidebar** (`components/layout/Sidebar.tsx` - optional)
   - Project navigation (Documents, Schema, Results, Export)
   - Visible on `/projects/[id]/*` pages

3. **Footer** (`components/layout/Footer.tsx`)
   - Copyright, links (Privacy, Terms - placeholder)

### Feature Components
1. **ProjectCard** (`components/features/projects/ProjectCard.tsx`)
   - Display project summary (name, description, stats)
   - Actions (View, Delete)

2. **DocumentUploader** (`components/features/documents/DocumentUploader.tsx`)
   - Drag & drop zone
   - File list with progress

3. **ChatMessage** (`components/features/chat/ChatMessage.tsx`)
   - Message bubble (AI or User)
   - Timestamp, avatar

4. **DataTable** (`components/features/results/DataTable.tsx`)
   - Reusable table with sorting, filtering, pagination
   - Generic enough for any data

5. **ExportPreview** (`components/features/export/ExportPreview.tsx`)
   - Show preview of export data

### UI Components (shadcn/ui)
- Button
- Input
- Card
- Table
- Dialog (Modal)
- Dropdown Menu
- Badge
- Tooltip
- Slider
- Checkbox
- Tabs
- Toast (notifications)

**Install via CLI:**
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button input card table dialog dropdown-menu badge tooltip slider checkbox tabs toast
```

---

## Mock Data Structure

### Types (`src/types/models.ts`)
```typescript
export interface Project {
  id: string
  name: string
  description: string
  status: 'draft' | 'processing' | 'completed'
  documentCount: number
  createdAt: string
  updatedAt: string
}

export interface Document {
  id: string
  projectId: string
  filename: string
  fileType: 'pdf' | 'docx' | 'txt'
  fileSize: number // bytes
  uploadedAt: string
  status: 'pending' | 'uploaded' | 'processing' | 'completed' | 'error'
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface SchemaVariable {
  id: string
  name: string
  type: 'date' | 'location' | 'entity' | 'custom' | 'classification'
  description: string
  prompt?: string
}

export interface ExtractionResult {
  id: string
  documentId: string
  documentName: string
  data: Record<string, {
    value: string | number | null
    confidence: number // 0-100
  }>
  flagged: boolean
  extractedAt: string
}
```

### Mock Data Files
- `src/mocks/projects.ts` - 5 sample projects
- `src/mocks/documents.ts` - 20 sample documents
- `src/mocks/conversations.ts` - Predefined chat flow
- `src/mocks/schema.ts` - Generated schema examples
- `src/mocks/results.ts` - 100 extraction results

---

## Development Phases

### Week 1: Setup + Core Pages
**Days 1-2: Project Setup**
- [ ] Create Next.js 15 project (`npx create-next-app@latest`)
- [ ] Configure TypeScript (strict mode)
- [ ] Setup Tailwind CSS
- [ ] Install shadcn/ui components
- [ ] Setup folder structure
- [ ] Create type definitions

**Days 3-5: Basic Pages**
- [ ] Landing page (`/`)
- [ ] Dashboard page (`/dashboard`)
- [ ] Project layout (`/projects/[id]/layout.tsx`)
- [ ] Documents page (`/projects/[id]/documents`)

**Day 6-7: Mock Data + Service Layer**
- [ ] Create all mock data files
- [ ] Build `mockApi.ts` service
- [ ] Test data flow (Component → Service → Mock)

### Week 2: Feature Pages + Components
**Days 8-10: Schema & Results**
- [ ] Schema/Chat page (`/projects/[id]/schema`)
- [ ] Results page (`/projects/[id]/results`)
- [ ] Chat components (message, input)
- [ ] Data table component (sortable, filterable)

**Days 11-12: Export + Polish**
- [ ] Export page (`/projects/[id]/export`)
- [ ] CSV download functionality
- [ ] Shared layout components (Header, Sidebar, Footer)

**Days 13-14: Testing + Fixes**
- [ ] Manual testing of full user flow
- [ ] Fix bugs and edge cases
- [ ] Responsive design testing (mobile, tablet)
- [ ] Accessibility testing (keyboard nav, screen reader)

### Week 3: Deployment + Documentation
**Days 15-16: Deployment**
- [ ] Setup Vercel account
- [ ] Connect GitHub repo
- [ ] Configure build settings
- [ ] Deploy to production
- [ ] Test deployed site

**Days 17-18: Documentation + Handoff**
- [ ] Write README (setup, development, deployment)
- [ ] Document mock data structure
- [ ] Create Phase 2 integration guide
- [ ] List all `TODO(Phase 2)` items

**Days 19-21: Buffer / Iteration**
- [ ] Address feedback
- [ ] Polish UI/UX
- [ ] Performance optimization

---

## Accessibility Requirements (WCAG 2.1 AA)

### Keyboard Navigation
- [ ] All interactive elements focusable (Tab/Shift+Tab)
- [ ] Visual focus indicators (blue outline)
- [ ] Modal dialogs trap focus
- [ ] Escape key closes modals

### Screen Reader Support
- [ ] Semantic HTML (`<nav>`, `<main>`, `<article>`)
- [ ] ARIA labels on icon buttons (`aria-label="Delete project"`)
- [ ] Form labels properly associated
- [ ] Table headers have `scope` attribute
- [ ] Live regions for dynamic content (`aria-live="polite"`)

### Color & Contrast
- [ ] Text contrast ≥ 4.5:1 (body text)
- [ ] Large text contrast ≥ 3:1 (headings)
- [ ] No information conveyed by color alone (use icons + color)

### Forms
- [ ] Error messages linked to fields (`aria-describedby`)
- [ ] Required fields marked (`aria-required="true"`)
- [ ] Validation feedback immediate

---

## Performance Targets

### Lighthouse Scores (Target: >90)
- Performance: > 90
- Accessibility: > 95
- Best Practices: > 90
- SEO: > 90

### Core Web Vitals
- **LCP (Largest Contentful Paint):** < 2.5s
- **FID (First Input Delay):** < 100ms
- **CLS (Cumulative Layout Shift):** < 0.1

### Bundle Size
- Initial bundle: < 500KB (gzipped)
- Route-based code splitting (Next.js automatic)

---

## Risks & Mitigations

### Risk 1: Scope Creep
**Mitigation:** Strict adherence to Phase 1 scope. All backend features → Phase 2.

### Risk 2: Mock Data Doesn't Match Real API
**Mitigation:** Define TypeScript interfaces first. Mock data MUST conform. Real API will use same interfaces.

### Risk 3: UI Design Takes Too Long
**Mitigation:** Use shadcn/ui components (pre-built, accessible). Copy-paste examples. Don't overthink design.

### Risk 4: Deployment Issues
**Mitigation:** Deploy early (Day 10). Catch issues before final week.

---

## Definition of Done

A feature is "Done" when:
- ✅ Implemented and functional with mock data
- ✅ TypeScript compiles without errors
- ✅ Responsive on desktop/tablet/mobile
- ✅ Keyboard accessible
- ✅ Manually tested (full user flow)
- ✅ Committed to Git with clear commit message
- ✅ Deployed to Vercel (automatic via CI/CD)

---

## Phase 2 Handoff Checklist

Before starting Phase 2 (backend integration):
- [ ] All Phase 1 pages functional
- [ ] TypeScript interfaces documented
- [ ] Mock API service layer complete
- [ ] All `TODO(Phase 2)` comments cataloged
- [ ] README includes integration guide
- [ ] Deployed site URL shared with team/users

---

## Next Steps

1. **Review this plan** - Confirm scope and approach
2. **Create detailed task list** - Break down into actionable items
3. **Setup development environment** - Install tools, create repo
4. **Start Week 1** - Project setup + core pages

---

**Plan Status:** READY FOR IMPLEMENTATION
**Last Updated:** January 19, 2025
**Phase:** 1 of 2 (Frontend Only)
