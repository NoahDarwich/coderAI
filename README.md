# Research Automation Tool - Implementation Documentation

**Status:** ✅ Frontend MVP Complete with Full 5-Step Workflow
**Branch:** master (merged from 001-complete-user-workflow)
**Last Updated:** November 25, 2025

---

## 📚 Documentation Overview

This repository contains comprehensive documentation for building an AI-powered research automation tool that enables researchers to extract structured data from qualitative documents through conversational AI.

### Quick Navigation

| Document | Purpose | Use When |
|----------|---------|----------|
| **[CONCEPT.md](CONCEPT.md)** | Complete product vision & strategy | Understanding the big picture |
| **[MVP-SPEC.md](MVP-SPEC.md)** ⭐ | 3-4 month MVP specification | Planning development |
| **[FRONTEND-DESIGN.md](FRONTEND-DESIGN.md)** ⭐ | Frontend technical architecture | Building the UI |
| **[TECH-STACK-DECISION.md](TECH-STACK-DECISION.md)** ⭐ | Technology choices with rationale | Making tech decisions |
| **[API-SPECIFICATION.md](API-SPECIFICATION.md)** ⭐ | Complete REST API & WebSocket spec | Building frontend/backend |

⭐ = Essential for immediate implementation

---

## 🎯 What We're Building

### The Problem
Researchers spend weeks to months manually extracting structured data from documents. Traditional tools either:
- Have fixed schemas (GDELT, ICEWS)
- Require manual coding (ATLAS.ti, NVivo)
- Need programming skills (custom Python scripts)

### The Solution
A conversational AI system where researchers:
1. **Chat** with AI to define what data they need
2. **Upload** their documents (PDF, DOCX, TXT)
3. **Review** sample extractions and refine
4. **Process** all documents automatically
5. **Export** structured dataset (CSV)

**Time savings:** Weeks → Hours
**Accuracy:** 85-99%+ (with confidence scores)
**Skill required:** None - just conversation

---

## 🚀 MVP Scope (3-4 Months)

### What's IN ✅
- Conversational schema definition (natural language)
- Document upload & parsing (PDF, DOCX, TXT)
- Multi-agent extraction system (dates, locations, entities, custom variables)
- Testing on sample documents (10-20 docs)
- Full batch processing with progress tracking
- CSV export (wide or long format)
- Basic user accounts & project management

### What's OUT (Future) ❌
- Adaptive learning from corrections (Phase 2)
- Emergent theme discovery (Phase 2)
- Multiple export formats - Excel, JSON (Phase 2)
- Collaboration features (Phase 3+)
- Mobile interface (Phase 3+)
- Real-time monitoring pipelines (Phase 3+)

**See [MVP-SPEC.md](MVP-SPEC.md) for complete scope and user journey.**

---

## 🏗️ Architecture Overview

### Tech Stack (Recommended)

```yaml
Frontend:
  - Next.js 15 + React 19 + TypeScript
  - Tailwind CSS + shadcn/ui
  - Vercel (deployment)
  - Cost: Free (Hobby tier)

Backend:
  - FastAPI (Python 3.11+)
  - PostgreSQL 15 + Redis 7
  - Railway.app (deployment)
  - Cost: $20/month

LLM:
  - LangGraph (orchestration)
  - OpenAI GPT-4o (primary)
  - Anthropic Claude 3.5 Sonnet (secondary)
  - Cost: $50-150/month (usage-based)

Total MVP Cost: $70-170/month
```

### System Diagram

```
┌─────────────────────────────────────────────────┐
│  Frontend (Next.js)                             │
│  • Chat UI (schema builder)                     │
│  • Document uploader                            │
│  • Results viewer & export                      │
└────────────────┬────────────────────────────────┘
                 │ REST API + WebSocket
┌────────────────▼────────────────────────────────┐
│  Backend (FastAPI)                              │
│  • API routes                                   │
│  • Conversational AI orchestrator               │
│  • Multi-agent extraction (LangGraph)           │
│  • Document processing pipeline                 │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  Storage & Queue                                │
│  • PostgreSQL (data)                            │
│  • Redis (cache, queue)                         │
│  • Celery (background jobs)                     │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│  LLM APIs                                       │
│  • OpenAI GPT-4o                                │
│  • Anthropic Claude 3.5 Sonnet                  │
└─────────────────────────────────────────────────┘
```

