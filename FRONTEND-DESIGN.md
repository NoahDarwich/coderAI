# Frontend Technical Design Document

**Version:** 1.0
**Target:** MVP (3-4 months)
**Last Updated:** November 18, 2025

---

## Technology Stack

### Core Framework: Next.js 15 + React 19 + TypeScript

```json
{
  "framework": "Next.js 15",
  "react": "^19.0.0",
  "typescript": "^5.6.0",
  "styling": "Tailwind CSS 4.0",
  "ui-library": "shadcn/ui",
  "state-management": "Zustand",
  "forms": "React Hook Form + Zod",
  "api-client": "TanStack Query (React Query)",
  "websockets": "Socket.io-client",
  "data-tables": "TanStack Table",
  "file-upload": "react-dropzone",
  "notifications": "Sonner"
}
```

### Why These Choices?

**Next.js 15:**
- App Router (React Server Components)
- Built-in API routes for BFF pattern
- Excellent TypeScript support
- Image optimization
- Automatic code splitting
- SEO-friendly (if public pages needed)

**Tailwind CSS:**
- Rapid prototyping
- Consistent design system
- Small bundle size
- No CSS-in-JS runtime overhead

**shadcn/ui:**
- Copy-paste components (not a dependency)
- Full customization
- Accessible by default (ARIA)
- Beautiful design
- TypeScript first

**Zustand:**
- Simpler than Redux
- TypeScript support
- No boilerplate
- Perfect for MVP scope

**TanStack Query:**
- Server state management
- Automatic caching
- Background refetching
- Optimistic updates
- Perfect for REST APIs

---

## Project Structure

```
coderAI/
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js App Router
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── (dashboard)/
│   │   │   │   ├── projects/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   └── [id]/
│   │   │   │   │       ├── page.tsx           # Project overview
│   │   │   │   │       ├── documents/         # Document management
│   │   │   │   │       ├── schema/            # Schema builder (chat)
│   │   │   │   │       ├── test/              # Test results review
│   │   │   │   │       ├── process/           # Full processing
│   │   │   │   │       └── export/            # Data review & export
│   │   │   │   └── layout.tsx
│   │   │   ├── api/                # API routes (BFF if needed)
│   │   │   ├── layout.tsx          # Root layout
│   │   │   └── page.tsx            # Landing page
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn/ui components
│   │   │   ├── chat/
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   └── ChatInput.tsx
│   │   │   ├── documents/
│   │   │   │   ├── DocumentUploader.tsx
│   │   │   │   ├── DocumentList.tsx
│   │   │   │   └── DocumentPreview.tsx
│   │   │   ├── data/
│   │   │   │   ├── DataTable.tsx
│   │   │   │   ├── ExtractionPreview.tsx
│   │   │   │   └── ConfidenceIndicator.tsx
│   │   │   └── layout/
│   │   │       ├── Header.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       └── ProgressBar.tsx
│   │   ├── lib/
│   │   │   ├── api/                # API client
│   │   │   │   ├── client.ts
│   │   │   │   ├── projects.ts
│   │   │   │   ├── documents.ts
│   │   │   │   ├── schema.ts
│   │   │   │   └── extraction.ts
│   │   │   ├── hooks/              # Custom hooks
│   │   │   │   ├── useProject.ts
│   │   │   │   ├── useDocuments.ts
│   │   │   │   ├── useChat.ts
│   │   │   │   └── useWebSocket.ts
│   │   │   ├── store/              # Zustand stores
│   │   │   │   ├── authStore.ts
│   │   │   │   ├── projectStore.ts
│   │   │   │   └── chatStore.ts
│   │   │   ├── types/              # TypeScript types
│   │   │   │   ├── api.ts
│   │   │   │   ├── project.ts
│   │   │   │   ├── document.ts
│   │   │   │   └── extraction.ts
│   │   │   └── utils/
│   │   │       ├── validation.ts
│   │   │       ├── formatting.ts
│   │   │       └── export.ts
│   │   └── styles/
│   │       └── globals.css
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
```

---

## Key UI Components

### 1. Conversational Schema Builder

**Component:** `ChatInterface.tsx`

**Features:**
- Real-time message streaming
- Markdown rendering for AI responses
- Typing indicators
- Message history
- Context-aware suggestions

