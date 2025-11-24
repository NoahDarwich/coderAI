# Feature Specification: Complete User Workflow (5 Steps)

**Feature Branch**: `001-complete-user-workflow`
**Created**: 2025-01-23
**Status**: Draft
**Input**: User description: "Generate a plan for implementing all 5 workflow steps"

## User Workflow Context

**Primary Workflow Step(s):** All steps 1-5 (complete end-to-end workflow)

**Workflow Alignment:** This feature implements the complete 5-step user journey defined in USER_WORKFLOW.md, from project creation through data export. It represents the core MVP functionality that enables researchers to extract structured data from documents without technical expertise.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Project Setup & Document Input (Priority: P1) 🎯 MVP

A researcher wants to start a new research project and load their documents for analysis.

**Why this priority**: This is the entry point for all users. Without project creation and document upload, no other workflow steps are possible. This is the foundation of the entire application.

**Workflow Step:** Step 1 (Project Setup & Document Input)

**Independent Test**: User can create a project, select scale (small/large), upload documents via drag-and-drop or cloud connection, see document list with count, and proceed to next step.

**Acceptance Scenarios**:

1. **Given** user is on dashboard, **When** they click "New Project", **Then** they see project creation form with scale selector
2. **Given** user creates a small project, **When** they upload 5 PDF files via drag-and-drop, **Then** they see 5 documents in the list with names and upload status
3. **Given** user has uploaded documents, **When** they view the document list, **Then** they see document count, file names, and "Proceed to Schema Definition" button

---

### User Story 2 - Schema Definition Wizard (Priority: P1) 🎯 MVP

A researcher wants to define what data to extract from their documents using a step-by-step wizard interface.

**Why this priority**: The schema definition is the core intelligence of the system. Users must be able to define extraction variables before any processing can occur. This is what makes the tool flexible and valuable.

**Workflow Step:** Step 2 (Schema Definition Wizard)

**Independent Test**: User can navigate a multi-step wizard to define variables (name, type, extraction instructions, classification rules), add multiple variables, edit/delete/reorder them, and see AI suggestions.

**Acceptance Scenarios**:

1. **Given** user has uploaded documents, **When** they click "Define Schema", **Then** they see a wizard form with fields for variable name, type selector, and instructions
2. **Given** user is defining a variable, **When** they enter "Date of protest" as variable name and select "Date" type, **Then** AI suggests extraction instructions
3. **Given** user has defined 3 variables, **When** they click "Add Another Variable", **Then** they see a new blank variable form with progress showing "4 of N variables"
4. **Given** user has defined variables, **When** they click "Back", **Then** they return to previous variable without losing data
5. **Given** user has completed wizard, **When** they click "Review Schema", **Then** they proceed to schema review page

---

### User Story 3 - Schema Review & Confirmation (Priority: P1) 🎯 MVP

A researcher wants to review their complete schema before processing to ensure it's correct.

**Why this priority**: This is a critical validation gate. Reviewing the schema before processing prevents wasted time and LLM costs from running incorrect extractions on all documents.

**Workflow Step:** Step 3 (Schema Review & Confirmation)

**Independent Test**: User can view complete schema as a table preview, see all variables with types and rules, edit any variable (returns to wizard), delete variables, reorder via drag-and-drop, and approve for processing.

**Acceptance Scenarios**:

1. **Given** user completed schema wizard, **When** they view schema review page, **Then** they see table preview with column headers matching their defined variables
2. **Given** user views schema, **When** they click on a variable name, **Then** expandable details show type and extraction rules
3. **Given** user wants to modify a variable, **When** they click "Edit" on that variable, **Then** they return to wizard at that specific variable
4. **Given** user is satisfied with schema, **When** they click "Confirm and Proceed", **Then** they move to processing page

---

### User Story 4 - Sample Testing & Full Processing (Priority: P1) 🎯 MVP

A researcher wants to test extraction on a sample of documents first, review results, and then process all documents.

**Why this priority**: Sample testing prevents catastrophic failures. Users need to validate extraction quality before committing to processing 100+ documents. This saves time, money, and user trust.

**Workflow Step:** Step 4 (Processing - Sample & Full)

**Independent Test**: User can run sample extraction on 10-20 documents, view results in table format, flag errors, optionally refine schema, then run full processing with progress tracking.

**Acceptance Scenarios**:

**Phase A: Sample Testing**
1. **Given** user confirmed schema, **When** processing page loads, **Then** they see "Test on Sample" section with sample size selector (10-20 docs)
2. **Given** user clicks "Run Sample", **When** sample processing completes, **Then** they see results table with schema columns populated and confidence indicators
3. **Given** user reviews sample results, **When** they click a cell with incorrect data, **Then** they can flag it as error with checkmark/X button
4. **Given** user identifies issues, **When** they click "Refine Schema", **Then** they return to schema definition wizard
5. **Given** user is satisfied with sample, **When** they click "Approve for Full Processing", **Then** Phase B begins

**Phase B: Full Processing**
6. **Given** user approved schema, **When** full processing starts, **Then** they see real-time processing log with document names, progress bar, and status
7. **Given** processing is running, **When** user navigates away, **Then** processing continues in background with notification on completion
8. **Given** processing encounters error, **When** error occurs, **Then** user sees error message in log and processing continues with other documents

---

### User Story 5 - Results Review & Export (Priority: P1) 🎯 MVP

A researcher wants to review extracted data, filter by confidence, and export to CSV for analysis.

**Why this priority**: This is the deliverable. Without export, all the processing is useless. This is what researchers need to complete their work.

**Workflow Step:** Step 5 (Results & Export)

**Independent Test**: User can view complete results in sortable/filterable table, see confidence scores, filter by confidence threshold, select export format (CSV wide/long), configure export options, and download file.