**See [FRONTEND-DESIGN.md](FRONTEND-DESIGN.md) and [TECH-STACK-DECISION.md](TECH-STACK-DECISION.md) for details.**

---

## 📋 Development Timeline

### Month 1: Foundation
- **Week 1-2:** Project setup, backend structure, auth, database
- **Week 3-4:** Document upload, parsing, storage

**Deliverable:** Can upload and store documents

### Month 2: AI & LLM Integration
- **Week 5-6:** Conversational system, question generation
- **Week 7-8:** Multi-agent extraction, confidence scoring

**Deliverable:** Can extract data from documents via CLI/API

### Month 3: Frontend
- **Week 9-10:** UI setup, auth pages, document interface, chat UI
- **Week 11-12:** Results viewer, export functionality

**Deliverable:** Full web application UI

### Month 4: Integration & Polish
- **Week 13-14:** Connect frontend ↔ backend, WebSocket, job queue
- **Week 15-16:** Testing, bug fixes, deployment, beta users

**Deliverable:** Production-ready MVP

**See [MVP-SPEC.md](MVP-SPEC.md) for detailed task breakdown.**

---

## 🎨 Key Features

### 1. Conversational Schema Builder

**User Experience:**
```
🤖 AI: "What are you researching?"
👤 User: "Climate protests in Europe"

🤖 AI: "What information do you need to extract?"
👤 User: "Date, location, participants, topic, whether violent"

🤖 AI: "How should I classify the topic?"
👤 User: "Categories: Climate policy, Fossil fuels, Deforestation"

✅ Schema generated automatically
```

**Behind the scenes:**
- AI generates extraction prompts for each variable
- Creates specialized agents (date extractor, location extractor, etc.)
- Builds classification logic
- User never sees technical complexity

### 2. Multi-Agent Extraction

**Specialized Agents:**
- **Orchestrator:** Coordinates workflow
- **Date Extractor:** Finds and normalizes dates
- **Location Extractor:** Extracts geographic entities
- **Entity Extractor:** People, organizations
- **Custom Variable Extractor:** User-defined fields
- **Classifier:** Categorizes data
- **Validator:** Confidence scoring

**Performance:**
- Parallel processing where possible
- Confidence score per extraction
- Source text tracking for verification

### 3. Testing & Refinement Workflow

1. **Test on sample** (10-20 documents)
2. **Review results** side-by-side with source
3. **Flag errors** with simple ✓/✗ buttons
4. **Refine definitions** via continued conversation
5. **Re-test** until satisfied
6. **Approve** for full processing

**Result:** 85%+ accuracy before full processing starts

### 4. Results & Export

**Data Review Interface:**
- Sortable, filterable table
- Confidence indicators (🟢 🟡 🔴)
- Click cell → see source document
- Flag for manual review
- Filter by confidence threshold

**Export Options:**
- **Format:** CSV (Excel & JSON in Phase 2)
- **Structure:** Wide (1 row/doc) or Long (1 row/field)
- **Include:** Confidence scores, source text (optional)
- **Filter:** Minimum confidence, exclude flagged

---

## 💡 Why This Tech Stack?

### FastAPI (Backend)
✅ **Best Python web framework for APIs (2025)**
- 20K-30K requests/second (async)
- Automatic API docs (Swagger)
- Perfect for LLM integration
- Reuses existing Python code

❌ **Why not Django?**
- Too heavy, slower (5-10K req/sec)
- Overkill for API-only backend

❌ **Why not Node.js?**
- Would lose existing Python code
- Weaker AI/ML libraries

### Next.js (Frontend)
✅ **Most popular React framework (2025)**
- Huge ecosystem, best docs
- Server Components (smaller bundles)
- File-based routing (fast dev)
- Vercel deployment (free)

❌ **Why not Vue/Svelte?**
- Smaller ecosystems
- Fewer UI component libraries
- Harder to hire developers

### LangGraph (LLM Orchestration)
✅ **Industry standard for multi-agent systems**
- Built for stateful workflows
- Graph-based (intuitive)
- Excellent debugging tools
- LangChain ecosystem

