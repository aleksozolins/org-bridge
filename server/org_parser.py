"""
Org-mode file parsing and manipulation functions.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List


def append_todo_to_file(
    file_path: str,
    title: str,
    state: str = "TODO",
    priority: Optional[str] = None,
    tags: List[str] = None,
    scheduled: Optional[str] = None,
    deadline: Optional[str] = None,
    properties: Optional[dict] = None,
    body: Optional[str] = None
) -> str:
    """
    Append a TODO item to an org file.
    
    Args:
        file_path: Path to the org file
        title: TODO title/description
        state: TODO state (TODO, DONE, etc.)
        priority: Priority level (A, B, C)
        tags: List of tags
        scheduled: Scheduled date (org format)
        deadline: Deadline date (org format)
        properties: Dict of properties for properties drawer
        body: Additional content/notes for the TODO
    
    Returns:
        The TODO item text that was appended
    """
    tags = tags or []
    
    # Build the TODO line
    todo_parts = [f"* {state}"]
    
    # Add priority
    if priority:
        todo_parts.append(f"[#{priority}]")
    
    # Add title
    todo_parts.append(title)
    
    # Add tags
    if tags:
        tag_string = ":" + ":".join(tags) + ":"
        todo_parts.append(tag_string)
    
    todo_line = " ".join(todo_parts)
    
    # Add scheduling/deadline info
    additional_lines = []
    
    # If both scheduled and deadline exist, put them on the same line
    if scheduled and deadline:
        additional_lines.append(f"SCHEDULED: <{scheduled}> DEADLINE: <{deadline}>")
    elif scheduled:
        additional_lines.append(f"SCHEDULED: <{scheduled}>")
    elif deadline:
        additional_lines.append(f"DEADLINE: <{deadline}>")
    
    # Add properties drawer if properties exist
    if properties:
        # Ensure property keys are uppercase (org-mode convention)
        uppercased_properties = {k.upper(): v for k, v in properties.items()}
        
        additional_lines.append(":PROPERTIES:")
        for prop_name, prop_value in uppercased_properties.items():
            additional_lines.append(f":{prop_name}: {prop_value}")
        additional_lines.append(":END:")
    
    # Combine everything
    todo_text = todo_line
    if additional_lines:
        todo_text += "\n" + "\n".join(additional_lines)
    
    # Add body if provided (separated by blank line)
    if body:
        todo_text += "\n\n" + body.strip()
    
    # Append to file
    file_path_obj = Path(file_path)
    
    # Create directory if it doesn't exist
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Append the TODO (with newlines for proper formatting)
    with open(file_path_obj, "a", encoding="utf-8") as f:
        f.write(f"\n{todo_text}\n")
    
    return todo_text


def get_inbox_file_path(org_dir: str, inbox_filename: str = "inbox.txt") -> str:
    """
    Get the path to the inbox file.
    
    Args:
        org_dir: Directory containing org files
        inbox_filename: Name of the inbox file
    
    Returns:
        Full path to the inbox file
    """
    return str(Path(org_dir) / inbox_filename)


def validate_org_directory(org_dir: str) -> bool:
    """
    Check if the org directory exists.
    
    Args:
        org_dir: Directory to check
    
    Returns:
        True if directory exists, False otherwise
    """
    return Path(org_dir).exists() 