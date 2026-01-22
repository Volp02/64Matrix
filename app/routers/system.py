from fastapi import APIRouter, Response, HTTPException
from app.core.state_manager import StateManager
from app.models.schemas import SystemSettings
from app.core.engine import Engine
import logging
import os
import io

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/system", tags=["System"])

# Dependency injection for StateManager is a bit tricky in FastAPI without a global dependency override or singletons.
# Since we created state_manager in main.py, we can pass it to the router or use a singleton pattern.
# For simplicity in this scale, we will rely on a singleton-ish access or dependency injection from main. 
# A cleaner way is to use `app.state` or a dependency function.
# Let's assume we'll inject it via a dependency or access it from app state.

# For now, let's use a standard pattern:
# We will require the state_manager to be available. 
# We'll attach it to the app instance in main.py and access it via Request.

from fastapi import Request

@router.get("/status", response_model=SystemSettings)
def get_status(request: Request):
    state_manager: StateManager = request.app.state.state_manager
    settings = state_manager.get_settings()
    lib_mgr = getattr(request.app.state, "library_manager", None)
    
    # Enrich with active scene info
    current_scene = state_manager.get_active_scene()
    active_scene_name = "None"
    active_playlist_id = None
    active_scene_filename = None
    
    if current_scene:
        # Check if it's a PlaylistScene
        # To avoid circular imports, checking class name string or attribute
        if current_scene.__class__.__name__ == "PlaylistScene":
             active_playlist_id = getattr(current_scene, "playlist_data", {}).get("name", "Unknown Playlist")
             
             # Get sub-scene info if possible
             sub_scene = current_scene.current_scene_instance
             if sub_scene:
                 # Prefer filename/title for UI, fall back to class name
                 active_scene_filename = getattr(sub_scene, "filename", None)
                 if lib_mgr and active_scene_filename:
                     meta = lib_mgr.get_metadata(active_scene_filename) or {}
                     active_scene_name = meta.get(
                         "title",
                         os.path.splitext(active_scene_filename)[0].replace("_", " ").title(),
                     )
                 else:
                     active_scene_name = active_scene_filename or sub_scene.__class__.__name__
             else:
                 active_scene_name = "Loading..."
        else:
             active_scene_filename = getattr(current_scene, "filename", None)
             if lib_mgr and active_scene_filename:
                 meta = lib_mgr.get_metadata(active_scene_filename) or {}
                 active_scene_name = meta.get(
                     "title",
                     os.path.splitext(active_scene_filename)[0].replace("_", " ").title(),
                 )
             else:
                 active_scene_name = active_scene_filename or current_scene.__class__.__name__

    # Get selected palette info
    selected_palette_id = settings.get("selected_palette", "aurora")
    palette_mgr = getattr(request.app.state, "palette_manager", None)
    selected_palette = None
    if palette_mgr:
        selected_palette = palette_mgr.get_palette(selected_palette_id)
    
    # Add to response (requires schema update first!)
    # We return a dict that matches Schema 
    return {
        "brightness": settings.get("brightness", 100),
        "speed": settings.get("speed", 1.0),
        "active_scene": active_scene_name,
        "active_playlist": active_playlist_id,
        "active_scene_filename": active_scene_filename,
        "selected_palette": selected_palette_id,
        "selected_palette_data": selected_palette
    }

@router.post("/settings")
def update_settings(request: Request, settings: SystemSettings):
    state_manager: StateManager = request.app.state.state_manager
    matrix = request.app.state.matrix_driver
    
    # Brightness
    state_manager.update_setting("brightness", settings.brightness)
    # Apply brightness to hardware
    if matrix:
        try:
            matrix.set_brightness(settings.brightness)
        except Exception as e:
            logger.error(f"Failed to apply brightness: {e}")
    
    # Speed
    state_manager.update_setting("speed", settings.speed)
    
    # Selected Palette (if provided)
    if hasattr(settings, 'selected_palette') and settings.selected_palette:
        state_manager.update_setting("selected_palette", settings.selected_palette)
    
    return {"status": "ok", "settings": settings}

@router.get("/preview")
def get_preview(request: Request):
    """
    Get the latest preview frame as a PNG image.
    Returns a PNG image that can be displayed in the browser.
    """
    try:
        engine: Engine = request.app.state.engine
        preview_frame = engine.get_preview_frame()
        
        if preview_frame is None:
            # Return a placeholder/blank image if no frame available yet
            from PIL import Image
            blank_img = Image.new('RGB', (64, 64), color='black')
            buffer = io.BytesIO()
            blank_img.resize((256, 256), Image.Resampling.NEAREST).save(buffer, format='PNG')
            preview_frame = buffer.getvalue()
        
        return Response(content=preview_frame, media_type="image/png")
    except Exception as e:
        logger.error(f"Error serving preview frame: {e}")
        # Return a small error image
        from PIL import Image
        import io
        error_img = Image.new('RGB', (64, 64), color='red')
        buffer = io.BytesIO()
        error_img.resize((256, 256), Image.Resampling.NEAREST).save(buffer, format='PNG')
        return Response(content=buffer.getvalue(), media_type="image/png")
