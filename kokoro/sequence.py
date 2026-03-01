"""
File-based sequence generator with lock-safe incrementing.

Provides unique IDs across processes/greenlets using file locking.
"""

import fcntl
from pathlib import Path


class FileSequence:
    """
    Thread/greenlet-safe sequence generator using file-based storage.
    
    Usage:
        seq = FileSequence("logs/session_counter.txt")
        unique_id = seq.next()
    """
    
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(exist_ok=True)
    
    def next(self) -> int:
        """Get next value in sequence (atomically increments)."""
        with open(self.path, "a+") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.seek(0)
            content = f.read().strip()
            current = int(content) if content else 0
            next_id = current + 1
            f.seek(0)
            f.truncate()
            f.write(str(next_id))
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        
        return next_id
    
    def current(self) -> int:
        """Get current value without incrementing."""
        if not self.path.exists():
            return 0
        return int(self.path.read_text().strip() or 0)
    
    def reset(self, value: int = 0) -> None:
        """Reset sequence to a specific value."""
        self.path.write_text(str(value))
