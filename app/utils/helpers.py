import re
from typing import List, Dict, Any, Optional


def split_code_into_chunks(code: str, max_chunk_size: int = 1000) -> List[str]:
    """Split code into smaller chunks"""
    lines = code.split("\n")
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line)
        if current_size + line_size > max_chunk_size and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_size = 0
        
        current_chunk.append(line)
        current_size += line_size
    
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks


def extract_functions(code: str, language: str) -> List[Dict[str, Any]]:
    """Extract function definitions from code"""
    functions = []
    
    if language == "python":
        pattern = r'def\s+(\w+)\s*\((.*?)\):'
        for match in re.finditer(pattern, code):
            functions.append({
                "name": match.group(1),
                "params": match.group(2),
                "start": match.start(),
            })
    elif language in ["javascript", "typescript"]:
        # Function declarations
        pattern1 = r'function\s+(\w+)\s*\((.*?)\)'
        for match in re.finditer(pattern1, code):
            functions.append({
                "name": match.group(1),
                "params": match.group(2),
                "start": match.start(),
            })
        
        # Arrow functions
        pattern2 = r'const\s+(\w+)\s*=\s*\((.*?)\)\s*=>'
        for match in re.finditer(pattern2, code):
            functions.append({
                "name": match.group(1),
                "params": match.group(2),
                "start": match.start(),
            })
    
    return functions


def extract_imports(code: str, language: str) -> List[str]:
    """Extract import statements from code"""
    imports = []
    
    if language == "python":
        pattern = r'(?:from\s+[\w.]+\s+)?import\s+.+'
        imports = re.findall(pattern, code)
    elif language in ["javascript", "typescript"]:
        pattern = r'import\s+.+\s+from\s+[\'"].+[\'"]'
        imports = re.findall(pattern, code)
    elif language == "java":
        pattern = r'import\s+[\w.]+;'
        imports = re.findall(pattern, code)
    
    return imports


def count_lines_of_code(code: str, ignore_comments: bool = True) -> int:
    """Count lines of code"""
    lines = code.split("\n")
    
    if not ignore_comments:
        return len([line for line in lines if line.strip()])
    
    # Simple comment filtering (not perfect)
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("//"):
            count += 1
    
    return count


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters"""
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    return sanitized


def is_test_file(file_path: str) -> bool:
    """Check if file is a test file"""
    test_patterns = [
        r'test_.*\.py$',
        r'.*_test\.py$',
        r'.*\.test\.(js|ts)$',
        r'.*\.spec\.(js|ts)$',
        r'.*/tests?/.*',
        r'.*/spec/.*',
    ]
    
    for pattern in test_patterns:
        if re.search(pattern, file_path, re.IGNORECASE):
            return True
    return False


def calculate_diff_stats(patch: Optional[str]) -> Dict[str, int]:
    """Calculate statistics from a diff patch"""
    if not patch:
        return {"additions": 0, "deletions": 0, "changes": 0}
    
    additions = 0
    deletions = 0
    
    for line in patch.split("\n"):
        if line.startswith("+") and not line.startswith("+++"):
            additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            deletions += 1
    
    return {
        "additions": additions,
        "deletions": deletions,
        "changes": additions + deletions,
    }
