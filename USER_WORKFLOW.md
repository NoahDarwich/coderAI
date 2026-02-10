# User Workflow

**Primary Reference:** See [CODERAI_REFERENCE.md](CODERAI_REFERENCE.md) for architecture, data model, and backend implementation details.

---

## Step 1: Project Setup & Document Input
User creates a new project and specifies scale:

Small/Experimental: Single document or a couple of documents for testing
Large: Many documents from connected cloud folders

Document input methods:

Cloud connection: Link to folders containing many files (Google Drive, Dropbox, etc.)
Direct upload: Upload individual files for small projects
Text input: Paste text directly for quick analysis

**NEW: Project Context Questions** (enriches AI understanding)

Document type identification:
- File type: [Free text input - e.g., "PDF invoices", "Word contracts", "Excel spreadsheets", "Scanned documents"]

Domain context (optional but recommended):
- Industry/domain: [Free text input ]

Expected variance:
- Language: [Free text input - e.g., "English", "Spanish", "Mixed languages"]

After input:

Documents displayed in list/grid view with metadata preview
User can review documents before proceeding
Clear visual indication of number of documents loaded


Step 2: Unit of Observation (Wizard-Style)
**REQUIRED: Before defining what to extract, user must define the unit of observation.**
NOT a chat interface. This is a structured, wizard-style step.

**What is the Unit of Observation?**
The unit of observation is what each row in your final dataset represents.

**Wizard Questions:**

1. **Primary Question: "What does each row in your dataset represent?"**
   - Free text input with examples:
     - "Each document" (1 row per document - most common)
     - "Each invoice line item" (multiple rows per document)
     - "Each person mentioned" (variable rows per document)
     - "Each transaction" (could be multiple per document)
     - "Each paragraph" or "Each page"

2. **Clarification: "How many rows do you expect per document?"**
   - One row per document (most common - document-level extraction)
   - Multiple rows per document (entity-level extraction)
   - Variable (depends on document content)

3. **If Multiple Rows: "How should the system identify each [entity]?"**
   - Only asked if user selected multiple rows per document
   - Free text input: "Each row in a table", "Each section starting with a number", "Each paragraph containing a person's name", etc.
   - AI suggests identification patterns based on document type
   - User confirms or refines

4. **Nested Data: "Are there nested relationships?"** (Optional - Advanced)
   - No, flat structure (1 level)
   - Yes, hierarchical (e.g., Invoice → Line Items → Sub-items)
   - If yes: "Describe the relationship structure"

**Why This Matters:**
- Document-level extraction (one row per document): Simpler, extracts all variables once
- Entity-level extraction (multiple rows per document): More complex, requires entity identification
- Affects prompt structure, variable definitions, and result format

**UI Elements:**
- Clear visual examples of different unit types
- Preview showing how their choice affects the output table
- "Not sure?" helper with common patterns by document type
- Confirmation screen showing their choice before proceeding

**Next Step:** Once unit of observation is defined, proceed to define variables.


Step 3: Schema Definition (Wizard-Style)
NOT a chat interface. This is a structured, step-by-step wizard.
For each variable the user wants to extract:

**Core variable definition:**
- Variable name input field
- Variable type selector (text, number, date, category, boolean, etc.)
- Extraction instructions text area (user describes what to extract and how)
- Classification rules if applicable (categories, scales, conditions)


Handling uncertainty:
- Confidence threshold: High (95%+), Medium (80%+), Low (60%+)
- If uncertain: Skip and flag, Use default value, Extract with warning
- Multiple values found: Take first, Take last, Take all (array), Flag for review

Edge cases and validation:
- "What if this field is missing?" → [Required/Optional behavior]
- "What if multiple values exist?" → [Handling strategy]
- Data validation rules: Min/max values, regex pattern, allowed values list
- Default value if not found: [specify or leave empty]



**NEW: Variable Relationships:**
- "Does this variable depend on another?" (e.g., "Discount Amount" depends on "Has Discount: Yes")
- "Should this variable be calculated from others?" (formulas/derivations)
- Conditional extraction rules

The wizard allows:

