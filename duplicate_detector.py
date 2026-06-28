import hashlib
import os
from collections import defaultdict

def get_quick_hash(filepath, size=1024):
    """Hash only the first 1KB of a file"""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            hasher.update(f.read(size))
    except (OSError, IOError):
        return None
    return hasher.hexdigest()

def get_full_hash(filepath):
    """Full MD5 hash of a file"""
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):  # 64KB chunks
                hasher.update(chunk)
    except (OSError, IOError):
        return None
    return hasher.hexdigest()

def find_duplicates(files):
    duplicates = defaultdict(list)

    # Stage 1: Group by file size (no I/O at all)
    size_groups = defaultdict(list)
    for filepath in files:
        try:
            size = os.path.getsize(filepath)
            if size > 0:  # skip empty files
                size_groups[size].append(filepath)
        except OSError:
            continue

    # Keep only groups with more than one file
    size_groups = {s: p for s, p in size_groups.items() if len(p) > 1}
    print(f"Stage 1: {len(size_groups)} size groups with potential duplicates")

    # Stage 2: Quick hash (first 1KB only)
    quick_groups = defaultdict(list)
    for paths in size_groups.values():
        for filepath in paths:
            h = get_quick_hash(filepath)
            if h:
                quick_groups[h].append(filepath)

    quick_groups = {h: p for h, p in quick_groups.items() if len(p) > 1}
    print(f"Stage 2: {len(quick_groups)} groups after quick hash")

    # Stage 3: Full hash only on survivors
    for paths in quick_groups.values():
        for filepath in paths:
            h = get_full_hash(filepath)
            if h:
                duplicates[h].append(filepath)

    return {h: p for h, p in duplicates.items() if len(p) > 1}

def calculate_saved_space(duplicates):
    saved = 0
    for paths in duplicates.values():
        if len(paths) > 1:
            size = os.path.getsize(paths[0])
            saved += size * (len(paths) - 1)
    return saved