import os
from pathlib import Path
from typing import Optional


class LanguageDetector:
    """Detect programming language from file extension"""
    
    def __init__(self):
        """Initialize language detector"""
        self.extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".kt": "kotlin",
            ".go": "go",
            ".rs": "rust",
            ".c": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".h": "cpp",
            ".hpp": "cpp",
            ".cs": "csharp",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".m": "objectivec",
            ".scala": "scala",
            ".sh": "shell",
            ".bash": "shell",
            ".sql": "sql",
            ".r": "r",
            ".lua": "lua",
            ".pl": "perl",
            ".vim": "vim",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".xml": "xml",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".sass": "sass",
            ".md": "markdown",
            ".rst": "rst",
            ".tex": "latex",
        }
    
    def detect(self, file_path: str) -> Optional[str]:
        """Detect language from file path"""
        ext = Path(file_path).suffix.lower()
        return self.extension_map.get(ext)
    
    def is_supported(self, file_path: str) -> bool:
        """Check if file language is supported"""
        return self.detect(file_path) is not None
    
    def get_supported_extensions(self) -> list:
        """Get list of supported file extensions"""
        return list(self.extension_map.keys())
