# Research Automation Tool - MVP Specification (3-4 Month Timeline)

**Version:** 1.0
**Target Completion:** 3-4 months
**Last Updated:** November 18, 2025

---

## Executive Summary

This MVP focuses on delivering **core value** quickly: enabling researchers to define extraction schemas through conversation and automatically extract structured data from documents. We're deliberately excluding advanced features to hit a 3-4 month timeline.

### MVP Value Proposition
"Transform weeks of manual document coding into hours through conversational AI - without writing a single line of code."

---

## What's IN the MVP (Must-Have)

### 1. **Conversational Schema Definition** ✓
- Natural language conversation to define research goals
- AI asks clarifying questions about:
  - Research topic and context
  - Variables to extract (dates, locations, actors, events)
  - Classification schemes (binary, categorical)
- Generates extraction prompts automatically
- **Scope limit:** Simple variables only (no complex nested structures in MVP)

### 2. **Document Upload & Management** ✓
- Upload documents via:
  - File upload (PDF, DOCX, TXT)
  - Paste text directly
- Basic document library:
  - View uploaded documents
  - Delete documents
  - Document count and status
- **Scope limit:** Max 100 documents per project in MVP

### 3. **Multi-Agent Extraction System** ✓
- **Orchestrator agent:** Coordinates extraction workflow
- **Specialized extraction agents:**
  - Date/time extractor
  - Location extractor
  - Entity extractor (people, organizations)
  - Custom variable extractor (user-defined)
  - Basic classifier (categorical)
- Confidence scoring for each extraction
- **Scope limit:** Sequential processing only (no complex parallel optimization)

### 4. **Testing & Review Interface** ✓
- Sample processing (10-20 documents)
- Side-by-side view:
  - Source document text
  - Extracted data
  - Confidence scores
- Simple error flagging: ✓ correct / ✗ incorrect
- Re-run extraction on sample after adjustments
- **Scope limit:** No automatic prompt adjustment - manual refinement only

### 5. **Full Processing** ✓
- Process all documents with approved extraction logic
- Progress tracking
- Basic error logging
- **Scope limit:** Batch processing without advanced optimization

### 6. **Data Export** ✓
- CSV export only
- Structure options:
  - Wide format (one row per document)
  - Long format (one row per extracted item)
- Include confidence scores (optional)
- **Scope limit:** CSV only, no Excel/JSON in MVP

### 7. **Basic User System** ✓
- User registration and login
- Simple project management:
  - Create project
  - View projects
  - Delete project
- **Scope limit:** Single-user projects only (no collaboration)

---

## What's OUT of the MVP (Future Phases)

### Phase 2 (Months 5-8)
- ❌ Adaptive learning from corrections
- ❌ Automatic prompt adjustment
- ❌ Theme extraction (emergent themes)
- ❌ Advanced validation and quality control
- ❌ Multiple export formats (Excel, JSON)
- ❌ Advanced analytics and visualizations

### Phase 3+ (Months 9+)
- ❌ Collaboration features
- ❌ Template library
- ❌ Real-time monitoring
- ❌ Multi-lingual support
- ❌ API access
- ❌ Advanced relationship extraction
- ❌ Mobile interface

---

## MVP User Journey

### Step 1: Create Project (2 minutes)
1. User signs up / logs in
2. Clicks "New Project"
3. Enters project name and description

### Step 2: Upload Documents (5 minutes)
1. Upload documents (drag & drop or file browser)
2. System parses and previews documents
3. User confirms document list

### Step 3: Define Schema via Conversation (10-15 minutes)
**AI:** "What is your research about?"
**User:** "I'm studying climate protests in Europe"

**AI:** "What specific information do you need to extract?"
**User:** "Date, location, number of participants, what they're protesting about, whether there was violence"

**AI:** "How should I classify the protest topic?"
**User:** "Categories: Climate policy, Fossil fuels, Deforestation, General environmental"

**AI:** "How should I classify violence?"
**User:** "Yes or No - violence means physical confrontation or property damage"

**System generates:** Extraction configuration ready for testing

### Step 4: Test on Sample (10 minutes)
1. System processes 10-20 sample documents
2. User reviews extracted data in table view
3. User flags any errors
4. User can refine definitions and re-run

### Step 5: Full Processing (30 minutes - 2 hours depending on scale)
1. User approves sample results
2. System processes all documents
3. Progress bar shows status
4. User receives notification when complete

### Step 6: Review & Export (5 minutes)
1. Browse complete dataset
2. Filter and sort results
3. Review flagged low-confidence items (optional)
4. Export to CSV

**Total Time Investment:** ~1-2 hours for setup + processing time
**vs. Manual Coding:** Weeks to months

---

## Technical Architecture (MVP)

### Frontend Stack Recommendation

**Recommended: React + TypeScript + Next.js**

**Rationale:**
- **React:** Most mature ecosystem, extensive component libraries
- **TypeScript:** Type safety prevents bugs, better developer experience
- **Next.js:**
  - Built-in API routes for backend integration
  - Server-side rendering for better UX
  - File-based routing (faster development)
  - Excellent documentation

