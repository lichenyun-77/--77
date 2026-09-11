"""Unit tests for the paper-checking program."""

from pathlib import Path

import pytest

from main import (
    PaperCheckError,
    calculate_similarity,
    main,
    normalize_text,
    read_text,
)


def test_identical_texts_are_equal() -> None:
    assert calculate_similarity("今天是星期天。", "今天是星期天。") == 1.0


def test_completely_different_texts_have_no_overlap() -> None:
    assert calculate_similarity("甲乙丙丁", "春夏秋冬") == 0.0


def test_whitespace_does_not_change_similarity() -> None:
    assert calculate_similarity("今天\n天气晴", "今天  天气\t晴") == 1.0


def test_case_is_ignored_for_latin_text() -> None:
    assert calculate_similarity(
        "Python Programming", "python programming"
    ) == 1.0


def test_full_width_characters_are_normalized() -> None:
    assert normalize_text("ＡＢＣ１２３") == "abc123"


def test_inserted_content_lowers_similarity() -> None:
    score = calculate_similarity("今天我要去看电影", "今天晚上我要和朋友去看电影")
    assert 0.6 < score < 1.0


def test_deleted_content_lowers_similarity() -> None:
    score = calculate_similarity("今天晚上我要去看电影", "今天我要看电影")
    assert 0.6 < score < 1.0


def test_replaced_content_lowers_similarity() -> None:
    score = calculate_similarity("天气晴朗", "天气阴沉")
    assert 0.3 < score < 1.0


def test_two_empty_texts_are_equal() -> None:
    assert calculate_similarity("", "") == 1.0


def test_one_empty_text_has_zero_similarity() -> None:
    assert calculate_similarity("内容", "") == 0.0


def test_missing_input_file_raises_clear_error(tmp_path: Path) -> None:
    with pytest.raises(PaperCheckError, match="不存在"):
        read_text(tmp_path / "missing.txt")


def test_command_line_writes_two_decimal_result(tmp_path: Path) -> None:
    original = tmp_path / "original.txt"
    copied = tmp_path / "copied.txt"
    answer = tmp_path / "nested" / "answer.txt"
    original.write_text("今天是星期天", encoding="utf-8")
    copied.write_text("今天是星期天", encoding="utf-8")

    assert main([str(original), str(copied), str(answer)]) == 0
    assert answer.read_text(encoding="utf-8") == "1.00\n"


def test_command_line_returns_one_for_missing_file(tmp_path: Path) -> None:
    answer = tmp_path / "answer.txt"
    arguments = [
        str(tmp_path / "none.txt"),
        str(tmp_path / "none2.txt"),
        str(answer),
    ]
    assert main(arguments) == 1