❌ **Why not custom?**
- Reinventing the wheel
- Months of extra work
- No debugging tools

### PostgreSQL (Database)
✅ **Rock-solid relational database**
- ACID compliance (data integrity)
- Excellent JSON support (JSONB)
- Your data is mostly structured
- Full-text search built-in

❌ **Why not MongoDB?**
- No advantage for structured data
- Harder to model relationships
- PostgreSQL JSONB handles flexibility

**See [TECH-STACK-DECISION.md](TECH-STACK-DECISION.md) for complete analysis.**

---

## 🔌 API Overview

### Key Endpoints

```http
# Authentication
POST   /auth/register
POST   /auth/login
GET    /auth/me

# Projects
GET    /projects
POST   /projects
GET    /projects/{id}
DELETE /projects/{id}

# Documents
POST   /projects/{id}/documents       # Upload
GET    /projects/{id}/documents       # List
DELETE /projects/{id}/documents/{id}  # Delete

# Schema (Conversation)
POST   /projects/{id}/schema/conversation       # Start chat
POST   /projects/{id}/schema/conversation/messages  # Send message
GET    /projects/{id}/schema                    # Get generated schema
POST   /projects/{id}/schema/approve            # Approve for use

# Extraction
POST   /projects/{id}/extraction/sample  # Test on sample
POST   /projects/{id}/extraction/full    # Process all
GET    /projects/{id}/extraction/jobs/{job_id}  # Status
GET    /projects/{id}/extraction/results # Get results

# Export
POST   /projects/{id}/export           # Create export
GET    /projects/{id}/exports/{id}     # Status
GET    /projects/{id}/exports/{id}/download  # Download
```

### WebSocket Events

```javascript
// Subscribe to job progress
socket.emit('subscribe:job', { job_id });

// Receive updates
socket.on('job:progress', ({ completed, total, percentage }));
socket.on('job:completed', ({ results_count }));
socket.on('job:error', ({ error }));
```

**See [API-SPECIFICATION.md](API-SPECIFICATION.md) for complete reference.**

---

## 📊 Success Metrics

### Technical Validation
- ✓ Extract 4-6 variable types successfully
- ✓ Process 100 documents in < 2 hours
- ✓ Extraction accuracy > 85%
- ✓ System uptime > 95%

### User Validation (Beta Testing)
- ✓ 5 researchers complete end-to-end workflow
- ✓ Average satisfaction > 7/10
- ✓ Time savings > 70% vs manual
- ✓ No technical support needed

### Business Validation
- ✓ MVP deployed and accessible
- ✓ Operating costs < $200/month
- ✓ Path to monetization identified

---

## ⚠️ Key Risks & Mitigations

### Risk 1: LLM Accuracy
**Mitigation:**
- Confidence scoring highlights uncertainty
- Sample testing before full processing
- Manual review for low-confidence items
- Multi-agent cross-validation

### Risk 2: Scope Creep
**Mitigation:**
- Strict MVP boundaries documented
- Park all extra features for Phase 2
- Weekly scope reviews

### Risk 3: LLM API Costs
**Mitigation:**
- Aggressive caching
- Use cheaper models where appropriate
- Set per-user usage limits
- Daily cost monitoring

### Risk 4: Integration with Existing Code
**Mitigation:**
- Week 1: Audit existing Python code
- Identify reusable components
- Refactor incrementally
- Don't force integration if major rewrite needed

---

## 🏁 Next Steps

### Before Starting Development

1. **Review all documentation** - Ensure understanding of scope and architecture

2. **Answer these questions:**
   - What exists in current Python codebase?
   - What can be reused vs. rebuilt?
   - OpenAI/Anthropic API keys available?
   - Comfortable with Railway/Render or need AWS?

3. **Set up development environment:**
   - GitHub repository
   - Development branches (main, develop)
   - CI/CD pipeline
   - Environment variables

4. **Create detailed technical designs:**
   - Database schema (expand on API spec)
   - Component hierarchy (expand on frontend design)
   - Agent workflow diagrams
   - Error handling strategy

### Week 1 Action Items

**Backend:**
- [ ] Set up FastAPI project structure
- [ ] Configure PostgreSQL + Redis (Railway)
- [ ] Implement user auth (JWT)
- [ ] Create basic CRUD endpoints
- [ ] Set up Celery for background jobs

