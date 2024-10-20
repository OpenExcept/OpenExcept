import os
import shutil
from pathlib import Path

def cleanup_local_fs_openexcept_storage():
    local_fs_storage_path = os.path.expanduser("~/.openexcept")
    
    if Path(local_fs_storage_path).exists():
        try:
            shutil.rmtree(local_fs_storage_path)
            print(f"Successfully removed local filesystem storage at {local_fs_storage_path}")
        except Exception as e:
            print(f"Error while removing local filesystem storage at {local_fs_storage_path}: {e}")
    else:
        print(f"No local filesystem storage found at {local_fs_storage_path}")

if __name__ == "__main__":
    cleanup_local_fs_openexcept_storage()