from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from pathlib import Path
from datetime import datetime

from org_parser import append_todo_to_file, get_inbox_file_path, validate_org_directory

app = FastAPI(
    title="Org-Bridge API",
    description="API server for bridging Emacs org-mode with Zapier",
    version="0.1.0"
)

# Configuration
ORG_FILES_DIR = os.getenv("ORG_FILES_DIR")
if not ORG_FILES_DIR:
    raise ValueError("ORG_FILES_DIR environment variable is required")
INBOX_FILENAME = os.getenv("INBOX_FILENAME", "inbox.org")
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8247"))

# Pydantic models
class TodoItem(BaseModel):
    id: Optional[str] = None
    title: str
    state: str = "TODO"  # TODO, DONE, etc.
    priority: Optional[str] = None  # A, B, C
    tags: List[str] = []
    scheduled: Optional[str] = None  # ISO datetime string
    deadline: Optional[str] = None   # ISO datetime string
    include_scheduled_time: Optional[bool] = False
    include_deadline_time: Optional[bool] = False
    is_recurring: Optional[bool] = False
    recurring_field: Optional[str] = None  # "scheduled" or "deadline"
    repeat_every: Optional[int] = None
    repeat_unit: Optional[str] = None  # "hours", "days", "weeks", "months", "years"
    repeat_type: Optional[str] = None  # "standard", "from_completion", "catch_up"
    properties: Optional[Dict[str, str]] = None
    body: Optional[str] = None
    file_path: Optional[str] = None
    heading: Optional[str] = None  # Heading under which to file the TODO

class CreateTodoRequest(BaseModel):
    title: str
    state: str = "TODO"
    priority: Optional[str] = None
    tags: List[str] = []
    scheduled: Optional[str] = None  # ISO datetime string
    deadline: Optional[str] = None   # ISO datetime string
    include_scheduled_time: Optional[bool] = False
    include_deadline_time: Optional[bool] = False
    is_recurring: Optional[bool] = False
    recurring_field: Optional[str] = None  # "scheduled" or "deadline"
    repeat_every: Optional[int] = None
    repeat_unit: Optional[str] = None  # "hours", "days", "weeks", "months", "years"
    repeat_type: Optional[str] = None  # "standard", "from_completion", "catch_up"
    properties: Optional[Dict[str, str]] = None
    body: Optional[str] = None
    file_name: Optional[str] = None  # Which org file to add to
    heading: Optional[str] = None  # Heading under which to file the TODO

class NoteRequest(BaseModel):
    title: str
    content: str = ""
    tags: List[str] = []

