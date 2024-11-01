#!/usr/bin/env python3
import shutil
import os
from pathlib import Path

def cleanup_qdrant_storage():
    """Clean up Qdrant storage directory"""
    storage_path = os.path.expanduser("~/.openexcept")
    if os.path.exists(storage_path):
        shutil.rmtree(storage_path)
        print(f"Cleaned up Qdrant storage at {storage_path}")
    else:
        print(f"No Qdrant storage found at {storage_path}")

if __name__ == "__main__":
    cleanup_qdrant_storage() 