**Acceptance Scenarios**:

1. **Given** processing is complete, **When** user views results page, **Then** they see data table with schema columns, sortable headers, and confidence indicators (🟢 🟡 🔴)
2. **Given** user wants to filter, **When** they set minimum confidence to 80%, **Then** table shows only rows with confidence ≥ 80%
3. **Given** user clicks a cell, **When** modal opens, **Then** they see source document text that generated the extraction
4. **Given** user is ready to export, **When** they click "Export Data", **Then** they see format selector (CSV wide/long) and options (include confidence scores, include source text)
5. **Given** user configures export, **When** they click "Download", **Then** CSV file downloads with specified format and options

---

### Edge Cases

- What happens when user uploads 0 documents? (Block proceed button, show helpful message)
- What happens when user defines 0 variables in wizard? (Block review, require at least 1 variable)
- What happens when sample processing fails completely? (Show error, allow schema refinement or retry)
- What happens when user navigates back mid-workflow? (Preserve all data, allow resuming)
- What happens when processing a document times out? (Log error, continue with other documents, mark document as failed)
- What happens when user exports with 0 results? (Show warning, allow export of empty CSV with headers)

## Requirements *(mandatory)*

### Functional Requirements

**Step 1: Project Setup & Document Input**
- **FR-001**: System MUST allow users to create new projects with a unique project name
- **FR-002**: System MUST provide project scale selector (Small/Experimental, Large)
- **FR-003**: System MUST support document upload via drag-and-drop interface
- **FR-004**: System MUST support cloud folder connection (Google Drive, Dropbox) for large projects
- **FR-005**: System MUST display uploaded documents in list/grid view with document name and count
- **FR-006**: System MUST allow users to delete uploaded documents before proceeding

**Step 2: Schema Definition Wizard**
- **FR-007**: System MUST provide wizard interface with fields for variable name, type, and extraction instructions
- **FR-008**: System MUST support variable types: text, number, date, category, boolean
- **FR-009**: System MUST allow users to add classification rules for categorical variables
- **FR-010**: System MUST provide AI-generated suggestions for extraction instructions based on variable name and type
- **FR-011**: System MUST allow users to add multiple variables sequentially
- **FR-012**: System MUST allow users to edit previously defined variables
- **FR-013**: System MUST allow users to delete variables
- **FR-014**: System MUST allow users to reorder variables
- **FR-015**: System MUST show progress indicator (e.g., "3 variables defined")

**Step 3: Schema Review & Confirmation**
- **FR-016**: System MUST display complete schema as table preview with column headers
- **FR-017**: System MUST show expandable details for each variable (type, extraction rules, classification rules)
- **FR-018**: System MUST provide "Edit" action that returns to wizard at specific variable
- **FR-019**: System MUST allow drag-and-drop reordering of columns
- **FR-020**: System MUST require explicit confirmation via "Confirm and Proceed" button

**Step 4: Processing**
- **FR-021**: System MUST provide sample processing on configurable subset (10-20 documents)
- **FR-022**: System MUST display sample results in table format with schema columns populated
- **FR-023**: System MUST show confidence scores for each extraction
- **FR-024**: System MUST allow users to flag cells as correct (✓) or incorrect (✗)
- **FR-025**: System MUST allow users to refine schema after sample review
- **FR-026**: System MUST provide "Approve for Full Processing" button after sample review
- **FR-027**: System MUST process all documents after approval with batch processing
- **FR-028**: System MUST display real-time processing log with document name, progress percentage
- **FR-029**: System MUST support background processing (user can navigate away)
- **FR-030**: System MUST send notification when processing completes
- **FR-031**: System MUST log errors and continue processing remaining documents

**Step 5: Results & Export**
- **FR-032**: System MUST display results in sortable, filterable data table
- **FR-033**: System MUST show confidence indicators (🟢 high ≥85%, 🟡 medium 70-84%, 🔴 low <70%)
- **FR-034**: System MUST allow filtering by minimum confidence threshold
- **FR-035**: System MUST allow clicking cells to view source document text
- **FR-036**: System MUST provide CSV export in wide format (1 row per document)
- **FR-037**: System MUST provide CSV export in long format (1 row per extracted field)
- **FR-038**: System MUST allow optional inclusion of confidence scores in export
- **FR-039**: System MUST allow optional inclusion of source text in export
- **FR-040**: System MUST display data summary statistics (row count, completion %)

### Key Entities

- **Project**: Represents a research project with name, scale (small/large), creation date, status
- **Document**: Uploaded file with name, type (PDF/DOCX/TXT), upload timestamp, content text
- **Schema**: Collection of variables defined by user
- **Variable**: Single extraction target with name, type, instructions, classification rules (if applicable)
- **Extraction**: Single extracted value with document reference, variable reference, value, confidence score, source text span
- **ExportConfig**: Export configuration with format (CSV wide/long), options (include confidence, include source)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete Step 1 (project setup + document upload) in under 3 minutes for small projects
- **SC-002**: Users can define a 5-variable schema in Step 2 (wizard) in under 10 minutes without technical support
- **SC-003**: Sample processing (Step 4A) completes for 20 documents in under 2 minutes (with mock data)
- **SC-004**: Users can identify schema issues in Step 3 (review) and return to wizard without data loss
- **SC-005**: Full processing progress (Step 4B) updates in real-time with < 1 second latency
- **SC-006**: Users can export data (Step 5) in desired format with < 5 clicks
- **SC-007**: 90% of users successfully navigate all 5 steps on first attempt (measured in usability testing)
- **SC-008**: System maintains WCAG 2.1 AA accessibility compliance across all 5 workflow steps