**Alternative (if Python backend preferred):** Vue 3 + TypeScript + Vite
- Simpler learning curve
- Faster build times
- Good for smaller teams

### Backend Stack Recommendation

**Recommended: Python + FastAPI**

**Rationale:**
- **Leverage existing Python code** from your partial pipeline
- **FastAPI:**
  - Modern async framework (excellent performance)
  - Automatic API documentation (Swagger)
  - Type hints with Pydantic
  - WebSocket support for real-time updates
  - Fastest Python framework
- **Python AI ecosystem:**
  - LangChain / LlamaIndex for LLM orchestration
  - OpenAI SDK / Anthropic SDK
  - PyPDF2, python-docx for document parsing
  - Pandas for data manipulation

**Why NOT Node.js for backend:**
- You have existing Python code
- Python's AI/ML libraries are superior
- Document processing libraries more mature

### Database

**Recommended: PostgreSQL + Redis**

**PostgreSQL for:**
- User accounts
- Projects
- Document metadata
- Extracted data
- Structured relational data

**Redis for:**
- Session management
- Job queue (background processing)
- Caching LLM responses
- Real-time progress updates

**Why NOT MongoDB:**
- Data is mostly structured for MVP
- PostgreSQL JSON support sufficient
- Better for transactional integrity

### LLM Integration

**Recommended: Multi-provider with LangGraph**

**LLM Providers (start with both):**
- **OpenAI GPT-4o:** Fast, cost-effective, excellent for structured extraction
- **Anthropic Claude 3.5 Sonnet:** Better at nuanced understanding, longer context

**Orchestration:**
- **LangGraph:** Best framework for multi-agent systems (2025 standard)
  - Built by LangChain team
  - Stateful agent orchestration
  - Easy to visualize agent flows
  - Great debugging tools

**Alternative:** AutoGen (Microsoft)
- More mature but less flexible
- Good for simpler use cases

### Infrastructure (MVP)

**Recommended: Railway or Render**

**Why NOT AWS/GCP for MVP:**
- Too complex for 3-4 month timeline
- Overkill for initial scale
- Expensive to maintain

**Railway.app:**
- Excellent for FastAPI + PostgreSQL + Redis
- One-click deployment
- Automatic HTTPS
- Environment variables management
- $5-20/month initially
- Easy scaling path

**Render.com (alternative):**
- Similar to Railway
- Good free tier for testing
- Automatic deploys from GitHub

### Job Queue

**Recommended: Celery + Redis**

**Rationale:**
- Industry standard for Python async tasks
- Perfect for document processing jobs
- Built-in retry logic
- Progress tracking
- Can scale to distributed workers later

---

## MVP Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js + React)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Chat UI     │  │  Document    │  │  Data Review       │  │
│  │  (Schema     │  │  Upload      │  │  & Export          │  │
│  │   Builder)   │  │  Manager     │  │  Interface         │  │
│  └──────────────┘  └──────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓ REST API + WebSocket
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI + Python)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            API Layer (FastAPI Routes)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Conversational AI Orchestrator                          │  │
│  │  • Question generator                                    │  │
│  │  • Response interpreter                                  │  │
│  │  • Prompt builder                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Multi-Agent Extraction System (LangGraph)               │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │  │
│  │  │Orchestr. │ │Date      │ │Location  │ │Entity    │  │  │
│  │  │Agent     │ │Extractor │ │Extractor │ │Extractor │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │  │
│  │  ┌──────────┐ ┌──────────────────────────────────────┐ │  │
│  │  │Custom    │ │Validator Agent                       │ │  │
│  │  │Variable  │ │(Confidence scoring)                  │ │  │
│  │  └──────────┘ └──────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Document Processing Pipeline                            │  │
│  │  • PDF/DOCX parser • Text extraction • Chunking         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              JOB QUEUE (Celery + Redis)                          │
│  • Async document processing                                    │
│  • Progress tracking                                            │
│  • Error handling & retry                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE (PostgreSQL)                               │
│  • Users & Authentication                                       │
│  • Projects                                                     │
│  • Documents                                                    │
│  • Extraction Schemas                                           │
│  • Extracted Data                                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              LLM APIS (OpenAI + Anthropic)                       │
│  • GPT-4o for structured extraction                             │
│  • Claude 3.5 Sonnet for nuanced understanding                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Models (MVP)

### User
```python
{
  "id": "uuid",
  "email": "string",
  "hashed_password": "string",
  "created_at": "timestamp",
  "last_login": "timestamp"
}
```

