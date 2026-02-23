#!/usr/bin/env python3
import csv
import re
import shutil
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "extracted_images"
TMP_DIR = ROOT / ".tmp_image_extract"
MIN_IMAGE_AREA = 50000

SURVEY_RE = re.compile(r"조사번호\s*([A-Z]{2}\d{3})")
IMG_ROW_RE = re.compile(r"^\s*(\d+)\s+(\d+)\s+image\s+(\d+)\s+(\d+)\s+")
SPLIT_RE = re.compile(r"\s{2,}")


def run(cmd):
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def find_source_image(extract_dir: Path, prefix: str, img_num: int) -> Path | None:
    patterns = [
        f"{prefix}-{img_num:03d}.*",
        f"{prefix}-{img_num:04d}.*",
        f"{prefix}-{img_num}.*",
    ]
    for pat in patterns:
        matches = sorted(extract_dir.glob(pat))
        if matches:
            return matches[0]
    return None


def survey_start_pages(pages: list[str]) -> list[tuple[int, str]]:
    starts = []
    for i, page in enumerate(pages, start=1):
        m = SURVEY_RE.search(page)
        if m:
            starts.append((i, m.group(1)))
    return starts


def survey_for_page(page_no: int, starts: list[tuple[int, str]]) -> tuple[str | None, int | None]:
    last_page = None
    last_code = None
    for p, code in starts:
        if p <= page_no:
            last_page = p
            last_code = code
        else:
            break
    if last_page is None:
        return None, None
    delta = page_no - last_page
    if delta > 2:
        return None, None
    return last_code, delta


def clean_title(line: str) -> str:
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    return line


def is_bad_title(line: str) -> bool:
    bad = [
        "지질유산 분포지도 구축",
        "지질유산 현장 조사표",
        "조사번호",
        "지질유산명",
        "유형 분류",
        "문 헌 명",
        "문헌명",
        "참고자료",
        "기존자료",
        "페이지",
        "소속 및 연락처",
    ]
    if not line:
        return True
    if re.match(r"^-\s*\d+\s*-$", line):
        return True
    if re.match(r"^\d+\s*그룹", line):
        return True
    for b in bad:
        if b in line:
            return True
    return False


def extract_titles(page_text: str) -> list[str]:
    lines = [clean_title(x) for x in page_text.splitlines() if x.strip()]
    out = []
    for ln in lines:
        if is_bad_title(ln):
            continue
        parts = SPLIT_RE.split(ln)
        parts = [clean_title(p) for p in parts if p.strip()]
        if not parts:
            continue
        for p in parts:
            if is_bad_title(p):
                continue
            if len(p) < 4 or len(p) > 80:
                continue
            if not re.search(r"[가-힣A-Za-z]", p):
                continue
            if (
                "분포지도" in p
                or "사진" in p
                or "전경" in p
                or "산출" in p
                or "위치" in p
                or "단면도" in p
                or "동굴" in p
            ):
                out.append(p)
    dedup = []
    seen = set()
    for x in out:
        if x not in seen:
            dedup.append(x)
            seen.add(x)
    return dedup


def main():
    pdf_files = sorted(ROOT.glob("*.pdf"))
    if not pdf_files:
        raise SystemExit("No PDF files found.")

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    seq_by_code = defaultdict(int)

    for pdf in pdf_files:
        base = pdf.stem
        txt_path = TMP_DIR / f"{base}.txt"
        run(["pdftotext", "-layout", str(pdf), str(txt_path)])
        pages = txt_path.read_text(errors="ignore").split("\f")
        starts = survey_start_pages(pages)
        if not starts:
            continue

        list_out = run(["pdfimages", "-list", str(pdf)]).stdout.splitlines()
        extract_dir = TMP_DIR / f"imgs_{base}"
        extract_dir.mkdir(parents=True, exist_ok=True)
        run(["pdfimages", "-all", str(pdf), str(extract_dir / base)])

        page_titles = {}
        for pno in range(1, len(pages) + 1):
            code, delta = survey_for_page(pno, starts)
            if not code or delta is None or delta == 0:
                continue
            page_titles[pno] = extract_titles(pages[pno - 1])

        page_img_idx = defaultdict(int)
        for row in list_out:
            m = IMG_ROW_RE.match(row)
            if not m:
                continue
            page_no = int(m.group(1))
            img_num = int(m.group(2))
            width = int(m.group(3))
            height = int(m.group(4))
            area = width * height
            if area < MIN_IMAGE_AREA:
                continue
            if width <= 260 and height <= 70:
                continue

            code, delta = survey_for_page(page_no, starts)
            if not code:
                continue
            if delta not in (1, 2):
                continue

            src = find_source_image(extract_dir, base, img_num)
            if src is None:
                continue

            page_img_idx[page_no] += 1
            idx_in_page = page_img_idx[page_no] - 1
            titles = page_titles.get(page_no, [])
            title = titles[idx_in_page] if idx_in_page < len(titles) else ""

            seq_by_code[code] += 1
            ext = src.suffix.lower() or ".jpg"
            out_name = f"{code}_{seq_by_code[code]:03d}{ext}"
            code_dir = OUT_DIR / code
            code_dir.mkdir(parents=True, exist_ok=True)
            out_path = code_dir / out_name
            shutil.copy2(src, out_path)

            manifest_rows.append(
                {
                    "survey_no": code,
                    "pdf_file": pdf.name,
                    "page": page_no,
                    "image_num": img_num,
                    "output_file": str(out_path.relative_to(ROOT)),
                    "title": title,
                    "width": width,
                    "height": height,
                }
            )

    manifest_rows.sort(key=lambda r: (r["survey_no"], int(r["page"]), int(r["image_num"])))
    manifest = OUT_DIR / "manifest.csv"
    with manifest.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "survey_no",
                "pdf_file",
                "page",
                "image_num",
                "output_file",
                "title",
                "width",
                "height",
            ],
        )
        w.writeheader()
        w.writerows(manifest_rows)

    summary = OUT_DIR / "README.txt"
    by_code = defaultdict(int)
    titled = 0
    for r in manifest_rows:
        by_code[r["survey_no"]] += 1
        if r["title"]:
            titled += 1
    with summary.open("w", encoding="utf-8") as f:
        f.write("PDF image extraction result\n")
        f.write(f"total_images={len(manifest_rows)}\n")
        f.write(f"surveys={len(by_code)}\n")
        f.write(f"images_with_title={titled}\n")
        f.write("\n")
        for code in sorted(by_code):
            f.write(f"{code}\t{by_code[code]}\n")

    print(f"Extracted images: {len(manifest_rows)}")
    print(f"Survey count: {len(by_code)}")
    print(f"Manifest: {manifest}")


if __name__ == "__main__":
    main()
