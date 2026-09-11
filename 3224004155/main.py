"""Command-line program for comparing the similarity of two text files.

Usage:
    python main.py <original_file> <copy_file> <answer_file>
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path


class PaperCheckError(Exception):
    """Raised when an input or output file cannot be handled safely."""


def read_text(file_path: str | Path) -> str:
    """Read UTF-8 text from an existing regular file."""
    path = Path(file_path)
    if not path.exists():
        raise PaperCheckError(f"输入文件不存在: {path}")
    if not path.is_file():
        raise PaperCheckError(f"输入路径不是文件: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise PaperCheckError(f"输入文件不是 UTF-8 文本: {path}") from error
    except OSError as error:
        raise PaperCheckError(f"无法读取输入文件: {path}") from error


def normalize_text(text: str) -> str:
    """Normalize Unicode and ignore whitespace when comparing articles.

    Whitespace is formatting rather than paper content, so line breaks, tabs,
    and spaces do not affect the resulting similarity. Punctuation remains: it
    can
    still indicate a meaningful edit in short passages.
    """
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return re.sub(r"\s+", "", normalized)


def calculate_similarity(original: str, copied: str) -> float:
    """Return a character-level similarity between 0.0 and 1.0.

    SequenceMatcher finds matching character blocks while tolerating
    insertions, deletions, and replacements. Empty texts are handled explicitly
    so that two empty files are equal and one empty file is unrelated.
    """
    normalized_original = normalize_text(original)
    normalized_copied = normalize_text(copied)
    if not normalized_original and not normalized_copied:
        return 1.0
    if not normalized_original or not normalized_copied:
        return 0.0
    # Article text contains many repeated Chinese characters. Disabling
    # SequenceMatcher's heuristic prevents it from discarding such characters
    # as "popular" and returning an artificially low score on longer papers.
    return SequenceMatcher(
        None, normalized_original, normalized_copied, autojunk=False
    ).ratio()


def write_result(file_path: str | Path, similarity: float) -> None:
    """Write a two-decimal result and create the output parent if needed."""
    path = Path(file_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{similarity:.2f}\n", encoding="utf-8")
    except OSError as error:
        raise PaperCheckError(f"无法写入答案文件: {path}") from error


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    """Parse the three paths required by the grading interface."""
    parser = argparse.ArgumentParser(description="计算两篇论文的重复率")
    parser.add_argument("original_file", help="原文文件的绝对路径")
    parser.add_argument("copied_file", help="抄袭版文件的绝对路径")
    parser.add_argument("answer_file", help="答案文件的绝对路径")
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    """Run the comparison and return a process exit code."""
    args = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    try:
        original = read_text(args.original_file)
        copied = read_text(args.copied_file)
        write_result(args.answer_file, calculate_similarity(original, copied))
    except PaperCheckError as error:
        print(f"错误: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
