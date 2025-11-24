# Quickstart: Frontend Development

**Feature**: 001-complete-user-workflow
**Goal**: Get the frontend development environment running in < 10 minutes
**Scope**: Frontend only (Phase 1) - No backend required

## Prerequisites

- **Node.js**: v20+ (check with `node --version`)
- **npm**: v10+ (check with `npm --version`)
- **Git**: Installed and configured
- **Code Editor**: VS Code recommended (with TypeScript extensions)

## Step 1: Initial Setup (2 minutes)

```bash
# Navigate to project root
cd /home/noahdarwich/code/coderAI

# Create frontend directory if it doesn't exist
mkdir -p frontend
cd frontend

# Initialize Next.js 15 project
npx create-next-app@latest . --typescript --tailwind --app --src-dir --import-alias "@/*" --no-git --yes

# Install additional dependencies
npm install zustand @tanstack/react-query @tanstack/react-table react-dropzone zod react-hook-form @hookform/resolvers date-fns
```

## Step 2: Install shadcn/ui (3 minutes)

```bash
# Initialize shadcn/ui
npx shadcn@latest init

# Select the following options when prompted:
# - Style: Default
# - Base color: Slate
# - CSS variables: Yes

# Install required shadcn/ui components
npx shadcn@latest add button card dialog form input select table tabs toast progress badge dropdown-menu separator
```

## Step 3: Project Structure Setup (2 minutes)

```bash
# Create directory structure
cd src
mkdir -p app/\(dashboard\)/projects/\[id\]/{documents,schema/review,process,results}
mkdir -p components/{ui,workflow/{step1,step2,step3,step4,step5},layout}
mkdir -p lib services types mocks store

# Create empty files
touch services/api.ts services/mockApi.ts
touch types/{index,project,document,schema,extraction,processing,export,api}.ts
touch mocks/{projects,documents,schemas,extractions,processingJobs,README}.ts
touch store/{projectStore,workflowStore,schemaWizardStore}.ts
```

## Step 4: Configure TypeScript (1 minute)

Edit `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "preserve",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowJs": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "incremental": true,
    "paths": {
      "@/*": ["./src/*"]
    },
    "plugins": [
      {
        "name": "next"
      }
    ]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

## Step 5: Run Development Server (1 minute)

```bash
# Start dev server
npm run dev

# Open browser to http://localhost:3000
# You should see the Next.js welcome page
```

## Development Workflow

### File Organization

```
src/
├── app/                           # Pages (Next.js App Router)
│   ├── (dashboard)/               # Dashboard route group
│   │   ├── projects/
│   │   │   ├── page.tsx           # Projects list
│   │   │   └── [id]/              # Dynamic project routes
│   │   │       ├── page.tsx       # Project overview
│   │   │       ├── documents/page.tsx     # Step 1
│   │   │       ├── schema/
│   │   │       │   ├── page.tsx           # Step 2
│   │   │       │   └── review/page.tsx    # Step 3
│   │   │       ├── process/page.tsx       # Step 4
│   │   │       └── results/page.tsx       # Step 5
│   │   └── layout.tsx             # Dashboard layout
│   ├── layout.tsx                 # Root layout
│   └── page.tsx                   # Home/landing page
├── components/
│   ├── ui/                        # shadcn/ui components
│   ├── workflow/                  # Workflow-specific components
│   │   ├── step1/                 # Project setup components
│   │   ├── step2/                 # Schema wizard components
│   │   ├── step3/                 # Schema review components
│   │   ├── step4/                 # Processing components
│   │   └── step5/                 # Results & export components
│   └── layout/                    # Layout components (nav, progress, etc.)
├── lib/                           # Utilities
├── services/                      # API layer
│   ├── api.ts                     # Main API interface (what components use)
│   └── mockApi.ts                 # Mock implementation (Phase 1)
├── types/                         # TypeScript interfaces
├── mocks/                         # Mock data
└── store/                         # Zustand stores
```

### Component Development Pattern

1. **Create TypeScript interfaces first** (in `types/`)
2. **Create mock data** (in `mocks/`)
3. **Build UI component** (in `components/workflow/`)
4. **Connect to mock API** (via `services/api.ts`)
5. **Add to page** (in `app/`)

### Example: Creating a New Component

```typescript
// 1. Define type (types/project.ts)
export interface Project {
  id: string;
  name: string;
  // ...
}

