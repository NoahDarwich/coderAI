# Backend Workflow Reference

## Overview
The backend processes user inputs and transforms them into structured datasets through a series of steps involving prompt generation, API calls, and data aggregation.

---

## Workflow Steps

### 1. Project Configuration Collection

The system collects initial project information:
- Type of text sources (news articles, reports, academic papers, etc.)
- Unit of observation (document-level, event-level, paragraph-level, etc.)
- Language of source texts
- Project scale (small experimental vs. large-scale)
- Research goal and expected output format
- Domain-specific context

This information is stored as project metadata and used to contextualize all subsequent processing.

---

### 2. Schema Design & Variable Definition

The user defines each variable to extract:
- **Variable name**: Column name in final dataset
- **Variable type**: text, numeric, categorical, date, boolean, etc.
- **Extraction instructions**: Natural language description of what to extract
- **Classification rules**: Categories, scales, or conditions (if applicable)

Each variable definition is stored and associated with the project.

---

### 3. Prompt Generation

The backend transforms each variable's extraction instructions into a prompt for the OpenAI API. The user's natural language instructions are converted into structured prompts that incorporate project context and specify the expected output format. Each variable gets its own dedicated prompt.

---

### 4. Prompt & Configuration Storage

For each variable, the system stores:
- Variable metadata (name, type, user instructions)
- Generated prompt (OpenAI-ready)
- Model configuration (model name, temperature, max tokens, etc.)
- Version history (previous prompt versions)

This structure allows each variable to have different extraction logic and model settings.

---

### 5. Sample Validation & Prompt Refinement

**Sample Processing:**
The user selects a small subset of documents to test the schema. The backend processes each sample document, calling the OpenAI API for each variable and returning results in table format.

**User Validation:**
The user reviews sample results and can flag incorrect extractions with comments explaining what's wrong.

**Prompt Adjustment:**
When errors are flagged, the backend analyzes the corrections, modifies the affected variable's prompt, and stores the new version. The user can re-test with updated prompts or proceed to full processing.

---

### 6. Full Processing

Once the schema is confirmed, full processing begins:

- A processing job is created for all documents
- For each document, the OpenAI API is called for each variable with that variable's finalized prompt
- Responses are parsed and stored
- Progress is tracked (documents completed, errors logged)
- Processing happens asynchronously - users can navigate away and return later

When complete, all extractions are combined into a structured dataset with the schema applied (columns = variables, rows = documents/observations).

---

### 7. Export & Delivery

The user requests the dataset in a specific format (CSV, Excel, JSON, or custom). The backend generates the file including:
- Complete dataset with all extracted variables
- Project metadata
- Variable definitions (codebook)
- Processing statistics

---

## How Data Flows

```
User Input → Project Metadata Stored
↓
Variables Defined → Variable Definitions Stored
↓
Instructions → OpenAI Prompts Created → Stored with Configs
↓
Sample Docs → API Calls → Results → User Feedback → Prompt Updates
↓
All Docs → API Calls → Extracted Data → Dataset
↓
Dataset → Format Conversion → File Delivery
```

---

## Processing States

- **Created**: Initial setup complete
- **Schema Defined**: Variables configured
- **Sample Testing**: Processing sample documents
- **Ready**: Sample validated, ready for full processing
- **Processing**: Full processing in progress
- **Complete**: All documents processed
- **Error**: Processing failed

The frontend receives status updates to show appropriate UI states.

---

**Document Version:** 1.0  
**Purpose:** Backend workflow explanation for frontend development