**Design Pattern:** Based on 2025 best practices:
- Multi-modal input (text primary, voice future)
- Context preservation
- Clear AI vs. user distinction
- Example suggestions on first load

```tsx
interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    suggestions?: string[];
    extractedSchema?: Partial<ExtractionSchema>;
  };
}

// Usage
<ChatInterface
  projectId={projectId}
  onSchemaComplete={(schema) => handleSchemaComplete(schema)}
  initialPrompt="Let's define what data you want to extract..."
/>
```

**Key UX Principles:**
- **Progressive disclosure:** Show examples initially, hide as conversation progresses
- **Context awareness:** Reference previous answers in follow-up questions
- **Error recovery:** Allow users to go back and modify earlier answers
- **Transparency:** Show what schema is being built in sidebar as conversation proceeds

### 2. Document Upload Manager

**Component:** `DocumentUploader.tsx`

**Features:**
- Drag-and-drop zone
- Multiple file upload
- Format validation (PDF, DOCX, TXT)
- Upload progress tracking
- Preview uploaded documents
- Batch delete

```tsx
<DocumentUploader
  projectId={projectId}
  maxFiles={100}
  acceptedFormats={['pdf', 'docx', 'txt']}
  onUploadComplete={(documents) => handleUploadComplete(documents)}
  onError={(error) => showErrorToast(error)}
/>
```

**Design:**
- Large drop zone with clear visual feedback
- File list with thumbnails
- Individual file actions (view, delete)
- Batch actions (delete selected, download all)

### 3. Extraction Results Table

**Component:** `ExtractionPreview.tsx`

**Features:**
- Sortable/filterable data table
- Confidence score visualization
- Source document linking
- Inline error flagging
- Export selection

```tsx
interface ExtractionResult {
  id: string;
  documentId: string;
  documentName: string;
  extractedData: Record<string, {
    value: any;
    confidence: number;
    sourceText?: string;
  }>;
  flagged: boolean;
  timestamp: Date;
}

<ExtractionPreview
  results={extractionResults}
  onFlag={(resultId) => flagForReview(resultId)}
  onExport={(format) => exportData(format)}
  showConfidenceScores={true}
/>
```

**Design:**
- **Confidence indicators:**
  - 90-100%: Green dot
  - 70-89%: Yellow dot
  - <70%: Red dot + auto-flag
- **Inline source quotes:** Hover to see source text
- **Side-by-side view:** Click row to see full document + extraction

### 4. Live Progress Tracker

**Component:** `ProcessingProgress.tsx`

**Features:**
- Real-time progress updates via WebSocket
- Estimated time remaining
- Current document being processed
- Error count
- Pause/cancel ability

```tsx
<ProcessingProgress
  jobId={jobId}
  totalDocuments={totalDocs}
  onComplete={() => navigateToResults()}
  onError={(error) => handleError(error)}
/>
```

---

## State Management Strategy

### Global State (Zustand)

**Auth Store:**
```typescript
interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}
```

**Project Store:**
```typescript
interface ProjectStore {
  currentProject: Project | null;
  projects: Project[];
  setCurrentProject: (project: Project) => void;
  createProject: (data: CreateProjectDto) => Promise<Project>;
  deleteProject: (id: string) => Promise<void>;
}
```

**Chat Store:**
```typescript
interface ChatStore {
  messages: ChatMessage[];
  isStreaming: boolean;
  schema: Partial<ExtractionSchema>;
  addMessage: (message: ChatMessage) => void;
  updateSchema: (schema: Partial<ExtractionSchema>) => void;
  resetConversation: () => void;
}
```

### Server State (TanStack Query)

**Key Queries:**
```typescript
// Projects
useQuery({ queryKey: ['projects'], queryFn: fetchProjects })
useQuery({ queryKey: ['project', id], queryFn: () => fetchProject(id) })

// Documents
useQuery({ queryKey: ['documents', projectId], queryFn: () => fetchDocuments(projectId) })

// Extractions
useQuery({ queryKey: ['extractions', projectId], queryFn: () => fetchExtractions(projectId) })
```

