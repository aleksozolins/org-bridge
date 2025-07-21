#!/usr/bin/env python3
"""Generate a secure API key for org-bridge server."""

import uuid

# Generate a secure API key using UUID4
api_key = str(uuid.uuid4())

print(f"Generated API key: {api_key}")
print()
print("Add this to your environment:")
print(f"  export ORG_BRIDGE_API_KEY={api_key}")
print()
print("Or add to .env file:")
print(f"  echo 'ORG_BRIDGE_API_KEY={api_key}' >> .env")
print()
print("Or add to systemd service:")
print(f"  Environment=ORG_BRIDGE_API_KEY={api_key}") 