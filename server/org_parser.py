"""
Org-mode file parsing and manipulation functions.
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple


def build_repeat_suffix(repeat_every: int, repeat_unit: str, repeat_type: str) -> str:
    """
    Build org-mode repeat suffix from components.
    
    Args:
        repeat_every: Number of intervals (1, 2, 3, etc.)
        repeat_unit: Unit type ("hours", "days", "weeks", "months", "years")
        repeat_type: Type ("standard", "from_completion", "catch_up")
    
    Returns:
        Org-mode repeat suffix like '+1w', '.+2d', '++3m'
    """
    # Map units to org-mode abbreviations
    unit_map = {
        "hours": "h",
        "days": "d",
        "weeks": "w", 
        "months": "m",
        "years": "y"
    }
    
    # Map types to org-mode prefixes
    type_map = {
        "standard": "+",
        "from_completion": ".+",
        "catch_up": "++"
    }
    
    unit_abbrev = unit_map.get(repeat_unit, "d")
    type_prefix = type_map.get(repeat_type, "+")
    
    return f"{type_prefix}{repeat_every}{unit_abbrev}"


def format_org_timestamp(
    iso_datetime_str: str, 
    include_time: bool = False,
    repeat_every: Optional[int] = None,
    repeat_unit: Optional[str] = None,
    repeat_type: Optional[str] = None
) -> str:
    """
    Convert ISO datetime string to org-mode timestamp format.
    Ignores timezone info and uses date/time as-is.
    
    Args:
        iso_datetime_str: ISO format datetime string or date string
        include_time: Whether to include time in the output
        repeat_every: Number for recurring pattern
        repeat_unit: Unit for recurring pattern ("hours", "days", "weeks", "months", "years")
        repeat_type: Type for recurring pattern ("standard", "from_completion", "catch_up")
    
    Returns:
        Org-mode timestamp string like '<2025-01-20>' or '<2025-01-20 14:30 +1w>'
    """
    # Parse ISO string but ignore timezone
    dt = datetime.fromisoformat(iso_datetime_str.replace('Z', '+00:00'))
    
    # Build base timestamp
    if include_time:
        timestamp = f"{dt.strftime('%Y-%m-%d %H:%M')}"
    else:
        timestamp = f"{dt.strftime('%Y-%m-%d')}"
    
    # Add repeat suffix if recurring
    if repeat_every and repeat_unit and repeat_type:
        repeat_suffix = build_repeat_suffix(repeat_every, repeat_unit, repeat_type)
        timestamp += f" {repeat_suffix}"
    
    return f"<{timestamp}>"


def find_heading_insertion_point(lines: List[str], target_heading: str) -> Optional[Tuple[int, int]]:
    """
    Find the insertion point for a TODO under a specific heading.
    
    Args:
        lines: List of file lines
        target_heading: The heading text to search for (without the * prefix)
    
    Returns:
        Tuple of (line index where TODO should be inserted, heading level) or None if heading not found
    """
    target_heading = target_heading.strip()
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check if this line is a heading that matches our target
        if line.startswith('*') and line.count('*') >= 1:
            # Extract heading text (remove * and any tags)
            heading_text = line.lstrip('*').strip()
            
            # Remove tags if present (anything after the last space that contains :)
            if ':' in heading_text and heading_text.endswith(':'):
                # Find the last space before tags
                words = heading_text.split()
                for j in range(len(words) - 1, -1, -1):
                    if ':' not in words[j]:
                        heading_text = ' '.join(words[:j+1])
                        break
                else:
                    # All words contain :, so it's just tags
                    continue
            
            # Check if this heading matches our target
            if heading_text == target_heading:
                # Found the heading! Now find where to insert the TODO
                heading_level = line.count('*')
                
                # Look for the end of this heading's content
                # We want to insert before any subheading or next heading of same/higher level
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    
                    # If we find another heading, check its level
                    if next_line.startswith('*'):
                        next_heading_level = next_line.count('*')
                        
                        # If it's same level or higher (fewer *), insert before it
                        if next_heading_level <= heading_level:
                            return j, heading_level
                
                # If we reach here, insert at the end of the file
                return len(lines), heading_level
    
    # Heading not found
    return None


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
    is_recurring: bool = False,
    recurring_field: Optional[str] = None,
    repeat_every: Optional[int] = None,
    repeat_unit: Optional[str] = None,
    repeat_type: Optional[str] = None,
    properties: Optional[dict] = None,
    body: Optional[str] = None,
    heading: Optional[str] = None
):
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
        is_recurring: Whether this TODO is recurring
        recurring_field: Which field to make recurring ("scheduled" or "deadline")
        repeat_every: Number for recurring pattern
        repeat_unit: Unit for recurring pattern ("hours", "days", "weeks", "months", "years")
        repeat_type: Type for recurring pattern ("standard", "from_completion", "catch_up")
        properties: Dict of properties for properties drawer
        body: Additional content/notes for the TODO
        heading: The heading under which the TODO should be filed
    
    Returns:
        Tuple of (TODO item text that was appended, generated UUID)
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
    
    # Determine which field gets the recurring pattern
    add_recurring_to_scheduled = is_recurring and recurring_field == "scheduled"
    add_recurring_to_deadline = is_recurring and recurring_field == "deadline"
    
    if scheduled:
        if add_recurring_to_scheduled:
            scheduled_timestamp = format_org_timestamp(
                scheduled, include_scheduled_time, 
                repeat_every, repeat_unit, repeat_type
            )
        else:
            scheduled_timestamp = format_org_timestamp(scheduled, include_scheduled_time)
    
    if deadline:
        if add_recurring_to_deadline:
            deadline_timestamp = format_org_timestamp(
                deadline, include_deadline_time,
                repeat_every, repeat_unit, repeat_type
            )
        else:
            deadline_timestamp = format_org_timestamp(deadline, include_deadline_time)
    
    # If both scheduled and deadline exist, put them on the same line
    if scheduled_timestamp and deadline_timestamp:
        additional_lines.append(f"SCHEDULED: {scheduled_timestamp} DEADLINE: {deadline_timestamp}")
    elif scheduled_timestamp:
        additional_lines.append(f"SCHEDULED: {scheduled_timestamp}")
    elif deadline_timestamp:
        additional_lines.append(f"DEADLINE: {deadline_timestamp}")
    
    # Always add properties drawer with generated ID
    if not properties:
        properties = {}
    
    # Generate UUID for this TODO (following org-id convention)
    generated_uuid = str(uuid.uuid4()).upper()
    properties["ID"] = generated_uuid
    
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
    
    # Prepare file path
    file_path_obj = Path(file_path)
    
    # Create directory if it doesn't exist
    file_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    # Handle heading-based filing vs. simple append
    if heading:
        # Read the entire file to find the heading
        if file_path_obj.exists():
            with open(file_path_obj, "r", encoding="utf-8") as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Find the target heading and insertion point
        result = find_heading_insertion_point(lines, heading)
        
        if result is not None:
            insertion_point, heading_level = result
            
            # Create TODO at one level deeper than the parent heading
            todo_level = "*" * (heading_level + 1)
            
            # Rebuild TODO with correct level
            todo_parts = [f"{todo_level} {state}"]
            
            # Add priority
            if priority:
                todo_parts.append(f"[#{priority}]")
            
            # Add title
            todo_parts.append(title)
            
            # Add tags
            if tags:
                tag_string = ":" + ":".join(tags) + ":"
                todo_parts.append(tag_string)
            
            corrected_todo_line = " ".join(todo_parts)
            
            # Rebuild the complete TODO text with correct heading level
            corrected_todo_text = corrected_todo_line
            if additional_lines:
                corrected_todo_text += "\n" + "\n".join(additional_lines)
            
            # Add body if provided (separated by blank line)
            if body:
                corrected_todo_text += "\n\n" + body.strip()
            
            # Insert the TODO under the found heading with proper spacing
            todo_lines = corrected_todo_text.split('\n')
            
            # Handle proper spacing - ensure exactly one blank line before and after TODO
            
            # Check if we need a blank line before the TODO
            need_blank_before = True
            if insertion_point > 0:
                prev_line = lines[insertion_point - 1].strip()
                if prev_line == '':
                    need_blank_before = False
            
            # Check if we need a blank line after the TODO  
            need_blank_after = True
            if insertion_point < len(lines):
                next_line = lines[insertion_point].strip()
                if next_line == '':
                    need_blank_after = False
            
            # Insert the TODO with proper spacing
            offset = 0
            
            # Add blank line before if needed
            if need_blank_before:
                lines.insert(insertion_point + offset, '\n')
                offset += 1
            
            # Insert the TODO lines
            for i, line in enumerate(todo_lines):
                lines.insert(insertion_point + offset + i, line + '\n')
            offset += len(todo_lines)
            
            # Add blank line after if needed
            if need_blank_after:
                lines.insert(insertion_point + offset, '\n')
            
            # Write the modified content back to file
            with open(file_path_obj, "w", encoding="utf-8") as f:
                f.writelines(lines)
        else:
            # Heading not found, create it and add the TODO under it (TODO as level 2)
            heading_text = f"* {heading}\n\n** {state}"
            
            # Add priority to the TODO
            if priority:
                heading_text += f" [#{priority}]"
            
            # Add title
            heading_text += f" {title}"
            
            # Add tags
            if tags:
                tag_string = ":" + ":".join(tags) + ":"
                heading_text += f" {tag_string}"
            
            # Add the rest of the TODO content
            if additional_lines:
                heading_text += "\n" + "\n".join(additional_lines)
            
            # Add body if provided
            if body:
                heading_text += "\n\n" + body.strip()
            
            # Append the new heading and TODO to file
            with open(file_path_obj, "a", encoding="utf-8") as f:
                f.write(f"\n{heading_text}\n")
    else:
        # No heading specified, append to end of file (original behavior)
        # Use smart spacing logic similar to heading insertion
        if file_path_obj.exists():
            with open(file_path_obj, "r", encoding="utf-8") as f:
                existing_content = f.read()
            
            # Check if file ends with content or blank lines
            if existing_content.strip():  # File has content
                # Check if file already ends with newline(s)
                if existing_content.endswith('\n\n'):
                    # Already has blank line at end, just add TODO
                    with open(file_path_obj, "a", encoding="utf-8") as f:
                        f.write(f"{todo_text}\n")
                elif existing_content.endswith('\n'):
                    # Ends with single newline, add blank line then TODO
                    with open(file_path_obj, "a", encoding="utf-8") as f:
                        f.write(f"\n{todo_text}\n")
                else:
                    # Doesn't end with newline, add newline + blank line + TODO
                    with open(file_path_obj, "a", encoding="utf-8") as f:
                        f.write(f"\n\n{todo_text}\n")
            else:
                # Empty file, just add TODO
                with open(file_path_obj, "w", encoding="utf-8") as f:
                    f.write(f"{todo_text}\n")
        else:
            # File doesn't exist, create it with TODO
            with open(file_path_obj, "w", encoding="utf-8") as f:
                f.write(f"{todo_text}\n")
    
    return todo_text, generated_uuid


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