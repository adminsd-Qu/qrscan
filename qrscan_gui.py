#!/usr/bin/env python3
"""QR Code Scanner — Windows Desktop GUI.

tkinter dialog: paste / browse image path, decode QR codes and barcodes.
Supports drag-and-drop from Explorer (Win32 WM_DROPFILES).
"""

import ctypes
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from qrscan import decode_image

WM_DROPFILES = 0x0233

# -- 64-bit Win32 API signatures -----------------------------------------------
# windll auto-detection guesses wrong on 64-bit Python for LONG_PTR parameters.
# Set explicit argtypes once at module level.

_ct = ctypes

_ct.windll.comctl32.DefSubclassProc.argtypes = [
    _ct.c_void_p, _ct.c_uint, _ct.c_void_p, _ct.c_void_p]
_ct.windll.comctl32.DefSubclassProc.restype = _ct.c_longlong
_ct.windll.comctl32.SetWindowSubclass.restype = _ct.c_bool

_ct.windll.shell32.DragQueryFileW.argtypes = [
    _ct.c_void_p, _ct.c_uint, _ct.c_void_p, _ct.c_uint]
_ct.windll.shell32.DragQueryFileW.restype = _ct.c_uint
_ct.windll.shell32.DragFinish.argtypes = [_ct.c_void_p]

SUBCLASSPROC = _ct.WINFUNCTYPE(
    _ct.c_longlong,     # LRESULT
    _ct.c_void_p,       # HWND
    _ct.c_uint,         # UINT
    _ct.c_void_p,       # WPARAM
    _ct.c_longlong,     # LPARAM
    _ct.c_ulonglong,    # UINT_PTR  uIdSubclass
    _ct.c_ulonglong,    # DWORD_PTR dwRefData
)


def _resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base, rel)


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class QRScannerApp(tk.Tk):

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
        self.after(100, self._enable_drag_drop)

    # -- window ------------------------------------------------------------

    def _center_window(self):
        ws, hs = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (ws - self.WIDTH) // 2
        y = (hs - self.HEIGHT) // 2
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}")

    # -- UI ----------------------------------------------------------------

    def _build_ui(self):
        pad = {"padx": 12, "pady": (12, 0)}
        pad_sm = {"padx": 12, "pady": (4, 0)}
        pad_last = {"padx": 12, "pady": (4, 12)}

        # Row 0: file path
        ttk.Label(self, text="图片文件:").grid(row=0, column=0, sticky="w", **pad)
        self._entry_path = ttk.Entry(self, textvariable=self._path_var)
        self._entry_path.grid(row=0, column=1, sticky="ew", **pad_sm)
        ttk.Button(self, text="浏览", command=self._browse).grid(
            row=0, column=2, **pad_sm)
        self.columnconfigure(1, weight=1)

        # Row 1: hint
        ttk.Label(self, text="支持从资源管理器拖入图片文件", foreground="gray").grid(
            row=1, column=1, sticky="w", padx=12, pady=(0, 0))

        # Row 2: decode button
        ttk.Button(self, text="解码", command=self._decode).grid(
            row=2, column=0, columnspan=3, pady=10)

        # Row 3: result area
        ttk.Label(self, text="结果:").grid(row=3, column=0, sticky="nw", **pad)
        self._txt_result = tk.Text(
            self, wrap="word", width=50, height=10,
            relief="sunken", borderwidth=2, font=("Consolas", 10),
            state="disabled")
        self._txt_result.grid(row=3, column=1, columnspan=2, sticky="ew", **pad_sm)
        scroll = ttk.Scrollbar(self, orient="vertical",
                               command=self._txt_result.yview)
        scroll.grid(row=3, column=3, sticky="ns", pady=(4, 0), padx=(0, 12))
        self._txt_result["yscrollcommand"] = scroll.set
        self.rowconfigure(3, weight=1)

        # Row 4: help button (right-aligned)
        frame_bottom = ttk.Frame(self)
        frame_bottom.grid(row=4, column=0, columnspan=4, sticky="ew", **pad_last)
        frame_bottom.columnconfigure(0, weight=1)
        ttk.Button(frame_bottom, text="帮助", command=self._open_help).grid(
            row=0, column=1, sticky="e")

    # -- drag-and-drop ------------------------------------------------------

    def _enable_drag_drop(self):
        """Register WM_DROPFILES via SetWindowSubclass.
        Subclass (not replace) keeps Tk's window procedure intact."""
        self.update_idletasks()
        hwnd = int(self.frame(), 16)

        @SUBCLASSPROC
        def _subclass_proc(hwnd, msg, wparam, lparam, _uid, _ref):
            if msg == WM_DROPFILES:
                buf = ctypes.create_unicode_buffer(260)
                ctypes.windll.shell32.DragQueryFileW(wparam, 0, buf, 260)
                ctypes.windll.shell32.DragFinish(wparam)
                self._path_var.set(buf.value)
                return 0
            return ctypes.windll.comctl32.DefSubclassProc(
                hwnd, msg, wparam, lparam)

        self._subclass_ref = _subclass_proc  # prevent GC

        ctypes.windll.comctl32.SetWindowSubclass(hwnd, _subclass_proc, 1, 0)
        ctypes.windll.shell32.DragAcceptFiles(hwnd, True)

    # -- actions ------------------------------------------------------------

    def _on_path_change(self, *_):
        """Auto-strip double-quotes pasted via Ctrl+Shift+C."""
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
            ])
        if path:
            self._path_var.set(path)

    def _decode(self):
        path = self._path_var.get()
        if not path:
            messagebox.showwarning("提示", "请先输入或选择图片文件路径。")
            return
        results = decode_image(path)
        if results is None:
            messagebox.showerror("错误", f"无法解码图片：\n{path}")
            return
        self._txt_result.config(state="normal")
        self._txt_result.delete("1.0", tk.END)
        if results:
            lines = [r.data.decode("utf-8", errors="replace") for r in results]
            self._txt_result.insert("1.0", "\n".join(lines))
        else:
            self._txt_result.insert("1.0", "未发现二维码或条形码。")
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
    QRScannerApp().mainloop()


if __name__ == "__main__":
    main()
