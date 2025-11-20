<!--
═══════════════════════════════════════════════════════════════════════
Sync Impact Report - Constitution v1.1.0
═══════════════════════════════════════════════════════════════════════
Version Change: 1.0.0 → 1.1.0 (MINOR)
Rationale: Scope reduction to frontend-only development phase

Modified Principles:
  - I. AI-First Architecture → Deferred to Phase 2 (backend integration)
  - II. Research-Grade Quality → Adapted for UI/UX focus
  - III. Pragmatic Development → Updated for frontend-only scope

Added Sections:
  - Development Phases (Phase 1: Frontend + Mock Data)
  - Mock Data Strategy

Removed Sections:
  - Backend-specific quality standards (deferred)
  - LLM orchestration requirements (deferred)

Templates Requiring Updates:
  ✅ All templates - No changes needed (phase-based approach)

Follow-up TODOs:
  - Phase 2: Update constitution for backend integration
  - Phase 2: Restore AI-First Architecture principle
═══════════════════════════════════════════════════════════════════════
-->

# Research Automation Tool Constitution

**Current Phase:** Phase 1 - Frontend Development (Mock Data)

## Core Principles

### I. UI-First Design (Phase 1 Focus)
**Build a complete, functional UI with mock data that demonstrates the full user experience.**

- All MVP pages MUST be implemented (see FRONTEND-DESIGN.md):
  - Dashboard (project overview)
  - Document upload interface
  - Chat UI for schema definition
  - Results viewer (data table with filtering/sorting)
  - Export configuration and download
- Mock data MUST be realistic:
  - Representative of actual backend responses
  - Cover edge cases (errors, empty states, large datasets)
  - Typed interfaces matching future API contracts
- UI MUST be backend-agnostic:
  - All data access through typed service layer (`services/api.ts`)
  - Easy swap from mock → real API (change import only)
  - NO hardcoded data in components
- Component design MUST support future backend integration:
  - Loading states for async operations
  - Error boundaries for API failures
  - Optimistic updates where appropriate

**Rationale:** Building UI-first with mock data allows rapid iteration on UX without backend dependencies. The service layer abstraction ensures seamless backend integration in Phase 2. Realistic mocks catch design issues early.

**Phase 2 (Future):** This principle will be replaced with "AI-First Architecture" when backend integration begins.

### II. User Experience Excellence
**The UI MUST be intuitive, accessible, and delightful for non-technical researchers.**

- **Clarity over cleverness:**
  - Clear labels and helpful placeholder text
  - Tooltips for complex features
  - Inline help where needed (no hunting for documentation)
- **Accessibility (WCAG 2.1 AA minimum):**
  - Keyboard navigation for all actions
  - Screen reader support (semantic HTML, ARIA labels)
  - Color contrast ratios meet standards
  - Focus indicators visible
- **Responsive design:**
  - Mobile-friendly (768px+ for full features)
  - Tablet-optimized layouts
  - Desktop-first design (primary use case)
- **Performance:**
  - Initial page load < 2 seconds
  - UI interactions feel instant (< 100ms feedback)
  - No layout shift (reserve space for dynamic content)
- **Error handling:**
  - Friendly error messages (no tech jargon)
  - Clear recovery actions ("Try again" vs "Error 500")
  - Validation feedback as user types (not just on submit)

**Rationale:** Researchers are domain experts, not programmers. The UI must be self-explanatory and forgiving. Poor UX will kill adoption faster than missing features.

### III. Rapid Iteration (Frontend-First)
**Ship a working UI fast, iterate based on visual feedback, connect backend later.**

- **Phase 1 scope (Frontend + Mock Data):**
  - ✅ IN: All UI pages, mock data, component library, Vercel deployment
  - ❌ OUT: Backend integration, real LLM calls, database, authentication (Phase 2)
