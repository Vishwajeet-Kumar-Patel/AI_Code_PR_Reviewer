"""
Plugin system for extensible code analysis
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from pathlib import Path
import importlib
import inspect
from app.core.logging import logger


class AnalyzerPlugin(ABC):
    """Base class for analyzer plugins"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.enabled = True
    
    @abstractmethod
    async def analyze(self, code: str, language: str, context: Dict) -> Dict:
        """
        Analyze code and return findings
        
        Args:
            code: Source code to analyze
            language: Programming language
            context: Additional context (file_path, repo_info, etc.)
        
        Returns:
            Dict with findings: {
                "issues": [...],
                "suggestions": [...],
                "metrics": {...}
            }
        """
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Return list of supported languages"""
        pass
    
    def get_info(self) -> Dict:
        """Get plugin information"""
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "supported_languages": self.get_supported_languages()
        }


class StyleCheckerPlugin(AnalyzerPlugin):
    """Plugin for code style checking"""
    
    async def analyze(self, code: str, language: str, context: Dict) -> Dict:
        """Check code style"""
        issues = []
        
        # Example: Check line length
        for i, line in enumerate(code.split("\n"), 1):
            if len(line) > 120:
                issues.append({
                    "line": i,
                    "type": "style",
                    "severity": "low",
                    "message": f"Line too long ({len(line)} characters)"
                })
        
        # Check naming conventions
        if language == "python":
            import re
            # Check for snake_case function names
            func_pattern = r"def ([A-Z][a-zA-Z0-9]*)\("
            for match in re.finditer(func_pattern, code):
                issues.append({
                    "type": "naming",
                    "severity": "medium",
                    "message": f"Function '{match.group(1)}' should use snake_case"
                })
        
        return {
            "issues": issues,
            "metrics": {
                "total_lines": len(code.split("\n")),
                "style_violations": len(issues)
            }
        }
    
    def get_supported_languages(self) -> List[str]:
        return ["python", "javascript", "typescript", "java", "go"]


class DocumentationPlugin(AnalyzerPlugin):
    """Plugin for documentation analysis"""
    
    async def analyze(self, code: str, language: str, context: Dict) -> Dict:
        """Check documentation coverage"""
        issues = []
        suggestions = []
        
        if language == "python":
            # Check for docstrings
            import ast
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            issues.append({
                                "line": node.lineno,
                                "type": "documentation",
                                "severity": "medium",
                                "message": f"{node.__class__.__name__} '{node.name}' missing docstring"
                            })
            except SyntaxError:
                pass
        
        return {
            "issues": issues,
            "suggestions": suggestions,
            "metrics": {
                "documentation_coverage": max(0, 100 - len(issues) * 10)
            }
        }
    
    def get_supported_languages(self) -> List[str]:
        return ["python", "javascript", "typescript", "java"]


class PerformancePlugin(AnalyzerPlugin):
    """Plugin for performance analysis"""
    
    async def analyze(self, code: str, language: str, context: Dict) -> Dict:
        """Analyze performance issues"""
        issues = []
        
        if language == "python":
            # Check for common performance anti-patterns
            if "for" in code and "append" in code:
                # Suggest list comprehension
                issues.append({
                    "type": "performance",
                    "severity": "low",
                    "message": "Consider using list comprehension for better performance"
                })
            
            if code.count("time.sleep") > 0:
                issues.append({
                    "type": "performance",
                    "severity": "high",
                    "message": "Synchronous sleep detected - consider async/await"
                })
        
        return {
            "issues": issues,
            "metrics": {
                "performance_score": max(0, 100 - len(issues) * 15)
            }
        }
    
    def get_supported_languages(self) -> List[str]:
        return ["python", "javascript", "java", "go"]


class PluginManager:
    """Manage analyzer plugins"""
    
    def __init__(self):
        self.plugins: Dict[str, AnalyzerPlugin] = {}
        self._load_builtin_plugins()
    
    def _load_builtin_plugins(self):
        """Load built-in plugins"""
        builtin_plugins = [
            StyleCheckerPlugin(),
            DocumentationPlugin(),
            PerformancePlugin()
        ]
        
        for plugin in builtin_plugins:
            self.register_plugin(plugin)
            logger.info(f"Loaded built-in plugin: {plugin.name}")
    
    def register_plugin(self, plugin: AnalyzerPlugin):
        """Register a plugin"""
        if not isinstance(plugin, AnalyzerPlugin):
            raise TypeError("Plugin must inherit from AnalyzerPlugin")
        
        self.plugins[plugin.name] = plugin
        logger.info(f"Registered plugin: {plugin.name}")
    
    def unregister_plugin(self, plugin_name: str):
        """Unregister a plugin"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            logger.info(f"Unregistered plugin: {plugin_name}")
    
    def get_plugin(self, plugin_name: str) -> Optional[AnalyzerPlugin]:
        """Get a specific plugin"""
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[Dict]:
        """List all registered plugins"""
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def get_plugins_for_language(self, language: str) -> List[AnalyzerPlugin]:
        """Get all plugins that support a language"""
        return [
            plugin for plugin in self.plugins.values()
            if language in plugin.get_supported_languages() and plugin.enabled
        ]
    
    async def run_analysis(self, code: str, language: str, context: Dict) -> Dict:
        """Run all applicable plugins"""
        applicable_plugins = self.get_plugins_for_language(language)
        
        all_issues = []
        all_suggestions = []
        all_metrics = {}
        
        for plugin in applicable_plugins:
            try:
                result = await plugin.analyze(code, language, context)
                
                # Aggregate results
                all_issues.extend(result.get("issues", []))
                all_suggestions.extend(result.get("suggestions", []))
                all_metrics[plugin.name] = result.get("metrics", {})
                
            except Exception as e:
                logger.error(f"Plugin {plugin.name} failed: {e}", exc_info=True)
        
        return {
            "issues": all_issues,
            "suggestions": all_suggestions,
            "metrics": all_metrics,
            "plugins_run": [p.name for p in applicable_plugins]
        }
    
    def load_external_plugin(self, plugin_path: str):
        """Load external plugin from path"""
        try:
            spec = importlib.util.spec_from_file_location("external_plugin", plugin_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find AnalyzerPlugin subclasses
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, AnalyzerPlugin) and 
                    obj is not AnalyzerPlugin):
                    plugin = obj()
                    self.register_plugin(plugin)
                    logger.info(f"Loaded external plugin: {plugin.name}")
                    
        except Exception as e:
            logger.error(f"Failed to load external plugin: {e}", exc_info=True)


# Global plugin manager
plugin_manager = PluginManager()