### Project
```python
{
  "id": "uuid",
  "user_id": "uuid",
  "name": "string",
  "description": "string",
  "status": "enum[draft, processing, completed]",
  "schema_config": "json",  # Extraction configuration
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Document
```python
{
  "id": "uuid",
  "project_id": "uuid",
  "filename": "string",
  "content": "text",
  "file_type": "enum[pdf, docx, txt]",
  "status": "enum[uploaded, parsed, processing, completed, error]",
  "uploaded_at": "timestamp"
}
```

### ExtractionSchema
```python
{
  "id": "uuid",
  "project_id": "uuid",
  "conversation_history": "json[]",  # Chat messages
  "variables": "json[]",  # [{name, type, description, prompt}]
  "classifications": "json[]",  # [{name, categories, prompt}]
  "prompts": "json",  # Generated prompts for each agent
  "version": "integer",
  "created_at": "timestamp"
}
```

### ExtractedData
```python
{
  "id": "uuid",
  "document_id": "uuid",
  "schema_id": "uuid",
  "data": "json",  # {variable_name: {value, confidence}}
  "flagged": "boolean",
  "extracted_at": "timestamp"
}
```

---

## MVP Development Phases

### Month 1: Foundation
**Week 1-2: Setup & Core Backend**
- [ ] Project setup (repo, CI/CD, environment)
- [ ] FastAPI backend structure
- [ ] PostgreSQL + Redis setup
- [ ] User authentication (JWT)
- [ ] Basic API endpoints (CRUD for users, projects)

**Week 3-4: Document Pipeline**
- [ ] Document upload endpoint
- [ ] PDF/DOCX/TXT parsers
- [ ] Document storage
- [ ] Basic document management API

### Month 2: Conversational AI & LLM Integration
**Week 5-6: Conversation System**
- [ ] Conversation state management
- [ ] Question generation logic
- [ ] Response interpretation
- [ ] Prompt builder from conversation

**Week 7-8: Multi-Agent System**
- [ ] LangGraph setup
- [ ] Orchestrator agent
- [ ] Specialized extraction agents (date, location, entity)
- [ ] Confidence scoring
- [ ] Testing on sample data

### Month 3: Frontend Development
**Week 9-10: Core UI**
- [ ] Next.js setup with authentication
- [ ] Project dashboard
- [ ] Document upload interface
- [ ] Chat interface for schema definition

**Week 11-12: Data Review Interface**
- [ ] Sample results viewer
- [ ] Data table with filtering/sorting
- [ ] Error flagging UI
- [ ] Export to CSV functionality

### Month 4: Integration, Testing & Polish
**Week 13-14: Full Integration**
- [ ] Connect frontend to backend
- [ ] WebSocket for real-time updates
- [ ] Celery job queue for processing
- [ ] Progress tracking

**Week 15-16: Testing & Launch Prep**
- [ ] End-to-end testing
- [ ] Bug fixes
- [ ] Performance optimization
- [ ] Documentation
- [ ] Deploy to production
- [ ] User testing with 3-5 beta users

---

## Success Metrics (MVP)

### Technical Metrics
- ✓ Successfully extracts 4-6 common variable types
- ✓ Processes 100 documents in < 2 hours
- ✓ Extraction accuracy > 85% (vs. manual coding)
- ✓ System uptime > 95%
- ✓ User can complete full workflow in < 2 hours

### User Metrics (Beta Testing)
- ✓ 5 researchers complete end-to-end workflow
- ✓ Average satisfaction > 7/10
- ✓ Time savings > 70% vs. manual coding
- ✓ Users can use system without technical support

### Business Metrics
- ✓ MVP deployed and accessible
- ✓ $500-1000/month operating costs
- ✓ Clear path to monetization identified

---

## Risk Mitigation

### Risk 1: LLM Accuracy Issues
**Mitigation:**
- Start with well-defined, simple variables
- Confidence scoring highlights uncertain extractions
- Sample testing before full processing
- Manual review for low-confidence items

### Risk 2: Scope Creep
**Mitigation:**
- This document defines strict boundaries
- Park all additional features for Phase 2
- Weekly review of timeline vs. scope

### Risk 3: Cost Overruns (LLM API costs)
**Mitigation:**
- Implement caching aggressively
- Use cheaper models where appropriate (GPT-4o-mini)
- Set usage limits per user
- Monitor costs daily

### Risk 4: Integration with Existing Python Code
**Mitigation:**
- Week 1: Audit existing code
- Identify reusable components
- Refactor incrementally
- Don't force integration if code needs major rewrite

---

## Questions to Resolve Before Starting

### About Your Existing Python Code
1. **What components exist?**
   - Document parsing?
   - LLM integration?
   - Extraction logic?
   - Export functionality?

2. **What can be reused vs. rebuilt?**
   - Which parts are production-ready?
   - Which parts need refactoring?

3. **What's the code quality?**
   - Tests?
   - Documentation?
   - Code organization?

### Product Decisions
1. **User authentication:** Do you want social login (Google/GitHub) or just email/password?

2. **LLM provider preference:** OpenAI, Anthropic, or both?

3. **Deployment:** Self-hosted eventually, or always cloud?

4. **Pricing model:** How do you plan to monetize? (impacts resource limits)

---

## Next Steps

1. **Review this specification** - Confirm scope is appropriate
2. **Answer questions above** - Clarify unknowns
3. **Audit existing Python code** - Determine reusability
4. **Create detailed technical design docs** - API specs, component designs
5. **Set up development environment** - Repos, tools, CI/CD
6. **Start Month 1 development** - Begin with foundation

---

**Document Status:** DRAFT - Pending review and approval