Adding multiple variables sequentially
Editing previously defined variables
Removing variables
Reordering variables
**NEW: Duplicating similar variables** (copies config for faster setup)

Key UI elements:

"Add Another Variable" button
Progress indicator showing number of variables defined
"Back" and "Next" navigation
Clear visual separation between variables


Step 4: Schema Review & Confirmation
Display the complete schema:

Show all defined variables as column headers in a table preview
Include variable types and extraction rules in expandable details
Visual preview of what the final dataset structure will look like
**NEW: Show unit of observation** - "Each row represents: [UNIT]"
- If entity-level: Also show identification pattern


User actions available:

Edit unit of observation (returns to Step 2)
Edit any variable (returns to wizard for that variable)
Delete variables
Reorder columns via drag-and-drop or arrows
**NEW: Flag specific sample extractions as correct/incorrect** (trains the model, update the prompts based on the feedback)
**NEW: "Add validation rule"** based on sample data patterns
**NEW: "Save as template"** for reusing this schema on future projects
Confirm and Proceed button (prominent, clear)


Step 5: Processing
Phase A: Sample Testing

System processes a sample subset of documents first (user choose number of documents)
Results displayed in table format with schema columns populated

**NEW: Interactive Sample Review:**
User can:
- Review sample extractions
- **NEW: Click on any cell to:**
  - See source text from document
  - View AI's reasoning/confidence
  - Mark as correct/incorrect
  - Provide correct value if wrong
  - Add notes about the error
- **NEW: Filter view:**
  - Show only low-confidence extractions
  - Show only flagged items
  - Show specific variables
  - Show specific documents
- See which documents were processed
- **NEW: View extraction statistics:**
  - Success rate per variable
  - Average confidence scores
  - Most common errors/warnings


Decision point:
- Refine unit of observation (go back to Step 2)
- Refine schema (go back to Step 3)
- **NEW: Quick-fix specific variables** (inline editing without full wizard)
- **NEW: Provide additional examples** for problematic variables
- Proceed to full processing



Phase B: Full Processing

Detailed processing log visible in real-time:

Document being processed (name, number)
Variables being extracted with live confidence scores
Errors or warnings with severity levels
Progress percentage (overall and current document)
**NEW: Estimated time remaining**
**NEW: Running statistics:**
  - Documents processed / total
  - Success rate
  - Items flagged for review
  - Average processing time per document

**NEW: Continuous Quality Monitoring:**

- User can pause and review flagged items
- Option to "Review and continue" or "Auto-continue"


User can navigate away - processing continues in background
Project page shows processing status when user returns


Key UI elements:

Progress bar (overall and per-document if possible)
Processing log panel (scrollable, timestamped, filterable)
"View Project Dashboard" button to navigate away
Status indicator (Processing, Paused, Complete, Error)
**NEW: "Pause Processing"** button


Step 6: Results & Export
Dataset view:

Table format displaying all extracted data
Columns match the schema defined in Step 3
Rows represent the unit of observation defined in Step 2



User actions:

Review data (scroll, sort, filter)

Export functionality:

Export format selector (CSV, Excel, JSON, XML, PDF report)

Download button


Key UI elements:

Clean, readable table with proper column headers
Export button (prominent placement)
Data summary statistics (optional: row count, completion %, etc.)


---

## How User Questions Enrich AI Extraction Prompts

All questions asked throughout the workflow feed into the extraction prompt to dramatically improve accuracy. Here's how:

**From Step 1 (Project Context):**
```
Prompt enrichment:
- "You are extracting data from [FILE_TYPE] documents"
- "Domain/Industry: [DOMAIN_INDUSTRY]"
- "Documents are in [LANGUAGE]"
- "Document characteristics: [based on file type and domain context]"
```

