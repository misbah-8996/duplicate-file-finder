import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from scanner import scan_directory
from duplicate_detector import find_duplicates, calculate_saved_space
from deleteduplicates import delete_duplicates
import threading
import os

# ── Palette ────────────────────────────────────────────────────────────────────
BG        = "#1a1a2e"   # deep navy page
SURFACE   = "#16213e"   # card surface
SURFACE2  = "#0f3460"   # raised element
ACCENT    = "#e94560"   # coral-red accent
ACCENT2   = "#533483"   # purple secondary
TEXT      = "#eaeaea"   # primary text
TEXT_MUTED= "#8892a4"   # secondary text
SUCCESS   = "#4ecca3"   # teal success
WARNING   = "#f5a623"   # amber warning
BORDER    = "#2a2a4a"   # subtle border
FONT      = "Segoe UI"

class DuplicateFileFinderGUI:

    # ── Folder selection ───────────────────────────────────────────────────────
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.status_var.set("Folder selected — ready to scan.")

    # ── Scan (runs worker in background thread) ────────────────────────────────
    def scan_folder(self):
        folder = self.folder_path.get()
        if not folder:
            self.status_var.set("⚠  Select a folder first.")
            return

        self.scan_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
        self.status_var.set("Scanning…")
        self.results.config(state="normal")
        self.results.delete(1.0, tk.END)
        self.progress["value"] = 0
        self._update_stats(0, 0, 0)

        threading.Thread(target=self._scan_worker, args=(folder,), daemon=True).start()

    def _scan_worker(self, folder):
        try:
            total = sum(len(fs) for _, _, fs in os.walk(folder))
            self.root.after(0, lambda: self.progress.config(maximum=max(total, 1)))

            files = []
            for root_dir, _, filenames in os.walk(folder):
                for fn in filenames:
                    files.append(os.path.normpath(os.path.join(root_dir, fn)))
                    v = len(files)
                    self.root.after(0, lambda v=v: self._tick(v))

            self.root.after(0, lambda: self.status_var.set("Detecting duplicates…"))
            self.duplicates = find_duplicates(files)
            saved = calculate_saved_space(self.duplicates)
            self.root.after(0, lambda: self._scan_done(self.duplicates, saved))

        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))
            self.root.after(0, self._re_enable)

    def _tick(self, v):
        self.progress["value"] = v

    def _scan_done(self, duplicates, saved):
        total  = sum(len(p) for p in duplicates.values())
        groups = len(duplicates)
        mb     = round(saved / (1024 * 1024), 2)

        self._update_stats(total, groups, mb)

        self.results.config(state="normal")
        self.results.delete(1.0, tk.END)

        if not duplicates:
            self.results.insert(tk.END, "  No duplicates found.\n", "muted")
        else:
            for i, (fhash, paths) in enumerate(duplicates.items(), 1):
                self.results.insert(tk.END, f"\n  Group {i}  ", "group_num")
                self.results.insert(tk.END, f"({fhash[:12]}…)\n", "hash")
                self.results.insert(tk.END, "  " + "─" * 64 + "\n", "divider")
                for j, path in enumerate(paths):
                    tag = "keep" if j == 0 else "dupe"
                    label = "  ✔  keep  " if j == 0 else "  ✖  dupe  "
                    self.results.insert(tk.END, label, tag + "_label")
                    self.results.insert(tk.END, path + "\n", tag)

        self.results.config(state="disabled")
        self.progress["value"] = self.progress["maximum"]
        self.status_var.set(f"Scan complete — {groups} duplicate group(s) found.")
        self._re_enable()

    # ── Delete ─────────────────────────────────────────────────────────────────
    def delete_duplicates_action(self):
        if not self.duplicates:
            self.status_var.set("Run a scan first.")
            return
        
        groups = len(self.duplicates)
        total  = sum(len(p) - 1 for p in self.duplicates.values())
        
        confirmed = messagebox.askyesno(
            title="Confirm deletion",
            message=f"This will move {total} file(s) across {groups} group(s) to the Recycle Bin.\n\nAre you sure?",
            icon="warning"
        )
        
        if not confirmed:
            self.status_var.set("Deletion cancelled.")
            return
    
        self.scan_btn.config(state="disabled")
        self.delete_btn.config(state="disabled")
        self.status_var.set("Moving duplicates to recycle bin…")
        threading.Thread(target=self._delete_worker, daemon=True).start()

    def _delete_worker(self):
        try:
            delete_duplicates(self.duplicates)
            self.duplicates = {}
            self.root.after(0, lambda: self.status_var.set("Duplicates deleted. Rescanning…"))
            self.root.after(0, self.scan_folder)
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Delete error: {e}"))
            self.root.after(0, self._re_enable)

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _re_enable(self):
        self.scan_btn.config(state="normal")
        self.delete_btn.config(state="normal")

    def _update_stats(self, files, groups, mb):
        self.stat_files.config(text=str(files))
        self.stat_groups.config(text=str(groups))
        self.stat_space.config(text=f"{mb} MB")

    # ── Build UI ───────────────────────────────────────────────────────────────
    def __init__(self):
        self.root = tk.Tk()
        self.duplicates = {}
        self.folder_path = tk.StringVar()
        self.status_var  = tk.StringVar(value="Ready")

        self.root.title("Duplicate File Finder")
        self.root.geometry("960x700")
        self.root.minsize(800, 580)
        self.root.configure(bg=BG)

        self._apply_styles()
        self._build_header()
        self._build_folder_row()
        self._build_buttons()
        self._build_progress()
        self._build_stats()
        self._build_results()
        self._build_statusbar()

        self.root.mainloop()

    # ── Styles ─────────────────────────────────────────────────────────────────
    def _apply_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TProgressbar",
            troughcolor=SURFACE, background=ACCENT,
            bordercolor=BORDER, lightcolor=ACCENT, darkcolor=ACCENT,
            thickness=6)

    # ── Header ─────────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self.root, bg=SURFACE, pady=18)
        hdr.pack(fill="x")

        tk.Label(hdr, text="⬡", font=(FONT, 22), bg=SURFACE,
                 fg=ACCENT).pack(side="left", padx=(24, 8))

        tk.Label(hdr, text="Duplicate File Finder",
                 font=(FONT, 20, "bold"), bg=SURFACE,
                 fg=TEXT).pack(side="left")

        tk.Label(hdr, text="Find and remove duplicate files fast",
                 font=(FONT, 11), bg=SURFACE,
                 fg=TEXT_MUTED).pack(side="left", padx=16)

        # thin accent line under header
        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill="x")

    # ── Folder row ─────────────────────────────────────────────────────────────
    def _build_folder_row(self):
        row = tk.Frame(self.root, bg=BG, pady=20)
        row.pack(fill="x", padx=28)

        tk.Label(row, text="FOLDER", font=(FONT, 9, "bold"),
                 bg=BG, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        inner = tk.Frame(row, bg=SURFACE, bd=0,
                         highlightthickness=1, highlightbackground=BORDER)
        inner.pack(fill="x")

        entry = tk.Entry(inner, textvariable=self.folder_path,
                         font=(FONT, 12), bg=SURFACE, fg=TEXT,
                         insertbackground=TEXT, relief="flat",
                         bd=0, highlightthickness=0)
        entry.pack(side="left", fill="x", expand=True, padx=14, pady=10)

        browse_btn = tk.Button(inner, text="Browse",
                               font=(FONT, 11), bg=ACCENT2, fg=TEXT,
                               activebackground="#6a4aa0", activeforeground=TEXT,
                               relief="flat", bd=0, padx=18, pady=8,
                               cursor="hand2", command=self.select_folder)
        browse_btn.pack(side="right", padx=4, pady=4)

    # ── Action buttons ─────────────────────────────────────────────────────────
    def _build_buttons(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=28, pady=(0, 16))

        self.scan_btn = tk.Button(row, text="⟳  Scan folder",
                                  font=(FONT, 12, "bold"), bg=ACCENT, fg="#fff",
                                  activebackground="#c73652", activeforeground="#fff",
                                  relief="flat", bd=0, padx=24, pady=10,
                                  cursor="hand2", command=self.scan_folder)
        self.scan_btn.pack(side="left", padx=(0, 10))

        self.delete_btn = tk.Button(row, text="✖  Delete duplicates",
                                    font=(FONT, 12), bg=SURFACE2, fg=TEXT,
                                    activebackground="#1a4a80", activeforeground=TEXT,
                                    relief="flat", bd=0, padx=24, pady=10,
                                    cursor="hand2", command=self.delete_duplicates_action)
        self.delete_btn.pack(side="left")

    # ── Progress bar ───────────────────────────────────────────────────────────
    def _build_progress(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=28, pady=(0, 8))
        self.progress = ttk.Progressbar(row, orient="horizontal",
                                        mode="determinate", style="TProgressbar")
        self.progress.pack(fill="x")

    # ── Stats row ──────────────────────────────────────────────────────────────
    def _build_stats(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", padx=28, pady=(4, 12))

        def stat_card(parent, label):
            card = tk.Frame(parent, bg=SURFACE, padx=20, pady=14,
                            highlightthickness=1, highlightbackground=BORDER)
            card.pack(side="left", padx=(0, 10))
            val = tk.Label(card, text="0", font=(FONT, 22, "bold"),
                           bg=SURFACE, fg=SUCCESS)
            val.pack()
            tk.Label(card, text=label, font=(FONT, 9),
                     bg=SURFACE, fg=TEXT_MUTED).pack()
            return val

        self.stat_files  = stat_card(row, "FILES FOUND")
        self.stat_groups = stat_card(row, "DUPLICATE GROUPS")
        self.stat_space  = stat_card(row, "SPACE RECOVERABLE")
        self.stat_space.config(fg=WARNING)

    # ── Results area ───────────────────────────────────────────────────────────
    def _build_results(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="both", expand=True, padx=28, pady=(0, 8))

        tk.Label(frame, text="RESULTS", font=(FONT, 9, "bold"),
                 bg=BG, fg=TEXT_MUTED).pack(anchor="w", pady=(0, 6))

        self.results = tk.Text(frame, font=("Consolas", 11),
                               bg=SURFACE, fg=TEXT,
                               insertbackground=TEXT, relief="flat",
                               bd=0, padx=10, pady=8,
                               wrap="none", state="disabled",
                               highlightthickness=1, highlightbackground=BORDER)

        scroll_y = tk.Scrollbar(frame, orient="vertical",
                                command=self.results.yview, bg=SURFACE)
        scroll_x = tk.Scrollbar(frame, orient="horizontal",
                                command=self.results.xview, bg=SURFACE)
        self.results.configure(yscrollcommand=scroll_y.set,
                               xscrollcommand=scroll_x.set)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.results.pack(fill="both", expand=True)

        # text tags
        self.results.tag_config("group_num",  foreground=ACCENT,   font=("Consolas", 11, "bold"))
        self.results.tag_config("hash",       foreground=TEXT_MUTED)
        self.results.tag_config("divider",    foreground=BORDER)
        self.results.tag_config("keep_label", foreground=SUCCESS,   font=("Consolas", 10, "bold"))
        self.results.tag_config("keep",       foreground=TEXT)
        self.results.tag_config("dupe_label", foreground=ACCENT,    font=("Consolas", 10, "bold"))
        self.results.tag_config("dupe",       foreground=TEXT_MUTED)
        self.results.tag_config("muted",      foreground=TEXT_MUTED)

        self.results.config(state="normal")
        self.results.insert(tk.END, "\n  Select a folder above and click Scan folder to begin.\n", "muted")
        self.results.config(state="disabled")

    # ── Status bar ─────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=SURFACE, pady=6)
        bar.pack(fill="x", side="bottom")
        tk.Frame(bar, bg=ACCENT2, width=4).pack(side="left", fill="y")
        tk.Label(bar, textvariable=self.status_var,
                 font=(FONT, 10), bg=SURFACE, fg=TEXT_MUTED,
                 anchor="w").pack(side="left", padx=12)


if __name__ == "__main__":
    DuplicateFileFinderGUI()