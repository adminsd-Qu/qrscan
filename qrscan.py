#!/usr/bin/env python3
"""Decode QR codes and barcodes from image files.

Usage:
    qrscan.py image.png              # Decode a single image
    qrscan.py -j image.png           # JSON output
    qrscan.py -q *.png               # Quiet mode, raw data only
    qrscan.py -t image.jpg           # Include symbology type in output
"""

import argparse
import json
import sys

from PIL import Image, UnidentifiedImageError
from pyzbar import pyzbar

VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def decode_image(path):
    """Decode all barcodes in an image file.

    Returns a list of Decoded objects (empty list if none found),
    or prints an error to stderr and returns None on failure.
    """
    try:
        img = Image.open(path)
        return pyzbar.decode(img.convert("RGB"))
    except FileNotFoundError:
        print(f"Error: '{path}' - file not found.", file=sys.stderr)
    except PermissionError:
        print(f"Error: '{path}' - permission denied.", file=sys.stderr)
    except UnidentifiedImageError:
        print(f"Error: '{path}' - not a recognised image format.", file=sys.stderr)
    except (OSError, SyntaxError):
        print(f"Error: '{path}' - cannot decode image (file may be damaged).",
              file=sys.stderr)
    except Exception as exc:
        print(f"Error: '{path}' - decoder error: {exc}", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def format_text(file_results, *, show_types=False, quiet=False):
    """Format decoding results as plain text.

    file_results: dict of {path: list_of_Decoded | None}
        None values represent files that errored.
    """
    lines = []
    for path, results in file_results.items():
        if results is None:
            continue  # Error already printed to stderr

        if quiet:
            for r in results:
                prefix = f"[{r.type}] " if show_types else ""
                lines.append(f"{prefix}{r.data.decode('utf-8', errors='replace')}")
            continue

        multi = len(file_results) > 1 or len(results) > 1

        if multi:
            count = f" ({len(results)} codes found)" if results else ""
            lines.append(f"=== {path}{count} ===")

        if not results:
            lines.append("No QR codes found.")
        else:
            for i, r in enumerate(results, start=1):
                label = f"[{i}] " if multi else ""
                type_tag = f"[{r.type}] " if show_types else ""
                text = r.data.decode("utf-8", errors="replace")
                lines.append(f"{label}{type_tag}{text}")

        if multi:
            lines.append("")

    return "\n".join(lines).rstrip()


def format_json(file_results):
    """Format decoding results as JSON."""
    output = []
    for path, results in file_results.items():
        entry = {"file": path, "results": []}
        if results:
            for r in results:
                entry["results"].append({
                    "data": r.data.decode("utf-8", errors="replace"),
                    "type": r.type,
                })
        output.append(entry)
    return json.dumps(output, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Decode QR codes and barcodes from image files.",
    )
    parser.add_argument(
        "files", metavar="FILE", nargs="+",
        help="One or more image files to scan",
    )
    parser.add_argument(
        "-j", "--json", action="store_true",
        help="Output results as structured JSON",
    )
    parser.add_argument(
        "-t", "--types", action="store_true",
        help="Include barcode symbology type in output",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="Output only the decoded data, one per line (no headers)",
    )
    parser.add_argument(
        "--version", action="version",
        version=f"qrscan {VERSION}",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    file_results = {path: decode_image(path) for path in args.files}

    # Determine exit code
    any_found = any(
        r is not None and len(r) > 0 for r in file_results.values())
    any_error = any(r is None for r in file_results.values())

    if any_found:
        exit_code = 0
    elif any_error:
        exit_code = 2
    else:
        exit_code = 1

    # Output
    if args.json:
        print(format_json(file_results))
    else:
        output = format_text(file_results, show_types=args.types, quiet=args.quiet)
        if output:
            print(output)

    if exit_code == 1:
        print("No QR codes or barcodes found in any input file.", file=sys.stderr)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
