from scanner import scan_directory
from hasher import calculate_hash
from duplicate_detector import calculate_saved_space, find_duplicates
from deleteduplicates import delete_duplicates
from gui import DuplicateFileFinderGUI


DuplicateFileFinderGUI()  # Start the GUI