**Key Mutations:**
```typescript
useMutation({
  mutationFn: uploadDocuments,
  onSuccess: () => queryClient.invalidateQueries(['documents', projectId])
})

useMutation({
  mutationFn: startExtraction,
  onSuccess: () => queryClient.invalidateQueries(['extractions', projectId])
})
```

---

## API Integration

### REST API Client

```typescript
// lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
```

### WebSocket Connection

```typescript
// lib/hooks/useWebSocket.ts
import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface ProcessingUpdate {
  jobId: string;
  status: 'processing' | 'completed' | 'error';
  progress: number;
  currentDocument?: string;
  errorMessage?: string;
}

export function useWebSocket(jobId: string) {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [updates, setUpdates] = useState<ProcessingUpdate[]>([]);

  useEffect(() => {
    const newSocket = io(process.env.NEXT_PUBLIC_WS_URL!, {
      auth: { token: useAuthStore.getState().token },
    });

    newSocket.emit('subscribe', { jobId });

    newSocket.on('processing:update', (update: ProcessingUpdate) => {
      setUpdates((prev) => [...prev, update]);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, [jobId]);

  return { socket, updates };
}
```

---

## Routing Structure

### Public Routes
- `/` - Landing page
- `/login` - Login
- `/register` - Registration

### Protected Routes (require auth)
- `/projects` - Project list
- `/projects/new` - Create project
- `/projects/[id]` - Project details
- `/projects/[id]/documents` - Document management
- `/projects/[id]/schema` - Schema builder (chat)
- `/projects/[id]/test` - Test on sample
- `/projects/[id]/process` - Full processing
- `/projects/[id]/export` - Results & export

