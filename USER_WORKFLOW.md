User Workflow
Step 1: Project Setup & Document Input
User creates a new project and specifies scale:

Small/Experimental: Single document or a couple of documents for testing
Large: Many documents from connected cloud folders

Document input methods:

Cloud connection: Link to folders containing many files (Google Drive, Dropbox, etc.)
Direct upload: Upload individual files for small projects

After input:

Documents displayed in list/grid view
User can review documents before proceeding
Clear visual indication of number of documents loaded


Step 2: Schema Definition (Wizard-Style)
NOT a chat interface. This is a structured, step-by-step wizard.
For each variable the user wants to extract:

Variable name input field
Variable type selector (text, number, date, category, boolean, etc.)
Extraction instructions text area (user describes what to extract and how)
Classification rules if applicable (categories, scales, conditions)
AI provides suggestions based on user's description

The wizard allows:

Adding multiple variables sequentially
Editing previously defined variables
Removing variables
Reordering variables

Key UI elements:

"Add Another Variable" button
Progress indicator showing number of variables defined
"Back" and "Next" navigation
Clear visual separation between variables


Step 3: Schema Review & Confirmation
Display the complete schema:

Show all defined variables as column headers in a table preview
Include variable types and extraction rules in expandable details
Visual preview of what the final dataset structure will look like

User actions available:

Edit any variable (returns to wizard for that variable)
Delete variables
Reorder columns via drag-and-drop or arrows
Confirm and Proceed button (prominent, clear)


Step 4: Processing
Phase A: Sample Testing

System processes a sample subset of documents first
Results displayed in table format with schema columns populated
User can:

Review sample extractions
Flag errors or issues (click on cells to flag)
See which documents were processed
Choose to refine schema (go back to Step 3) or proceed to full processing



Phase B: Full Processing

Detailed processing log visible in real-time:

Document being processed (name, number)
Variables being extracted
Errors or warnings
Progress percentage


User can navigate away - processing continues in background
Project page shows processing status when user returns
Notification when processing completes

Key UI elements:

Progress bar (overall and per-document if possible)
Processing log panel (scrollable, timestamped)
"View Project Dashboard" button to navigate away
Status indicator (Processing, Paused, Complete, Error)


Step 5: Results & Export
Dataset view:

Table format displaying all extracted data
Columns match the schema defined in Step 2
Rows represent documents or extracted entities

User actions:

Review data (scroll, sort, filter)
Export functionality:

Export format selector (CSV, Excel, JSON, etc.)
Custom structure options (if defined in your system)
Download button



Key UI elements:

Clean, readable table with proper column headers
Export button (prominent placement)
Data summary statistics (optional: row count, completion %, etc.)


Development Instructions

Reference this workflow for all UI/UX decisions
Each step should be clearly identifiable in the interface
Navigation between steps must be intuitive and obvious
Visual hierarchy should guide users through the workflow naturally
Error states and loading states must be handled for every step
Mobile responsiveness is important but desktop is primary use case

Key Design Principles

Clarity over cleverness: Users should never be confused about what to do next
Progress visibility: Users should always know where they are in the workflow
Reversibility: Users should be able to go back and modify earlier decisions
Asynchronous awareness: Make it clear when processes run in background
Data transparency: Show users what's happening with their data at each step
