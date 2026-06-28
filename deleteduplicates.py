from send2trash import send2trash
import os

def delete_duplicates(duplicates):
    for paths in duplicates.values():
        if len(paths) > 1:
            for duplicate in paths[1:]:
                clean_path = os.path.normpath(duplicate)
                send2trash(clean_path)
                print(f"Moved to Recycle Bin: {clean_path}")