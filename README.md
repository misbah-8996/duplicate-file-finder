# 🔍 Duplicate File Finder

A fast, modern desktop app built with Python that scans folders for duplicate files and lets you safely remove them to free up storage space.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat-square&logo=python)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square)

---

## ✨ Features

- **Fast duplicate detection** — multi-stage pipeline (size → partial hash → full hash) avoids hashing every file, making scans significantly faster on large folders
- **Modern dark UI** — clean, colour-coded interface built with Tkinter
- **Non-blocking scans** — background threading keeps the GUI responsive even on folders with thousands of files
- **Live progress bar** — real-time feedback as files are scanned
- **Safe deletion** — duplicates are moved to the Recycle Bin via `send2trash`, not permanently deleted
- **Confirmation dialog** — warns you before any files are removed
- **Stats at a glance** — shows files found, duplicate groups, and recoverable space

---

## ScreenShots

![DuplicateFileFinder](<assets/ss1.jpg>)
![DuplicateFileFinder](<assets/ss2.jpg>)
![DuplicateFileFinder](<assets/ss3.jpg>)


---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/misbah-8996/duplicate-file-finder.git
   cd duplicate-file-finder
   ```

2. Install dependencies:
   ```bash
   pip install send2trash
   ```

3. Run the app:
   ```bash
   python main.py
   ```

---

## 🗂️ Project Structure

```
duplicate-file-finder/
│
├── main.py               # Entry point
├── gui.py                # Tkinter GUI — all UI logic
├── scanner.py            # Walks the folder and collects file paths
├── duplicate_detector.py # Multi-stage duplicate detection engine
├── deleteduplicates.py   # Moves duplicate files to Recycle Bin
├── hasher.py             # File hashing utilities
└── README.md
```

---

## ⚙️ How It Works

Duplicate detection runs in three stages to avoid unnecessary I/O:

| Stage | Method | Cost |
|-------|--------|------|
| 1 | Group files by **size** | Free — no file reads |
| 2 | **Partial hash** (first 1 KB) | Very cheap — tiny read |
| 3 | **Full MD5 hash** | Only for files that passed stages 1 & 2 |

This means ~90% of files are eliminated before any full hash is ever computed, making the tool fast even on folders with thousands of files.

---

## 🛠️ Built With

- [Python](https://www.python.org/) — core language
- [Tkinter](https://docs.python.org/3/library/tkinter.html) — desktop GUI
- [send2trash](https://github.com/arsenetar/send2trash) — safe deletion to Recycle Bin
- [hashlib](https://docs.python.org/3/library/hashlib.html) — file hashing
- [threading](https://docs.python.org/3/library/threading.html) — non-blocking background scans

---

## 📄 License

Feel free to use, modify, and distribute it for educational and personal projects.


---

## 🙋‍♂️ Author

**Misbah Javed**  
[LinkedIn](www.linkedin.com/in/misbah-javed-6b2905151) · [GitHub](https://github.com/misbah-8996)
