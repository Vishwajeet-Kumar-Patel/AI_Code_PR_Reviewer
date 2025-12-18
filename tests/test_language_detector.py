"""Tests for language detector"""
import pytest
from app.utils.language_detector import LanguageDetector


def test_detect_python():
    """Test Python file detection"""
    detector = LanguageDetector()
    
    assert detector.detect("script.py") == "python"
    assert detector.detect("/path/to/file.py") == "python"


def test_detect_javascript():
    """Test JavaScript file detection"""
    detector = LanguageDetector()
    
    assert detector.detect("script.js") == "javascript"
    assert detector.detect("component.jsx") == "javascript"


def test_detect_typescript():
    """Test TypeScript file detection"""
    detector = LanguageDetector()
    
    assert detector.detect("app.ts") == "typescript"
    assert detector.detect("component.tsx") == "typescript"


def test_detect_java():
    """Test Java file detection"""
    detector = LanguageDetector()
    
    assert detector.detect("Main.java") == "java"


def test_detect_unsupported():
    """Test unsupported file type"""
    detector = LanguageDetector()
    
    assert detector.detect("document.txt") is None
    assert detector.detect("image.png") is None


def test_is_supported():
    """Test is_supported method"""
    detector = LanguageDetector()
    
    assert detector.is_supported("script.py") is True
    assert detector.is_supported("script.js") is True
    assert detector.is_supported("unknown.xyz") is False


def test_case_insensitive():
    """Test case insensitive detection"""
    detector = LanguageDetector()
    
    assert detector.detect("Script.PY") == "python"
    assert detector.detect("APP.TS") == "typescript"
