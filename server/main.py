from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path

app = FastAPI(
    title="Org-Bridge API",
    description="API server for bridging Emacs org-mode with Zapier",
    version="0.1.0"
)

# Configuration
ORG_FILES_DIR = os.getenv("ORG_FILES_DIR", str(Path.home() / "org"))

# Pydantic models
class TodoItem(BaseModel):
    id: Optional[str] = None
    title: str
    state: str = "TODO"  # TODO, DONE, etc.
    priority: Optional[str] = None  # A, B, C
    tags: List[str] = []
    scheduled: Optional[str] = None
    deadline: Optional[str] = None
    file_path: Optional[str] = None

class CreateTodoRequest(BaseModel):
    title: str
    state: str = "TODO"
    priority: Optional[str] = None
    tags: List[str] = []
    scheduled: Optional[str] = None
    deadline: Optional[str] = None
    file_name: Optional[str] = None  # Which org file to add to

class NoteRequest(BaseModel):
    title: str
    content: str = ""
    tags: List[str] = []

@app.get("/")
async def root():
    return {
        "message": "Org-Bridge API Server",
        "version": "0.1.0",
        "org_files_dir": ORG_FILES_DIR
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/todos", response_model=List[TodoItem])
async def get_todos(
    state: Optional[str] = None,
    tag: Optional[str] = None,
    file_name: Optional[str] = None
):
    """Get all TODO items, optionally filtered by state, tag, or file"""
    # TODO: Implement org file parsing
    return []

@app.post("/todos", response_model=TodoItem)
async def create_todo(todo: CreateTodoRequest):
    """Create a new TODO item in an org file"""
    # TODO: Implement todo creation
    return TodoItem(
        id="placeholder",
        title=todo.title,
        state=todo.state,
        priority=todo.priority,
        tags=todo.tags,
        scheduled=todo.scheduled,
        deadline=todo.deadline
    )

@app.put("/todos/{todo_id}", response_model=TodoItem)
async def update_todo(todo_id: str, todo: CreateTodoRequest):
    """Update an existing TODO item"""
    # TODO: Implement todo update
    return TodoItem(
        id=todo_id,
        title=todo.title,
        state=todo.state,
        priority=todo.priority,
        tags=todo.tags,
        scheduled=todo.scheduled,
        deadline=todo.deadline
    )

@app.get("/agenda")
async def get_agenda(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get agenda items for a date range"""
    # TODO: Implement agenda parsing
    return []

@app.post("/notes")
async def create_note(note: NoteRequest):
    """Create a new denote-style note"""
    # TODO: Implement denote note creation
    return {
        "message": "Note created",
        "title": note.title,
        "file_name": f"placeholder--{note.title.lower().replace(' ', '-')}.org"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 