**Frontend:**
- [ ] Set up Next.js project
- [ ] Configure Tailwind CSS
- [ ] Install shadcn/ui components
- [ ] Create basic layouts
- [ ] Implement auth pages

**DevOps:**
- [ ] Set up Railway/Render accounts
- [ ] Configure environment variables
- [ ] Set up GitHub Actions for CI/CD
- [ ] Configure Vercel for frontend

---

## 🤝 Questions to Resolve

### About Existing Python Code
1. What components exist? (Document parsing? LLM integration? Extraction logic?)
2. What can be reused as-is?
3. What needs refactoring?
4. Code quality? (Tests? Documentation? Organization?)

### Product Decisions
1. **Authentication:** Email/password only, or social login (Google/GitHub)?
2. **LLM provider:** OpenAI only, Anthropic only, or both?
3. **Deployment:** Cloud-only or self-hosted option eventually?
4. **Pricing model:** How to monetize? (impacts resource limits)

### Technical Decisions
1. **Caching strategy:** What to cache? How long?
2. **Error handling:** Retry logic for LLM failures?
3. **Monitoring:** What metrics to track?
4. **Logging:** What level of detail?

---

## 📞 Getting Help

### Documentation Questions
- Re-read the specific focused document
- Check the [CONCEPT.md](CONCEPT.md) for strategic context
- Review the [MVP-SPEC.md](MVP-SPEC.md) for scope clarification

### Technical Questions
- **Frontend:** See [FRONTEND-DESIGN.md](FRONTEND-DESIGN.md)
- **Backend/API:** See [API-SPECIFICATION.md](API-SPECIFICATION.md)
- **Tech Stack:** See [TECH-STACK-DECISION.md](TECH-STACK-DECISION.md)

### Implementation Questions
- Review architecture diagrams
- Check code examples in documentation
- Consider if question is in scope for MVP

---

## 📈 Post-MVP Roadmap

### Phase 2 (Months 5-8)
- Adaptive learning from user corrections
- Automatic prompt adjustment
- Theme extraction (emergent themes)
- Advanced validation & quality control
- Multiple export formats (Excel, JSON)

### Phase 3+ (Months 9+)
- Collaboration features (team workspaces)
- Template library & schema sharing
- Real-time monitoring pipelines
- Multi-lingual support
- API for programmatic access
- Mobile interface

**See [CONCEPT.md](CONCEPT.md) Section 7 for complete roadmap.**

---

## 🎓 Learning Resources

### Recommended Reading

**FastAPI:**
- Official docs: https://fastapi.tiangolo.com/
- Tutorial: Build a full FastAPI app

**Next.js:**
- Official docs: https://nextjs.org/docs
- App Router tutorial

**LangGraph:**
- Official docs: https://langchain-ai.github.io/langgraph/
- Multi-agent tutorials

**LLM Best Practices:**
- OpenAI prompt engineering guide
- Anthropic prompt engineering guide

### Example Projects
- Look for FastAPI + Next.js starter templates
- Study multi-agent LLM examples
- Review document processing pipelines

---

## 📝 Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| README.md | ✅ Complete | Nov 18, 2025 |
| MVP-SPEC.md | ✅ Complete | Nov 18, 2025 |
| FRONTEND-DESIGN.md | ✅ Complete | Nov 18, 2025 |
| TECH-STACK-DECISION.md | ✅ Complete | Nov 18, 2025 |
| API-SPECIFICATION.md | ✅ Complete | Nov 18, 2025 |
| CONCEPT.md | ✅ Updated | Nov 18, 2025 |

**All documents are ready for implementation.**

---

## 🚀 Let's Build!

You now have:
- ✅ Clear product vision
- ✅ Focused MVP scope (3-4 months)
- ✅ Detailed technical specifications
- ✅ Complete API design
- ✅ Technology decisions with rationale
- ✅ Development timeline

**Next action:** Review all docs → Answer open questions → Start Week 1 development

**Questions?** Re-read the relevant focused document or the complete [CONCEPT.md](CONCEPT.md).

---

**Version:** 1.0
**Status:** READY FOR DEVELOPMENT
**Target Completion:** 3-4 months from start