@app.get("/")
async def root():
    """
    Get server information and configuration status.
    
    Returns server version, configured org files directory, inbox file path,
    and whether the org directory exists and is accessible.
    """
    return {
        "message": "Org-Bridge API Server",
        "version": "0.1.0",
        "org_files_dir": ORG_FILES_DIR,
        "inbox_file": get_inbox_file_path(ORG_FILES_DIR, INBOX_FILENAME),
        "org_dir_exists": validate_org_directory(ORG_FILES_DIR)
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# @app.get("/todos", response_model=List[TodoItem])
# async def get_todos(
#     state: Optional[str] = None,
#     tag: Optional[str] = None,
#     file_name: Optional[str] = None
# ):
#     """Get all TODO items, optionally filtered by state, tag, or file"""
#     # TODO: Implement org file parsing
#     return []

@app.post("/todos", response_model=TodoItem)
async def create_todo(todo: CreateTodoRequest):
    """
    Create a new TODO item in an org file.
    
    **Field Guide:**
    - `title`: The TODO description/heading text (e.g., "Review quarterly reports")
    - `state`: TODO state (e.g., "TODO", "DONE", "NEXT", "WAITING", "CANCELLED")
    - `priority`: Priority level (e.g., "A", "B", "C" or null for no priority)
    - `tags`: List of strings for categorization (e.g., ["work", "urgent", "meeting"])
    - `scheduled`: ISO datetime when you plan to work on it (e.g., "2025-01-20T14:30:00")
    - `deadline`: ISO datetime for hard deadline (e.g., "2025-01-22T17:00:00")
    - `include_scheduled_time`: Include time in scheduled timestamp (true = "14:30", false = date only)
    - `include_deadline_time`: Include time in deadline timestamp (true = "17:00", false = date only)
    - `file_name`: Which org file to write to (e.g., "work.org", defaults to "inbox.org")
    - `heading`: Heading to file under (e.g., "Projects", creates if doesn't exist)
    - `body`: Additional notes/content (e.g., "Need to review Q4 numbers before meeting")
    - `properties`: Key-value pairs (e.g., {"CATEGORY": "work", "EFFORT": "2:00"})
    
    **Recurring TODO fields:**
    - `is_recurring`: Enable recurring pattern (true/false)
    - `recurring_field`: Which date repeats (e.g., "scheduled" or "deadline")
    - `repeat_every`: Interval number (e.g., 1, 2, 7)
    - `repeat_unit`: Time unit (e.g., "days", "weeks", "months", "years")
    - `repeat_type`: Repeat behavior (e.g., "standard", "from_completion", "catch_up")
    
    **Example org-mode output:**
    ```
    * TODO [#A] Weekly team meeting :work:meeting:
    SCHEDULED: <2025-01-20 Mon 14:30 +1w>
    :PROPERTIES:
    :ID: 12345678-abcd-1234-5678-123456789abc
    :CATEGORY: work
    :EFFORT: 1:00
    :END:
    
    Review quarterly goals and discuss project updates.
    ```
    """
    try:
        # Determine which file to write to
        if todo.file_name:
            file_path = str(Path(ORG_FILES_DIR) / todo.file_name)
        else:
            # Default to inbox file
            file_path = get_inbox_file_path(ORG_FILES_DIR, INBOX_FILENAME)
        
        # Validate org directory exists
        if not validate_org_directory(ORG_FILES_DIR):
            raise HTTPException(
                status_code=404, 
                detail=f"Org files directory not found: {ORG_FILES_DIR}"
            )
        
        # Append the TODO to the file and get the generated UUID
        todo_text, generated_uuid = append_todo_to_file(
            file_path=file_path,
            title=todo.title,
            state=todo.state,
            priority=todo.priority,
            tags=todo.tags,
            scheduled=todo.scheduled,
            deadline=todo.deadline,
            include_scheduled_time=todo.include_scheduled_time or False,
            include_deadline_time=todo.include_deadline_time or False,
            is_recurring=todo.is_recurring or False,
            recurring_field=todo.recurring_field,
            repeat_every=todo.repeat_every,
            repeat_unit=todo.repeat_unit,
            repeat_type=todo.repeat_type,
            properties=todo.properties,
            body=todo.body,
            heading=todo.heading
        )
        
        # Use the generated UUID as the TODO ID
        todo_id = generated_uuid
        
        return TodoItem(
            id=todo_id,
            title=todo.title,
            state=todo.state,
            priority=todo.priority,
            tags=todo.tags,
            scheduled=todo.scheduled,
            deadline=todo.deadline,
            include_scheduled_time=todo.include_scheduled_time,
            include_deadline_time=todo.include_deadline_time,
            is_recurring=todo.is_recurring,
            recurring_field=todo.recurring_field,
            repeat_every=todo.repeat_every,
            repeat_unit=todo.repeat_unit,
            repeat_type=todo.repeat_type,
            properties=todo.properties,
            body=todo.body,
            file_path=file_path,
            heading=todo.heading
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create TODO: {str(e)}")

# @app.put("/todos/{todo_id}", response_model=TodoItem)
# async def update_todo(todo_id: str, todo: CreateTodoRequest):
#     """Update an existing TODO item"""
#     # TODO: Implement todo update
#     return TodoItem(
#         id=todo_id,
#         title=todo.title,
#         state=todo.state,
#         priority=todo.priority,
#         tags=todo.tags,
#         scheduled=todo.scheduled,
#         deadline=todo.deadline,
#         include_scheduled_time=todo.include_scheduled_time,
#         include_deadline_time=todo.include_deadline_time,
#         is_recurring=todo.is_recurring,
#         recurring_field=todo.recurring_field,
#         repeat_every=todo.repeat_every,
#         repeat_unit=todo.repeat_unit,
#         repeat_type=todo.repeat_type,
#         properties=todo.properties,
#         body=todo.body
#     )

# @app.get("/agenda")
# async def get_agenda(
#     start_date: Optional[str] = None,
#     end_date: Optional[str] = None
# ):
#     """Get agenda items for a date range"""
#     # TODO: Implement agenda parsing
#     return []

# @app.post("/notes")
# async def create_note(note: NoteRequest):
#     """Create a new denote-style note"""
#     # TODO: Implement denote note creation
#     return {
#         "message": "Note created",
#         "title": note.title,
#         "file_name": f"placeholder--{note.title.lower().replace(' ', '-')}.org"
#     }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT) 