**From Step 2 (Unit of Observation):**
```
Prompt enrichment:
- "Unit of observation: [WHAT_EACH_ROW_REPRESENTS]"
- "Rows per document: [ONE/MULTIPLE/VARIABLE]"
- "Extraction mode: [DOCUMENT_LEVEL or ENTITY_LEVEL]"

If Document-level (one row per document):
- "Extract all variables once per document"

If Entity-level (multiple rows per document):
- "Entity identification: [HOW_TO_IDENTIFY_EACH_ENTITY]"
- "For each document: first identify all [ENTITY_TYPE] using [IDENTIFICATION_PATTERN], then extract variables for each one"
- "Expected entities per document: [NUMBER_RANGE or VARIABLE]"
- "Data structure: [FLAT/HIERARCHICAL with relationship description]"

This fundamentally shapes how the AI approaches extraction:
- Document-level: Extract once per document
- Entity-level: Identify all instances of [ENTITY], extract each separately
```

**From Step 3 (Schema Definition):**
```
For each variable, prompt includes:
- "Extract [VARIABLE_NAME] which is a [TYPE]"
- "Description: [USER_DESCRIPTION]"
- "If confidence < [THRESHOLD]: [HANDLING_STRATEGY]"
- "If multiple values found: [MULTI_VALUE_STRATEGY]"
- "If missing: [this is REQUIRED/OPTIONAL], default: [DEFAULT_VALUE]"
- "Validation: [VALIDATION_RULES]"
- "Dependencies: [if CONDITION, then extract this]"
```

**From Step 4 (Schema Review & Golden Examples):**
```
Prompt enrichment:
- "Here are verified correct extractions from sample documents: [GOLDEN_EXAMPLES]"
- "Use these as reference patterns for similar documents"
- "Quality preference: [HIGH_PRECISION/HIGH_RECALL/BALANCED]"
- "For low confidence: [USER_STRATEGY]"
- "User-flagged corrections: [learn from these patterns]"
```

**From Step 5 (Processing Feedback):**
```
Dynamic prompt updates during processing:
- "User corrected [VARIABLE_X] from [WRONG] to [RIGHT] in [N] documents"
- "Pattern detected: [LEARNED_PATTERN]"
- "Adjusted extraction rule: [NEW_RULE]"
- "These documents differ from samples: [ADAPTATION_NOTES]"
- "User validated these extractions as correct: [VALIDATION_EXAMPLES]"
- "Active learning feedback: [REAL_TIME_CORRECTIONS]"
```

**From Step 6 (Post-Processing Insights):**
```
For future projects/re-runs:
- "Variables by reliability: [RANKING] - prioritize more reliable patterns"
- "Common error patterns: [ERRORS] - watch for these issues"
- "User noted: [FEEDBACK] - incorporate these insights"
- "Template improvements: [REFINEMENTS]"
```

**Composite Extraction Prompt Structure:**
```
System Context:
[Domain, industry, document type, structure, quality, language from Step 1]

Unit of Observation (from Step 2):
- What each row represents: [UNIT_OF_OBSERVATION]
- Extraction mode: [DOCUMENT_LEVEL or ENTITY_LEVEL]

If Document-level:
- Extract all variables once per document

If Entity-level:
- Entity identification pattern: [HOW_TO_IDENTIFY]
- Expected entities per document: [NUMBER_RANGE or VARIABLE]
- Data structure: [FLAT/HIERARCHICAL]
- First identify all [ENTITY_TYPE] in the document using [PATTERN], then extract variables for each one

Task:
Extract the following variables for each [UNIT_OF_OBSERVATION]:

Variable 1: [NAME]
- Type: [TYPE]
- Description: [USER_DESCRIPTION]
- Location: [WHERE_TO_LOOK]
- Labels: [ALTERNATIVE_NAMES]
- Examples: [USER_EXAMPLES]
- Validation: [RULES]
- If uncertain: [HANDLING_STRATEGY]
- Golden examples: [VERIFIED_CORRECT_EXTRACTIONS]
- Dependencies: [CONDITIONS]

[Repeat for each variable...]

Quality Instructions:
- Target confidence: [THRESHOLD]
- Precision/Recall preference: [USER_PREFERENCE]
- Handle missing fields: [STRATEGY]
- Handle multiple values: [STRATEGY]

Learning Context:
- User corrections applied: [PATTERNS_FROM_FEEDBACK]
- Validated extractions: [CONFIRMED_EXAMPLES]
- Known pitfalls: [ERROR_PATTERNS_TO_AVOID]

Output Format:
[Structured format with confidence scores and source references]
```

