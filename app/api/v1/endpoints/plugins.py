"""
Plugin system API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.plugins.plugin_manager import plugin_manager, AnalyzerPlugin
from app.core.deps import get_current_admin_user
from app.db.models import User
from typing import Dict, List
from pydantic import BaseModel


router = APIRouter(prefix="/plugins", tags=["Plugins"])


class AnalysisRequest(BaseModel):
    code: str
    language: str
    context: Dict = {}


class PluginToggleRequest(BaseModel):
    enabled: bool


@router.get("/")
async def list_plugins():
    """List all registered plugins"""
    return {
        "plugins": plugin_manager.list_plugins(),
        "total": len(plugin_manager.plugins)
    }


@router.get("/{plugin_name}")
async def get_plugin_info(plugin_name: str):
    """Get information about a specific plugin"""
    plugin = plugin_manager.get_plugin(plugin_name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    return plugin.get_info()


@router.post("/{plugin_name}/toggle")
async def toggle_plugin(
    plugin_name: str,
    request: PluginToggleRequest,
    current_user: User = Depends(get_current_admin_user)
):
    """Enable or disable a plugin (admin only)"""
    plugin = plugin_manager.get_plugin(plugin_name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    plugin.enabled = request.enabled
    
    return {
        "message": f"Plugin {plugin_name} {'enabled' if request.enabled else 'disabled'}",
        "plugin": plugin.get_info()
    }


@router.post("/analyze")
async def analyze_with_plugins(request: AnalysisRequest):
    """Run analysis using all applicable plugins"""
    result = await plugin_manager.run_analysis(
        code=request.code,
        language=request.language,
        context=request.context
    )
    
    return result


@router.post("/upload")
async def upload_external_plugin(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user)
):
    """Upload and install external plugin (admin only)"""
    
    if not file.filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only Python files allowed")
    
    # Save plugin file
    plugin_dir = Path("app/plugins/external")
    plugin_dir.mkdir(exist_ok=True)
    
    plugin_path = plugin_dir / file.filename
    
    content = await file.read()
    plugin_path.write_bytes(content)
    
    # Load plugin
    try:
        plugin_manager.load_external_plugin(str(plugin_path))
        return {
            "message": "Plugin uploaded and loaded successfully",
            "file": file.filename
        }
    except Exception as e:
        plugin_path.unlink()  # Delete file if loading failed
        raise HTTPException(status_code=400, detail=f"Failed to load plugin: {str(e)}")


@router.delete("/{plugin_name}")
async def uninstall_plugin(
    plugin_name: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Uninstall a plugin (admin only)"""
    plugin = plugin_manager.get_plugin(plugin_name)
    
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    # Don't allow uninstalling built-in plugins
    builtin_plugins = ["StyleCheckerPlugin", "DocumentationPlugin", "PerformancePlugin"]
    if plugin_name in builtin_plugins:
        raise HTTPException(status_code=400, detail="Cannot uninstall built-in plugins")
    
    plugin_manager.unregister_plugin(plugin_name)
    
    return {"message": f"Plugin {plugin_name} uninstalled successfully"}


from pathlib import Path
