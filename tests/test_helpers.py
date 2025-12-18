"""Tests for helper utilities"""
import pytest
from app.utils.helpers import (
    split_code_into_chunks,
    count_lines_of_code,
    format_file_size,
    truncate_text,
    is_test_file,
    calculate_diff_stats,
)


def test_split_code_into_chunks():
    """Test code splitting"""
    code = "\n".join([f"line {i}" for i in range(100)])
    chunks = split_code_into_chunks(code, max_chunk_size=50)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 100  # Some buffer


def test_count_lines_of_code():
    """Test LOC counting"""
    code = """
def hello():
    # This is a comment
    print("hello")
    
    return True
"""
    loc = count_lines_of_code(code, ignore_comments=True)
    assert loc > 0
    
    loc_with_comments = count_lines_of_code(code, ignore_comments=False)
    assert loc_with_comments >= loc


def test_format_file_size():
    """Test file size formatting"""
    assert format_file_size(100) == "100.0 B"
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1024 * 1024) == "1.0 MB"
    assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"


def test_truncate_text():
    """Test text truncation"""
    text = "This is a very long text that should be truncated"
    truncated = truncate_text(text, max_length=20)
    
    assert len(truncated) <= 23  # 20 + "..."
    assert truncated.endswith("...")


def test_is_test_file():
    """Test test file detection"""
    assert is_test_file("test_something.py") is True
    assert is_test_file("something_test.py") is True
    assert is_test_file("something.test.js") is True
    assert is_test_file("tests/test_file.py") is True
    assert is_test_file("src/main.py") is False


def test_calculate_diff_stats():
    """Test diff statistics calculation"""
    patch = """
--- a/file.py
+++ b/file.py
@@ -1,3 +1,4 @@
 def hello():
-    print("old")
+    print("new")
+    return True
"""
    stats = calculate_diff_stats(patch)
    
    assert stats["additions"] > 0
    assert stats["deletions"] > 0
    assert stats["changes"] == stats["additions"] + stats["deletions"]


def test_calculate_diff_stats_empty():
    """Test diff stats with empty patch"""
    stats = calculate_diff_stats(None)
    
    assert stats["additions"] == 0
    assert stats["deletions"] == 0
    assert stats["changes"] == 0