- **Development speed:**
  - Use shadcn/ui components (don't build from scratch)
  - Tailwind CSS for styling (no custom CSS files)
  - Copy-paste over abstraction (DRY can wait)
  - Ship ugly/fast, refine later
- **Mock data strategy:**
  - Create realistic mock responses in `src/mocks/`
  - Use MSW (Mock Service Worker) or simple JSON files
  - TypeScript interfaces define contracts for future API
- **Testing for Phase 1:**
  - Component tests for complex UI logic (forms, tables)
  - Visual testing (Storybook optional, manual review mandatory)
  - NO E2E tests yet (no backend to test against)
- **Technical debt is expected:**
  - Hardcoded mock data → OK (will be replaced)
  - Simplified state management → OK (add Zustand later if needed)
  - No optimization → OK (premature optimization is evil)
  - Document TODOs for Phase 2: `// TODO(Phase 2): Replace with real API call`

**Rationale:** Frontend development is fastest when decoupled from backend. Building the full UI with mocks validates the design before investing in backend work. Feedback on live UI (deployed to Vercel) beats wireframes.

## Development Phases

### Phase 1: Frontend + Mock Data (Current)
**Goal:** Deployable UI that demonstrates full user workflow with realistic mock data

**Deliverables:**
- Complete Next.js application with all MVP pages
- TypeScript interfaces for all data models
- Mock data service layer (`services/mockApi.ts`)
- Deployed to Vercel (public URL)
- Component library (shadcn/ui setup)
- Basic documentation (README with setup instructions)

**Success Criteria:**
- ✅ User can navigate full workflow with mock data
- ✅ UI is responsive and accessible
- ✅ Deployed site loads in < 2 seconds
- ✅ TypeScript has 0 errors (`npm run build` succeeds)

### Phase 2: Backend Integration (Future)
**Deferred until Phase 1 complete**

**Scope:**
- Connect existing Python backend script
- Replace mock data with real API calls
- Add authentication
- Deploy backend (Railway/Render)
- End-to-end testing

**Constitution Updates Required:**
- Restore "AI-First Architecture" principle
- Add backend quality standards
- Add deployment strategy for full stack

## Quality Standards (Phase 1)

### Code Quality
- **Type Safety:** TypeScript with strict mode enabled
- **Component Structure:**
  - One component per file
  - Props interfaces defined and exported
  - Max 200 lines per component (split if larger)
- **Styling:** Tailwind CSS utility classes only (no custom CSS)
- **Error Boundaries:** Wrap page-level components in error boundaries
- **Security:** NO API keys or secrets in frontend code (not applicable for Phase 1 with mocks)

### Performance Targets
- **Initial Load:** < 2 seconds (First Contentful Paint)
- **Time to Interactive:** < 3 seconds
- **Bundle Size:** < 500KB (gzipped)
- **Lighthouse Score:** > 90 (Performance, Accessibility)

### Accessibility Standards
- WCAG 2.1 AA compliance minimum
- Semantic HTML (proper headings hierarchy)
- ARIA labels for interactive elements
- Keyboard navigation works everywhere
- Color contrast ratio ≥ 4.5:1 for text

## Development Workflow (Phase 1)

### Git Workflow
- `main` branch = deployable code (auto-deploys to Vercel)
- Feature branches for all work (`feature/dashboard-ui`, `feature/upload-page`)
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `style:`, `chore:`
- Squash-merge to main (clean history)

### Code Organization
```
src/
├── app/                 # Next.js 15 app directory (pages)
├── components/          # React components
│   ├── ui/             # shadcn/ui components
│   ├── features/       # Feature-specific components
│   └── layout/         # Layout components
├── lib/                # Utilities and helpers
├── services/           # API service layer
│   └── mockApi.ts     # Mock data service (Phase 1)
├── types/              # TypeScript interfaces
└── mocks/              # Mock data files
```

### Testing Strategy (Phase 1)
- **Component Tests:** For complex components (data tables, forms)
- **Manual Testing:** Primary validation method
- **Visual Review:** Every PR includes screenshots/video
- Target: 30% coverage (quality over quantity)

### Deployment (Phase 1)
- **Vercel:** Automatic deployment on push to `main`
- **Preview Deployments:** Every PR gets a preview URL
- **Environment:** Production only (no staging for Phase 1)
- **Rollback:** Git revert + force push if needed

### Documentation (Phase 1)
- **README.md:** Setup instructions, development commands
- **Component docs:** JSDoc for complex components
- **Mock data docs:** Comment schemas in `mocks/README.md`
- **Phase 2 TODOs:** Track integration points in code comments

## Technology Stack (Phase 1)

### Approved Stack
- **Frontend Framework:** Next.js 15 (App Router)
- **React Version:** React 19
- **Language:** TypeScript (strict mode)
- **Styling:** Tailwind CSS v3+
- **UI Components:** shadcn/ui
- **State Management:** React useState/useContext (Zustand in Phase 2 if needed)
- **Icons:** Lucide React
- **Deployment:** Vercel (free tier)

### Phase 1 Dependencies (Allowed)
```json
{
  "next": "^15.0.0",
  "react": "^19.0.0",
  "typescript": "^5.0.0",
  "tailwindcss": "^3.0.0",
  "lucide-react": "latest",
  "@radix-ui/*": "latest"  // shadcn/ui dependencies
}
```

### Prohibited (Phase 1)
- ❌ Backend frameworks (FastAPI, Express, etc.)
- ❌ Database libraries (Prisma, Drizzle, etc.)
- ❌ Authentication libraries (NextAuth, etc.) - Phase 2
- ❌ State management libraries (Redux, MobX) - use React built-ins
- ❌ CSS-in-JS (Emotion, Styled Components) - use Tailwind only

### Phase 2 Stack (Future)
- Backend: FastAPI + Python 3.11+
- Database: PostgreSQL + Redis
- LLM: LangGraph + OpenAI/Anthropic
- Infrastructure: Railway (backend) + Vercel (frontend)

## Governance

### Constitution Authority
- This constitution supersedes all other development practices
- Conflicts are resolved in favor of constitution principles
- Exceptions require explicit documentation in commit messages

### Amendment Process
1. Propose amendment via issue/discussion
2. Document rationale (what changed, why, impact)
3. Update constitution with version bump (see Versioning below)
4. Update dependent templates if needed
5. Commit with message: `docs: amend constitution to vX.Y.Z (summary)`

### Versioning (Semantic)
- **MAJOR.MINOR.PATCH** format (e.g., 1.2.3)
- **MAJOR:** Backward-incompatible changes (remove principle, change architecture rule)
- **MINOR:** Add new principle or section
- **PATCH:** Clarifications, typo fixes, wording improvements

### Compliance Review
- Weekly check-in: Are we following principles?
- Flag violations immediately in PRs/commits
- Course-correct within 24 hours
- Constitution review at each major milestone (end of Month 1, 2, 3)

### Complexity Justification
- Any component requiring >500 lines of code MUST have justification
- Any external dependency MUST have rationale documented
- "Because it's cool" is NOT a valid justification
- "Saves X days of work" or "Prevents Y class of bugs" IS valid

## Mock Data Strategy

### Mock Data Requirements
- **Location:** All mocks in `src/mocks/` directory
- **Format:** TypeScript files exporting typed objects
- **Realism:** Data should match expected API responses exactly
- **Coverage:** Include success cases, errors, edge cases (empty, large datasets)

### Mock Service Layer
```typescript
// src/services/mockApi.ts
export const mockApi = {
  projects: {
    list: async () => mockProjects,
    get: async (id: string) => mockProjects.find(p => p.id === id),
    create: async (data: CreateProjectData) => { /* ... */ }
  },
  documents: { /* ... */ },
  extraction: { /* ... */ }
}

// Phase 2: Replace with real API
// import { mockApi as api } from './mockApi'
// import { realApi as api } from './realApi'
```

### TypeScript Contracts
- Define interfaces in `src/types/api.ts`
- Mock data MUST conform to interfaces
- Phase 2 real API MUST conform to same interfaces
- Version interfaces if API changes

**Version**: 1.1.0 | **Ratified**: 2025-01-19 | **Last Amended**: 2025-01-19