**Key Implementation Notes:**
1. **Progressive Enhancement**: Start with basic prompt, enrich as user provides more information
2. **Context Preservation**: Store all user inputs in structured format for prompt building
3. **Dynamic Updates**: Allow prompt refinement based on real-time feedback during processing
4. **Template System**: Save enriched prompts as templates for reuse
5. **A/B Testing**: Track which prompt enrichments correlate with better accuracy
6. **Confidence Calibration**: Use golden examples to calibrate confidence thresholds

---

## Development Instructions

Reference this workflow for all UI/UX decisions
Each step should be clearly identifiable in the interface
Navigation between steps must be intuitive and obvious
Visual hierarchy should guide users through the workflow naturally
Error states and loading states must be handled for every step
Mobile responsiveness is important but desktop is primary use case

**NEW: Prompt Engineering Integration:**
- All user inputs must be captured in structured format
- Build extraction prompts dynamically from collected metadata
- Store prompt templates and enrichment data in database
- Track correlation between enrichment types and accuracy improvements
- Provide API endpoints for prompt preview (dev/debug tool)

**NEW: Unit of Observation Implementation:**
- Step 2 is always shown - user must define unit of observation
- Smart defaults based on document type (suggest "Each document" for most cases)
- Progressive disclosure: Entity identification questions only appear if user selects multiple rows per document
- Store extraction mode (DOCUMENT_LEVEL or ENTITY_LEVEL) as project configuration
- Allow users to edit unit of observation from Step 4 review screen

## Key Design Principles

Clarity over cleverness: Users should never be confused about what to do next
Progress visibility: Users should always know where they are in the workflow
Reversibility: Users should be able to go back and modify earlier decisions
Asynchronous awareness: Make it clear when processes run in background
Data transparency: Show users what's happening with their data at each step
**NEW: Progressive disclosure**: Advanced options hidden by default, revealed when needed
**NEW: Intelligent defaults**: Use AI to suggest sensible defaults based on document analysis
**NEW: Feedback loops**: Every user interaction potentially improves extraction quality
**NEW: Learning transparency**: Show users how their input improves results

---

## UX Enhancements Summary

**Reducing Cognitive Load:**
1. **Smart defaults**: Pre-fill answers based on document analysis where possible
2. **Contextual help**: Show examples and explanations inline, not in separate docs
3. **Progressive disclosure**: Don't show all options at once - reveal as needed
4. **Wizards over forms**: Step-by-step guided experience, not overwhelming forms
5. **Visual feedback**: Show immediate impact of user choices (live previews)

**Improving Accuracy Through Better Questions:**
1. **Specificity prompts**: Ask for examples, not just descriptions
2. **Edge case handling**: Explicitly ask how to handle ambiguity
3. **Golden examples**: Let users provide "correct" answers to learn from
4. **Active learning**: Ask for feedback during processing, not just at the end
5. **Pattern detection**: AI suggests improvements based on user corrections

**Maintaining Flow:**
1. **Non-blocking questions**: Optional questions don't prevent progress
2. **Save and resume**: Users can leave and return without losing work
3. **Background processing**: Long operations don't block UI
4. **Quick iterations**: Easy to test, refine, and reprocess
5. **Template reuse**: Don't make users start from scratch each time

**Building Trust:**
1. **Transparency**: Always show confidence scores and reasoning
2. **Control**: User can override any AI decision
3. **Validation**: Show sample results before full processing
4. **Traceability**: Link extracted data back to source documents
5. **Quality metrics**: Clear indicators of extraction success rates

**Question Design Best Practices:**
- **Required vs Optional**: Mark clearly - don't overwhelm with too many required fields
- **Smart ordering**: Ask high-impact questions first, refinements later
- **Context-aware**: Only ask questions relevant to the document type/user choices
- **Learn and adapt**: Fewer questions needed on subsequent projects with templates
- **Batch related questions**: Group related configuration together for cognitive efficiency
