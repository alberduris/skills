"""The Excalidraw+ API key, shared by the REST API and the MCP."""
import os
import sys


def api_key():
    key = os.environ.get("EXCALIDRAW_API_KEY")
    if not key:
        sys.exit("EXCALIDRAW_API_KEY is not set: export your Excalidraw+ API key in it")
    return key
