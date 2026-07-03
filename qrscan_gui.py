#!/usr/bin/env python3
"""QR Code Scanner — Windows Desktop GUI.

A portable dialog-based QR code / barcode scanner.
Input an image file path, decode and copy the result.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from qrscan import decode_image

# ---------------------------------------------------------------------------
# Resource path helper (works both in dev and PyInstaller bundle)
# ---------------------------------------------------------------------------

def _resource_path(rel):
    """Resolve *rel* relative to the bundled resource directory (PyInstaller)
    or the script directory (development)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base, rel)


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class QRScannerApp(tk.Tk):
    """Main application window."""

    WIDTH = 520
    HEIGHT = 380

    def __init__(self):
        super().__init__()
        self.title("QR Code Scanner")
        self.resizable(False, False)
        self._center_window()

        self._path_var = tk.StringVar()
        self._path_var.trace_add("write", self._on_path_change)
        self._build_ui()

    # -- window management ------------------------------------------------

    def _center_window(self):
        ws = self.winfo_screenwidth()
        hs = self.winfo_screenheight()
        x = (ws - self.WIDTH) // 2
        y = (hs - self.HEIGHT) // 2
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

    # -- UI construction --------------------------------------------------

    def _build_ui(self):
        pad = {"padx": 12, "pady": (12, 0)}
        pad_sm = {"padx": 12, "pady": (4, 0)}
        pad_last = {"padx": 12, "pady": (4, 12)}

        # ---- Row 0: File path -------------------------------------------
        row = 0
        ttk.Label(self, text="图片文件:").grid(row=row, column=0, sticky="w", **pad)

        self._entry_path = ttk.Entry(self, textvariable=self._path_var)
        self._entry_path.grid(row=row, column=1, sticky="ew", **pad_sm)

        ttk.Button(self, text="浏览", command=self._browse).grid(
            row=row, column=2, **pad_sm
        )

        self.columnconfigure(1, weight=1)

        # ---- Row 1: Decode button ---------------------------------------
        row = 1
        ttk.Button(self, text="解码", command=self._decode).grid(
            row=row, column=0, columnspan=3, pady=10
        )

        # ---- Row 2: Result area -----------------------------------------
        row = 2
        ttk.Label(self, text="结果:").grid(row=row, column=0, sticky="nw", **pad)

        self._txt_result = tk.Text(
            self,
            wrap="word",
            width=50,
            height=10,
            relief="sunken",
            borderwidth=2,
            font=("Consolas", 10),
            state="disabled",
        )
        self._txt_result.grid(row=row, column=1, columnspan=2, sticky="ew", **pad_sm)

        # Scrollbar for the result area
        scroll = ttk.Scrollbar(self, orient="vertical", command=self._txt_result.yview)
        scroll.grid(row=row, column=3, sticky="ns", pady=(4, 0), padx=(0, 12))
        self._txt_result["yscrollcommand"] = scroll.set

        self.rowconfigure(row, weight=1)

        # ---- Row 3: Help button (right-aligned) -------------------------
        row = 3
        frame_bottom = ttk.Frame(self)
        frame_bottom.grid(row=row, column=0, columnspan=4, sticky="ew", **pad_last)
        frame_bottom.columnconfigure(0, weight=1)  # push button to the right

        ttk.Button(frame_bottom, text="帮助", command=self._open_help).grid(
            row=0, column=1, sticky="e"
        )

    # -- actions ----------------------------------------------------------

    def _on_path_change(self, *_):
        """Auto-strip surrounding double-quotes pasted via Ctrl+Shift+C."""
        path = self._path_var.get()
        cleaned = path.strip('"\' ')
        if cleaned != path:
            self._path_var.set(cleaned)

    def _browse(self):
        path = filedialog.askopenfilename(
            title="选择二维码图片",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp"),
                ("所有文件", "*.*"),
            ],
        )
        if path:
            self._entry_path.delete(0, tk.END)
            self._entry_path.insert(0, path)

    def _decode(self):
        path = self._path_var.get().strip('"\' ')
        if not path:
            messagebox.showwarning("提示", "请先输入或选择图片文件路径。")
            return

        results = decode_image(path)

        # decode_image returns None on error (already printed to stderr)
        if results is None:
            messagebox.showerror("错误", f"无法解码图片：\n{path}")
            return

        self._txt_result.config(state="normal")
        self._txt_result.delete("1.0", tk.END)

        if not results:
            self._txt_result.insert("1.0", "未发现二维码或条形码。")
        else:
            lines = []
            for r in results:
                text = r.data.decode("utf-8", errors="replace")
                lines.append(text)
            self._txt_result.insert("1.0", "\n".join(lines))

        self._txt_result.config(state="disabled")

    def _open_help(self):
        readme_path = _resource_path("README.md")
        if not os.path.isfile(readme_path):
            messagebox.showerror("错误", "帮助文件（README.md）未找到。")
            return
        try:
            os.startfile(readme_path)
        except Exception as exc:
            messagebox.showerror("错误", f"无法打开帮助文件：{exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = QRScannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
