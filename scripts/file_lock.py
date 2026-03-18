# File Lock Utility
# Prevents concurrent writes to shared data files

import fcntl
import os
import time
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def file_lock(filepath: Path, timeout: int = 10):
    """
    Context manager for file locking.
    
    Usage:
        with file_lock(Path("data/tasks.json")):
            # Read/write file safely
            data = json.loads(filepath.read_text())
            ...
            filepath.write_text(json.dumps(data))
    """
    lockfile = filepath.parent / f".{filepath.name}.lock"
    
    # Wait for lock
    start_time = time.time()
    while True:
        try:
            fd = os.open(str(lockfile), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            break
        except FileExistsError:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Could not acquire lock for {filepath}")
            time.sleep(0.1)
    
    try:
        yield
    finally:
        os.close(fd)
        try:
            os.remove(lockfile)
        except FileNotFoundError:
            pass


def atomic_json_read(filepath: Path, default=None):
    """Atomically read JSON file with locking."""
    if not filepath.exists():
        return default
    
    with file_lock(filepath):
        try:
            return json.loads(filepath.read_text())
        except (json.JSONDecodeError, IOError):
            return default


def atomic_json_write(filepath: Path, data):
    """Atomically write JSON file with locking."""
    with file_lock(filepath):
        # Write to temp file first
        temp_file = filepath.with_suffix('.tmp')
        temp_file.write_text(json.dumps(data, indent=2))
        # Atomic rename
        temp_file.rename(filepath)


def atomic_json_update(filepath: Path, update_fn):
    """Atomically update JSON file with locking."""
    with file_lock(filepath):
        try:
            data = json.loads(filepath.read_text()) if filepath.exists() else {}
        except (json.JSONDecodeError, IOError):
            data = {}
        
        update_fn(data)
        
        temp_file = filepath.with_suffix('.tmp')
        temp_file.write_text(json.dumps(data, indent=2))
        temp_file.rename(filepath)
