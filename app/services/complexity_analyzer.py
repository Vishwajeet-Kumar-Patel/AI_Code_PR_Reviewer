import re
import ast
from typing import List, Dict, Any, Optional
from app.core.logging import logger
from app.models.review import ComplexityMetrics, CodeIssue, IssueCategory, Severity
from app.models.code_analysis import CodeSmell, QualityMetrics


class ComplexityAnalyzer:
    """Analyzer for code complexity metrics"""
    
    def __init__(self):
        """Initialize complexity analyzer"""
        self.language_analyzers = {
            "python": self._analyze_python_complexity,
            "javascript": self._analyze_js_complexity,
            "typescript": self._analyze_js_complexity,
            "java": self._analyze_java_complexity,
        }
    
    def analyze(self, code: str, language: str, file_path: str) -> ComplexityMetrics:
        """Analyze code complexity"""
        analyzer = self.language_analyzers.get(language.lower(), self._analyze_generic_complexity)
        
        try:
            return analyzer(code, file_path)
        except Exception as e:
            logger.error(f"Complexity analysis failed for {file_path}: {e}")
            return self._get_default_metrics(code)
    
    def _analyze_python_complexity(self, code: str, file_path: str) -> ComplexityMetrics:
        """Analyze Python code complexity"""
        try:
            tree = ast.parse(code)
            
            cyclomatic = self._calculate_cyclomatic_complexity_python(tree)
            cognitive = self._calculate_cognitive_complexity_python(tree)
            loc = len([line for line in code.split("\n") if line.strip() and not line.strip().startswith("#")])
            maintainability = self._calculate_maintainability_index(cyclomatic, loc)
            
            return ComplexityMetrics(
                cyclomatic_complexity=cyclomatic,
                cognitive_complexity=cognitive,
                lines_of_code=loc,
                maintainability_index=maintainability,
            )
        except SyntaxError as e:
            logger.warning(f"Syntax error in Python file {file_path}: {e}")
            return self._get_default_metrics(code)
    
    def _calculate_cyclomatic_complexity_python(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity for Python"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            # Decision points
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_cognitive_complexity_python(self, tree: ast.AST) -> int:
        """Calculate cognitive complexity for Python"""
        complexity = 0
        nesting_level = 0
        
        def visit_node(node, level):
            nonlocal complexity
            
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1 + level
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1 + level
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
            
            # Increase nesting for control structures
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With, ast.Try)):
                level += 1
            
            for child in ast.iter_child_nodes(node):
                visit_node(child, level)
        
        visit_node(tree, 0)
        return complexity
    
    def _analyze_js_complexity(self, code: str, file_path: str) -> ComplexityMetrics:
        """Analyze JavaScript/TypeScript complexity"""
        # Simplified analysis using regex patterns
        cyclomatic = 1  # Base complexity
        
        # Count decision points
        cyclomatic += len(re.findall(r'\bif\b', code))
        cyclomatic += len(re.findall(r'\belse\s+if\b', code))
        cyclomatic += len(re.findall(r'\bwhile\b', code))
        cyclomatic += len(re.findall(r'\bfor\b', code))
        cyclomatic += len(re.findall(r'\bcase\b', code))
        cyclomatic += len(re.findall(r'\bcatch\b', code))
        cyclomatic += len(re.findall(r'\&\&', code))
        cyclomatic += len(re.findall(r'\|\|', code))
        cyclomatic += len(re.findall(r'\?', code))  # Ternary operators
        
        # Cognitive complexity (simplified)
        cognitive = cyclomatic + self._count_nesting_depth(code) * 2
        
        # Lines of code
        loc = len([line for line in code.split("\n") 
                   if line.strip() and not line.strip().startswith("//") 
                   and not line.strip().startswith("/*")])
        
        maintainability = self._calculate_maintainability_index(cyclomatic, loc)
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            maintainability_index=maintainability,
        )
    
    def _analyze_java_complexity(self, code: str, file_path: str) -> ComplexityMetrics:
        """Analyze Java code complexity"""
        # Similar to JavaScript analysis
        return self._analyze_js_complexity(code, file_path)
    
    def _analyze_generic_complexity(self, code: str, file_path: str) -> ComplexityMetrics:
        """Generic complexity analysis for unsupported languages"""
        lines = code.split("\n")
        loc = len([line for line in lines if line.strip()])
        
        # Simple heuristic
        cyclomatic = max(1, loc // 20)
        cognitive = cyclomatic
        maintainability = max(0, 100 - (loc / 10))
        
        return ComplexityMetrics(
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            lines_of_code=loc,
            maintainability_index=maintainability,
        )
    
    def _count_nesting_depth(self, code: str) -> int:
        """Count maximum nesting depth"""
        max_depth = 0
        current_depth = 0
        
        for char in code:
            if char == '{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == '}':
                current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _calculate_maintainability_index(self, cyclomatic: int, loc: int) -> float:
        """Calculate maintainability index"""
        # Simplified maintainability index calculation
        # Real MI uses Halstead volume and comment percentage
        if loc == 0:
            return 100.0
        
        # Basic formula: 171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)
        # Simplified version
        import math
        
        volume = max(1, loc * 2)  # Simplified volume
        mi = 171 - 5.2 * math.log(volume) - 0.23 * cyclomatic - 16.2 * math.log(loc)
        
        # Normalize to 0-100
        mi = max(0, min(100, mi))
        
        return round(mi, 2)
    
    def _get_default_metrics(self, code: str) -> ComplexityMetrics:
        """Get default metrics when analysis fails"""
        loc = len([line for line in code.split("\n") if line.strip()])
        return ComplexityMetrics(
            cyclomatic_complexity=1,
            cognitive_complexity=1,
            lines_of_code=loc,
            maintainability_index=50.0,
        )
    
    def detect_code_smells(self, code: str, language: str, file_path: str) -> List[CodeSmell]:
        """Detect code smells"""
        smells = []
        lines = code.split("\n")
        
        # Long method
        if len(lines) > 100:
            smells.append(CodeSmell(
                smell_type="long_method",
                description="Method/function is too long (>100 lines)",
                file_path=file_path,
                line_range=(1, len(lines)),
                severity="medium",
                refactoring_suggestion="Break down into smaller, focused functions",
            ))
        
        # Too many parameters (Python)
        if language.lower() == "python":
            for i, line in enumerate(lines, 1):
                if "def " in line:
                    params = re.findall(r'def\s+\w+\((.*?)\)', line)
                    if params and len(params[0].split(",")) > 5:
                        smells.append(CodeSmell(
                            smell_type="too_many_parameters",
                            description="Function has too many parameters (>5)",
                            file_path=file_path,
                            line_range=(i, i),
                            severity="medium",
                            refactoring_suggestion="Consider using a parameter object or reducing parameters",
                        ))
        
        # Deeply nested code
        max_nesting = self._count_nesting_depth(code)
        if max_nesting > 4:
            smells.append(CodeSmell(
                smell_type="deep_nesting",
                description=f"Code has deep nesting ({max_nesting} levels)",
                file_path=file_path,
                line_range=(1, len(lines)),
                severity="high",
                refactoring_suggestion="Extract nested logic into separate functions",
            ))
        
        return smells