### Middleware Protection

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value;

  // Protect dashboard routes
  if (request.nextUrl.pathname.startsWith('/projects')) {
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url));
    }
  }

  // Redirect authenticated users from auth pages
  if (request.nextUrl.pathname.startsWith('/login') ||
      request.nextUrl.pathname.startsWith('/register')) {
    if (token) {
      return NextResponse.redirect(new URL('/projects', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

---

## UI/UX Design Guidelines

### Design System (based on 2025 best practices)

**Color Palette:**
```css
:root {
  /* Primary - Blue for trust and technology */
  --primary: 220 90% 56%;
  --primary-foreground: 0 0% 100%;

  /* Success - Green for correct extractions */
  --success: 142 76% 36%;

  /* Warning - Yellow for medium confidence */
  --warning: 38 92% 50%;

  /* Destructive - Red for errors/low confidence */
  --destructive: 0 84% 60%;

  /* Background */
  --background: 0 0% 100%;
  --foreground: 222 47% 11%;

  /* Muted for secondary content */
  --muted: 210 40% 96%;
  --muted-foreground: 215 16% 47%;
}
```

**Typography:**
- **Headings:** Inter or Geist Sans (modern, clean)
- **Body:** Same as headings for consistency
- **Code/Data:** JetBrains Mono (for data tables)

**Spacing:**
- Use Tailwind's spacing scale (4px base unit)
- Generous padding in conversational interface
- Compact data tables

### Conversational Interface Design

**Key Principles from 2025 Research:**

1. **Multi-modal Ready:** Design for text now, voice later
   - Large input area
   - Support for long-form responses
   - Markdown rendering

2. **Context Awareness:**
   - Show conversation history
   - Highlight extracted schema in sidebar
   - Allow users to jump back to any question

3. **Progressive Disclosure:**
   - Show examples/suggestions initially
   - Hide as conversation progresses
   - "Show examples" button always available

4. **Transparency:**
   - Live schema preview as it's being built
   - "What we've learned so far" panel
   - Clear indication of what's next

**Example Layout:**

```
┌────────────────────────────────────────────────────────────┐
│  Header: Project Name                             [Save]   │
├────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────┐   │
│  │                       │  │  Schema Preview          │   │
│  │   Chat Messages       │  │  ──────────────────────  │   │
│  │                       │  │  Variables:              │   │
│  │  🤖 What are you      │  │  ✓ Date                  │   │
│  │     researching?      │  │  ✓ Location              │   │
│  │                       │  │  ✓ Participants          │   │
│  │  👤 Climate protests  │  │  ⚪ Violence (pending)    │   │
│  │                       │  │                          │   │
│  │  🤖 What information  │  │  Classifications:        │   │
│  │     do you need?      │  │  ✓ Protest type          │   │
│  │                       │  │                          │   │
│  │  👤 Date, location... │  │  [Test on Sample]        │   │
│  │                       │  │                          │   │
│  │                       │  │                          │   │
│  └──────────────────────┘  └──────────────────────────┘   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │  Type your response...                  [Send] ➤  │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

### Data Table Design

**Best Practices from 2025:**

1. **Confidence-First Design:**
   - Confidence dots in first column
   - Color-coded (green/yellow/red)
   - Sort by confidence by default

2. **Progressive Disclosure:**
   - Show 5-7 columns initially
   - "Show more columns" option
   - Customizable column visibility

3. **Source Linking:**
   - Click any cell → see source document
   - Highlight relevant text
   - Side-by-side comparison view

**Example Layout:**

```
┌────────────────────────────────────────────────────────────────┐
│  Extracted Data (127 documents)              [Export ▾] [⚙]   │
├────────────────────────────────────────────────────────────────┤
│  🟢 92% │ doc_001.pdf │ 2024-03-15 │ Berlin │ 5000 │ Climate...│
│  🟢 95% │ doc_002.pdf │ 2024-03-20 │ Paris  │ 3200 │ Fossil...│
│  🟡 78% │ doc_003.pdf │ 2024-04-01 │ London │ 1500 │ Deforest..│
│  🔴 65% │ doc_004.pdf │ Unknown    │ Madrid │ Unknown │ ...   │
│  🟢 91% │ doc_005.pdf │ 2024-04-10 │ Rome   │ 2100 │ Climate...│
│  ...                                                           │
└────────────────────────────────────────────────────────────────┘
     ↑        ↑             ↑           ↑         ↑          ↑
  Conf.    Document      Date      Location   Participants  Topic
```

---

## Performance Optimization

### Code Splitting
- Route-based splitting (automatic with Next.js App Router)
- Component lazy loading for heavy components
- Dynamic imports for modals and dialogs

### Image Optimization
- Use Next.js `<Image>` component
- Lazy loading
- Responsive images

### Data Fetching
- Server Components for initial data
- Client Components with React Query for dynamic data
- Prefetching on hover for navigation

### Bundle Size
- Use tree-shakeable libraries
- Avoid large dependencies
- Code splitting for non-critical features

---

## Testing Strategy

### Unit Tests (Vitest)
```typescript
// components/__tests__/ChatInput.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from '../chat/ChatInput';

describe('ChatInput', () => {
  it('should call onSend when message is submitted', () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} />);

    const input = screen.getByPlaceholderText('Type your response...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.submit(input.closest('form')!);

    expect(onSend).toHaveBeenCalledWith('Test message');
  });
});
```

### Integration Tests (Playwright)
```typescript
// e2e/project-creation.spec.ts
import { test, expect } from '@playwright/test';

test('should create new project and upload documents', async ({ page }) => {
  await page.goto('/projects/new');

  await page.fill('[name="name"]', 'Test Project');
  await page.fill('[name="description"]', 'Test description');
  await page.click('button[type="submit"]');

  await expect(page).toHaveURL(/\/projects\/[a-z0-9-]+/);
  await expect(page.locator('h1')).toContainText('Test Project');
});
```

---

## Deployment

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

```bash
# .env.production
NEXT_PUBLIC_API_URL=https://api.yourapp.com
NEXT_PUBLIC_WS_URL=wss://api.yourapp.com
NEXT_PUBLIC_APP_URL=https://yourapp.com
```

### Build & Deploy

**Development:**
```bash
npm run dev
```

**Production Build:**
```bash
npm run build
npm run start
```

**Deploy to Vercel (Recommended):**
```bash
vercel --prod
```

---

## Next Steps

1. **Set up Next.js project** with TypeScript and Tailwind
2. **Install core dependencies** (shadcn/ui, TanStack Query, Zustand)
3. **Create base layout** and routing structure
4. **Implement authentication** pages and flow
5. **Build ChatInterface** component
6. **Connect to backend** API

---

**Document Status:** READY FOR IMPLEMENTATION
