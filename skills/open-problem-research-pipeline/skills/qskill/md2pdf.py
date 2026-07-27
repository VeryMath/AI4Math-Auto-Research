#!/usr/bin/env python3
"""Convert a Markdown report to PDF with pandoc and XeLaTeX."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Union


def build_pdf(
    markdown_path: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    cjk_font: Optional[str] = None,
) -> Optional[Path]:
    """Build one PDF, returning its path or ``None`` when tooling fails."""

    source = Path(markdown_path)
    target_dir = Path(output_dir) if output_dir else source.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = target_dir / f"{source.stem}.pdf"

    missing = [tool for tool in ("pandoc", "xelatex") if shutil.which(tool) is None]
    if missing:
        print(f"PDF generation skipped; missing tool(s): {', '.join(missing)}")
        return None

    command = [
        "pandoc",
        str(source),
        "-o",
        str(pdf_path),
        "--pdf-engine=xelatex",
        "-V",
        "geometry:margin=2.5cm",
    ]
    selected_font = cjk_font or os.environ.get("AI4MATH_CJK_FONT")
    if selected_font:
        command.extend(["-V", f"CJKmainfont={selected_font}"])

    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    if result.returncode != 0 or not pdf_path.is_file():
        print("PDF generation failed:")
        print(result.stderr.strip())
        return None

    print(f"PDF generated: {pdf_path} ({pdf_path.stat().st_size} bytes)")
    return pdf_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown_file")
    parser.add_argument("output_dir", nargs="?")
    parser.add_argument(
        "--cjk-font",
        help="Optional installed CJK font; defaults to AI4MATH_CJK_FONT when set.",
    )
    args = parser.parse_args()
    return 0 if build_pdf(args.markdown_file, args.output_dir, args.cjk_font) else 1


if __name__ == "__main__":
    raise SystemExit(main())
