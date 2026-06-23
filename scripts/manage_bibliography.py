"""Manage the local research bibliography.

The script downloads only entries marked as open in
paper/bibliography/sources.json. Manual entries are rendered into _order.txt.
Downloaded PDFs are local research material and remain ignored by Git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BIBLIOGRAPHY_DIR = ROOT / "paper" / "bibliography"
SOURCES_PATH = BIBLIOGRAPHY_DIR / "sources.json"
PDF_DIR = BIBLIOGRAPHY_DIR / "pdfs"
CATALOG_PATH = BIBLIOGRAPHY_DIR / "CATALOG.md"
ORDER_PATH = BIBLIOGRAPHY_DIR / "_order.txt"
PDF_INDEX_PATH = BIBLIOGRAPHY_DIR / "PDF_INDEX.json"

THREAD_TITLES = {
    "ai-and-robo-advice": "AI and Robo Advice",
    "baselines-and-overfitting": "Baselines and Overfitting",
    "financial-ai-systems": "Financial AI Systems",
    "market-simulation-and-audit": "Market Simulation and Audit",
    "quality-and-profitability": "Quality and Profitability",
    "transaction-costs": "Transaction Costs",
}


@dataclass(frozen=True)
class Paper:
    bib_key: str
    title: str
    authors: str
    year: int
    publication: str
    role: str
    thread: str
    filename: str
    status: str
    source_url: str
    notes: str
    pdf_url: str | None = None

    @property
    def pdf_path(self) -> Path:
        return PDF_DIR / self.filename

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> Paper:
        return cls(
            bib_key=str(payload["bib_key"]),
            title=str(payload["title"]),
            authors=str(payload["authors"]),
            year=int(payload["year"]),
            publication=str(payload["publication"]),
            role=str(payload["role"]),
            thread=str(payload["thread"]),
            filename=str(payload["filename"]),
            status=str(payload["status"]),
            source_url=str(payload["source_url"]),
            notes=str(payload.get("notes", "")),
            pdf_url=payload.get("pdf_url"),
        )


def load_papers(path: Path = SOURCES_PATH) -> list[Paper]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    papers = [Paper.from_json(item) for item in payload["papers"]]
    validate_unique(papers)
    return sorted(papers, key=lambda paper: (paper.thread, paper.year, paper.bib_key))


def validate_unique(papers: list[Paper]) -> None:
    seen_keys: set[str] = set()
    seen_filenames: set[str] = set()
    duplicate_keys: set[str] = set()
    duplicate_filenames: set[str] = set()
    for paper in papers:
        if paper.bib_key in seen_keys:
            duplicate_keys.add(paper.bib_key)
        seen_keys.add(paper.bib_key)
        if paper.filename in seen_filenames:
            duplicate_filenames.add(paper.filename)
        seen_filenames.add(paper.filename)
    if duplicate_keys or duplicate_filenames:
        raise ValueError(
            "Duplicate bibliography identifiers: "
            f"keys={sorted(duplicate_keys)}, filenames={sorted(duplicate_filenames)}"
        )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def looks_like_pdf(path: Path) -> bool:
    with path.open("rb") as handle:
        return handle.read(5) == b"%PDF-"


def download_pdf(paper: Paper, overwrite: bool) -> str:
    if paper.status != "open":
        return "manual"
    if not paper.pdf_url:
        return "missing-url"
    if paper.pdf_path.exists() and not overwrite:
        return "exists"

    request = urllib.request.Request(
        paper.pdf_url,
        headers={"User-Agent": "ArenaWealth bibliography manager (research use)"},
    )
    temporary_path = paper.pdf_path.with_suffix(".tmp")
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            temporary_path.write_bytes(response.read())
    except urllib.error.URLError as error:
        if temporary_path.exists():
            temporary_path.unlink()
        return f"download-error:{error.reason}"

    if not looks_like_pdf(temporary_path):
        temporary_path.unlink()
        return "not-pdf"

    temporary_path.replace(paper.pdf_path)
    return "downloaded"


def download_open_pdfs(papers: list[Paper], overwrite: bool) -> dict[str, str]:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    return {paper.bib_key: download_pdf(paper, overwrite) for paper in papers}


def local_pdf_index(papers: list[Paper]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for paper in papers:
        if not paper.pdf_path.exists():
            continue
        entries.append(
            {
                "bib_key": paper.bib_key,
                "filename": paper.filename,
                "bytes": paper.pdf_path.stat().st_size,
                "sha256": sha256(paper.pdf_path),
                "source_url": paper.source_url,
                "pdf_url": paper.pdf_url,
            }
        )
    return {
        "description": (
            "Local PDF index. PDFs are not part of the public artifact; "
            "this file records what was available in the local research library."
        ),
        "pdf_count": len(entries),
        "entries": entries,
    }


def write_pdf_index(papers: list[Paper]) -> None:
    PDF_INDEX_PATH.write_text(
        json.dumps(local_pdf_index(papers), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def status_for(paper: Paper) -> str:
    if paper.pdf_path.exists():
        return "have"
    if paper.status == "open":
        return "open-missing"
    return "manual"


def write_order(papers: list[Paper], download_results: dict[str, str]) -> None:
    lines = [
        "# Papers to download manually or retry",
        "#",
        "# Drop each PDF into paper/bibliography/pdfs/ using the bracketed filename.",
        "# Do not bypass paywalls; use open, author-hosted, institutional, or licensed copies.",
        "",
    ]
    for paper in papers:
        local_status = status_for(paper)
        result = download_results.get(paper.bib_key, "")
        should_list = local_status != "have" or result.startswith("download-error")
        if not should_list:
            continue
        lines.extend(
            [
                f"[{paper.filename}]",
                f"{paper.authors} ({paper.year}). \"{paper.title}.\"",
                f"Publication/source: {paper.publication}",
                f"Role: {paper.role}",
                f"URL: {paper.source_url}",
                f"PDF URL: {paper.pdf_url or 'manual'}",
                f"Status: {local_status}; last download result: {result or 'not attempted'}",
                f"Notes: {paper.notes}",
                "",
            ]
        )
    ORDER_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_catalog(papers: list[Paper]) -> None:
    by_thread: dict[str, list[Paper]] = {}
    for paper in papers:
        by_thread.setdefault(paper.thread, []).append(paper)

    lines = [
        "# Bibliography Catalog",
        "",
        "This catalog is generated from `paper/bibliography/sources.json`.",
        "`paper/references.bib` remains the BibTeX source used by the manuscript.",
        "PDFs are local research material under `paper/bibliography/pdfs/` and are",
        "ignored by Git; `_order.txt` lists missing or manually downloadable papers.",
        "",
        "## Status legend",
        "",
        "- `have` - local PDF exists.",
        "- `open-missing` - marked open, but the PDF is not present locally.",
        "- `manual` - requires manual, licensed, or author-copy download.",
        "",
    ]

    for thread, thread_papers in sorted(by_thread.items()):
        lines.extend(
            [
                f"## {THREAD_TITLES.get(thread, thread.replace('-', ' ').title())}",
                "",
                "| BibKey | Work | Year | Publication | Role | Status |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for paper in thread_papers:
            lines.append(
                "| "
                f"`{paper.bib_key}` | {paper.title} | {paper.year} | "
                f"{paper.publication} | {paper.role} | {status_for(paper)} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Reproducibility note",
            "",
            "The paper and artifact do not require these PDFs to run. The bibliography",
            "library is a research aid for reading, related-work synthesis, and citation",
            "auditing. Run `make bibliography` to refresh local downloads, the catalog,",
            "`PDF_INDEX.json`, and `_order.txt`.",
            "",
        ]
    )
    CATALOG_PATH.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    papers = load_papers()
    if args.no_download:
        download_results = {paper.bib_key: "not-attempted" for paper in papers}
    else:
        download_results = download_open_pdfs(papers, overwrite=args.overwrite)
    write_catalog(papers)
    write_order(papers, download_results)
    write_pdf_index(papers)

    summary = {
        "papers": len(papers),
        "local_pdfs": local_pdf_index(papers)["pdf_count"],
        "manual_or_missing": sum(1 for paper in papers if status_for(paper) != "have"),
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