// 2. Create mock data (mocks/projects.ts)
export const mockProjects: Project[] = [
  { id: '1', name: 'Climate Study' },
  // ...
];

// 3. Create component (components/workflow/step1/ProjectList.tsx)
'use client';

import { useEffect, useState } from 'react';
import { api } from '@/services/api';
import { Project } from '@/types';
import { Card } from '@/components/ui/card';

export function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    api.projects.list().then(response => {
      if (response.data) {
        setProjects(response.data);
      }
    });
  }, []);

  return (
    <div className="grid gap-4">
      {projects.map(project => (
        <Card key={project.id}>
          <h3>{project.name}</h3>
        </Card>
      ))}
    </div>
  );
}

// 4. Use in page (app/(dashboard)/projects/page.tsx)
import { ProjectList } from '@/components/workflow/step1/ProjectList';

export default function ProjectsPage() {
  return (
    <main className="container py-8">
      <h1 className="text-3xl font-bold mb-8">My Projects</h1>
      <ProjectList />
    </main>
  );
}
```

## Testing Your Work

### Manual Testing Checklist

For each workflow step you implement:

- [ ] Page loads without errors
- [ ] TypeScript has no errors (`npm run build`)
- [ ] Components display correctly on desktop (1920x1080)
- [ ] Components are responsive on tablet (768px)
- [ ] Keyboard navigation works (Tab, Enter, Space)
- [ ] Loading states appear during async operations
- [ ] Error states display when mocked
- [ ] Data persists across page refreshes (localStorage)

### Run TypeScript Check

```bash
npm run build
# Should complete with 0 errors
```

### Run Development Server

```bash
npm run dev
# Navigate to http://localhost:3000
```

## Common Issues & Solutions

### Issue: "Module not found" errors

**Solution**: Check import paths use `@/` alias:
```typescript
// ❌ Wrong
import { api } from '../services/api';

// ✅ Correct
import { api } from '@/services/api';
```

### Issue: TypeScript errors in components

**Solution**: Ensure types are exported from `types/index.ts`:
```typescript
// types/index.ts
export * from './project';
export * from './document';
// ...
```

### Issue: shadcn/ui components not found

**Solution**: Re-run component installation:
```bash
npx shadcn@latest add button
```

### Issue: Styles not applying

**Solution**: Check `tailwind.config.ts` includes all paths:
```typescript
content: [
  './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  './src/components/**/*.{js,ts,jsx,tsx,mdx}',
],
```

## Next Steps

Once environment is running:

1. **Read the spec**: `specs/001-complete-user-workflow/spec.md`
2. **Review data models**: `specs/001-complete-user-workflow/data-model.md`
3. **Start with Step 1**: Implement project setup and document upload
4. **Use mock data**: Reference `mocks/` for realistic data
5. **Follow USER_WORKFLOW.md**: Ensure UI matches the canonical workflow

## Development Tips

- **Start simple**: Build basic version first, add polish later
- **Use shadcn/ui**: Don't build components from scratch
- **Mock everything**: All API calls should work with mock data
- **Test frequently**: Check TypeScript errors often (`npm run build`)
- **Commit early**: Small, frequent commits are better than large ones
- **Reference constitution**: Ensure compliance with Phase 1 principles

## Deployment (Optional)

Deploy to Vercel for live preview:

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel

# Follow prompts to link project and deploy
```

Your frontend will be live at a Vercel URL within 2 minutes!

## Resources

- **Next.js Docs**: https://nextjs.org/docs
- **shadcn/ui Docs**: https://ui.shadcn.com/
- **Tailwind CSS Docs**: https://tailwindcss.com/docs
- **Zustand Docs**: https://zustand-demo.pmnd.rs/
- **TanStack Query Docs**: https://tanstack.com/query/latest
- **React Hook Form**: https://react-hook-form.com/

## Summary

You should now have:
- ✅ Next.js 15 + React 19 + TypeScript running
- ✅ shadcn/ui components installed
- ✅ Project structure created
- ✅ Development server running on http://localhost:3000
- ✅ Ready to implement workflow steps

**Total setup time**: ~10 minutes

**Next action**: Start implementing Step 1 (Project Setup & Document Upload)
