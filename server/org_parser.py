"""
Org-mode file parsing and manipulation functions.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List


def format_org_timestamp(iso_datetime_str: str, include_time: bool = False) -> str:
    """
    Convert ISO datetime string to org-mode timestamp format.
    Ignores timezone info and uses date/time as-is.
    
    Args:
        iso_datetime_str: ISO format datetime string or date string
        include_time: Whether to include time in the output
    
    Returns:
        Org-mode timestamp string like '<2025-01-20>' or '<2025-01-20 14:30>'
    """
    # Parse ISO string but ignore timezone
    dt = datetime.fromisoformat(iso_datetime_str.replace('Z', '+00:00'))
    
    if include_time:
        return f"<{dt.strftime('%Y-%m-%d %H:%M')}>"
    else:
        return f"<{dt.strftime('%Y-%m-%d')}>"


def append_todo_to_file(
    file_path: str,
    title: str,
    state: str = "TODO",
    priority: Optional[str] = None,
    tags: List[str] = None,
    scheduled: Optional[str] = None,
    deadline: Optional[str] = None,
    include_scheduled_time: bool = False,
    include_deadline_time: bool = False,
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
        scheduled: Scheduled date (ISO datetime string)
        deadline: Deadline date (ISO datetime string)
        include_scheduled_time: Whether to include time in scheduled timestamp
        include_deadline_time: Whether to include time in deadline timestamp
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
    
    # Format timestamps
    scheduled_timestamp = None
    deadline_timestamp = None
    
    if scheduled:
        scheduled_timestamp = format_org_timestamp(scheduled, include_scheduled_time)
    
    if deadline:
        deadline_timestamp = format_org_timestamp(deadline, include_deadline_time)
    
    # If both scheduled and deadline exist, put them on the same line
    if scheduled_timestamp and deadline_timestamp:
        additional_lines.append(f"SCHEDULED: {scheduled_timestamp} DEADLINE: {deadline_timestamp}")
    elif scheduled_timestamp:
        additional_lines.append(f"SCHEDULED: {scheduled_timestamp}")
    elif deadline_timestamp:
        additional_lines.append(f"DEADLINE: {deadline_timestamp}")
    
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