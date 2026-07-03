# qrscan — QR Code & Barcode Decoder

A lightweight QR code and barcode decoder for Windows. Comes in two flavors:

- **GUI** (`qrscan_gui.py`) — Desktop dialog, paste path or browse, copy result
- **CLI** (`qrscan.py`) — Command-line batch processing

The pre-built **`dist/QRScanner.exe`** is a portable Windows x86-64 executable — no Python or installation required.

---

## Quick Start

### GUI (Desktop App)

```
dist/QRScanner.exe
```

1. Enter an image file path (or click **浏览** to browse)
2. Click **解码**
3. Select and copy the decoded result with `Ctrl+C`
4. Click **帮助** to view this README

**Tip:** In Explorer, `Ctrl+Shift+C` on a file copies its path as `"C:\path\file.jpg"` — paste it directly into the dialog; the program automatically strips the quotes.

### CLI (Terminal)

```bash
pip install -r requirements.txt

python qrscan.py menu.png              # Decode a single image
python qrscan.py -j menu.png           # JSON output
python qrscan.py -q *.png              # Quiet mode, raw data only
python qrscan.py -t image.jpg          # Include symbology type
```

---

## GUI Usage

```
┌──────────────────────────────────────┐
│  QR Code Scanner                     │
│                                      │
│  图片文件: [__________________] [浏览]│
│                                      │
│  [解码]                              │
│                                      │
│  结果:                               │
│  ┌──────────────────────────────────┐│
│  │ (selectable decoded text)        ││
│  └──────────────────────────────────┘│
│                          [帮助]      │
└──────────────────────────────────────┘
```

- **图片文件** — Type or paste the image path, or click **浏览** to pick a file
- **解码** — Decode all barcodes found in the image
- **结果** — Decoded text appears here; select and `Ctrl+C` to copy
- **帮助** — Opens this README in your default `.md` viewer

---

## CLI Usage

```
qrscan.py [-h] [-j] [-t] [-q] [--version] FILE [FILE ...]

Positional arguments:
  FILE              One or more image files to scan

Options:
  -h, --help        Show help
  -j, --json        Output as structured JSON
  -t, --types       Include symbology type (QRCODE, CODE128, etc.)
  -q, --quiet       Raw data only, one per line — no headers
  --version         Show version number
```

---

## Supported Formats

PNG, JPG, BMP, GIF, TIFF, WebP — any format [Pillow](https://python-pillow.org/) can read.

## Supported Barcode Types

QRCODE, EAN-13, EAN-8, UPC-A, UPC-E, CODE-128, CODE-39, Data Matrix, PDF417, and more — everything [libzbar](https://github.com/mchehab/zbar) supports.

---

## Build Your Own EXE

```bash
pip install pyinstaller
cd qrscan
pyinstaller --onefile --noconsole --name "QRScanner" ^
    --add-data "README.md;." ^
    --add-binary "%USERPROFILE%\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\pyzbar\libiconv.dll;pyzbar" ^
    --add-binary "%USERPROFILE%\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\pyzbar\libzbar-64.dll;pyzbar" ^
    qrscan_gui.py
```

The output `dist/QRScanner.exe` is a standalone 32 MB portable binary.

---

## Project Structure

```
qrscan/
├── qrscan.py              # CLI decoder (core logic)
├── qrscan_gui.py          # GUI desktop app (tkinter)
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── dist/
    └── QRScanner.exe      # Pre-built portable exe
```

---

## Exit Codes (CLI only)

| Code | Meaning |
|------|---------|
| 0    | Success — at least one barcode found |
| 1    | No barcodes found in any file |
| 2    | File error (not found / permission denied) |

---

## Running Tests

```bash
pip install pytest qrcode
pytest tests/ -v
```
