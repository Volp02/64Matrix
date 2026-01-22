from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from app.models.schemas import SceneList, SetSceneRequest
from app.core.state_manager import StateManager
from app.core.loaders.script_loader import ScriptLoader
from app.core.loaders.clip_loader import ClipLoader
from app.core.engine import Engine
from app.core.library_manager import LibraryManager
import os
import logging
import threading

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scenes", tags=["Scenes"])

@router.get("/", response_model=SceneList)
def list_scenes(request: Request):
    loader: ScriptLoader = request.app.state.script_loader
    clip_loader: ClipLoader = request.app.state.clip_loader
    state_manager: StateManager = request.app.state.state_manager
    lib_mgr = request.app.state.library_manager
    
    scripts = loader.list_available_scripts()
    clips = clip_loader.list_available_clips()
    
    scene_items = []
    
    for s in scripts:
        meta = lib_mgr.get_metadata(s)
        display_name = meta.get("title", s.replace(".py", "").replace("_", " ").title())
        scene_items.append({
            "filename": s,
            "name": display_name,
            "type": "script"
        })
        
    for c in clips:
        meta = lib_mgr.get_metadata(c)
        # For clips, default clean name is filename without ext
        clean_name = os.path.splitext(c)[0].replace("_", " ").title()
        display_name = meta.get("title", clean_name)
        
        scene_items.append({
            "filename": c,
            "name": display_name,
            "type": "clip"
        })
        
    active = state_manager.get_active_scene()
    active_name = None
    if active:
        # This is a bit hacky, getting the class name or some ID would be better.
        # For now, we don't strictly track the filename in the active_scene object.
        # We might want to fix that in StateManager or BaseScene.
        active_name = active.__class__.__name__

    return {
        "scenes": scene_items,
        "active_scene": active_name
    }

@router.post("/activate")
def activate_scene(request: Request, req: SetSceneRequest):
    try:
        loader: ScriptLoader = request.app.state.script_loader
        clip_loader: ClipLoader = request.app.state.clip_loader
        state_manager: StateManager = request.app.state.state_manager
        
        if not req.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        # Security: Prevent directory traversal
        if ".." in req.filename or "/" in req.filename or "\\" in req.filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        scene_instance = None
        
        # Try to load as script first
        try:
            scene_class = loader.load_script(req.filename)
            if scene_class:
                scene_instance = loader.get_scene(req.filename)
        except Exception as e:
            logger.debug(f"Failed to load as script {req.filename}: {e}")
        
        # If script loading failed, try as clip
        if not scene_instance:
            try:
                scene_instance = clip_loader.load_clip(req.filename)
            except Exception as e:
                logger.debug(f"Failed to load as clip {req.filename}: {e}")
        
        if not scene_instance:
            raise HTTPException(status_code=404, detail=f"Scene '{req.filename}' not found or could not be loaded")
        
        # Set the scene
        try:
            state_manager.set_scene(scene_instance)
            logger.info(f"Activated scene: {req.filename}")
            
            # Schedule automatic thumbnail generation for scripts if no thumbnail exists
            lib_mgr: LibraryManager = request.app.state.library_manager
            engine: Engine = request.app.state.engine
            
            # Check if this is a script (not a clip) and has no thumbnail
            if scene_instance.__class__.__name__ != "GifScene" and not lib_mgr.thumbnail_exists(req.filename):
                logger.info(f"Scheduling thumbnail capture for script {req.filename} in 15 seconds")
                
                def capture_thumbnail():
                    """Capture thumbnail after 15 seconds if scene is still active."""
                    try:
                        # Check if this scene is still active
                        current_scene = state_manager.get_active_scene()
                        if current_scene and hasattr(current_scene, 'filename') and current_scene.filename == req.filename:
                            # Get preview frame from engine
                            preview_frame = engine.get_preview_frame()
                            if preview_frame:
                                # Convert PNG bytes to PIL Image
                                from PIL import Image
                                import io
                                img = Image.open(io.BytesIO(preview_frame))
                                
                                # Preview frames are scaled 4x (256x256), scale down to original 64x64
                                if img.size == (256, 256):
                                    # Scale down to 64x64 (original matrix size)
                                    img = img.resize((64, 64), Image.Resampling.NEAREST)
                                elif img.size != (64, 64):
                                    # If unexpected size, resize to 64x64
                                    img = img.resize((64, 64), Image.Resampling.LANCZOS)
                                
                                # Save thumbnail (LibraryManager will resize to 128x128 for thumbnail)
                                if lib_mgr.save_thumbnail(req.filename, img):
                                    logger.info(f"Auto-generated thumbnail for script {req.filename}")
                                else:
                                    logger.warning(f"Failed to save auto-generated thumbnail for {req.filename}")
                            else:
                                logger.debug(f"No preview frame available for thumbnail capture of {req.filename}")
                        else:
                            logger.debug(f"Scene {req.filename} is no longer active, skipping thumbnail capture")
                    except Exception as e:
                        logger.error(f"Error during automatic thumbnail capture for {req.filename}: {e}")
                
                # Schedule thumbnail capture after 15 seconds
                timer = threading.Timer(15.0, capture_thumbnail)
                timer.daemon = True  # Don't prevent shutdown
                timer.start()
            
        except Exception as e:
            logger.error(f"Failed to activate scene {req.filename}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to activate scene: {str(e)}")
        
        return {"status": "ok", "active_scene": req.filename}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error activating scene: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.delete("/{filename}")
def delete_scene(filename: str, request: Request):
    # Determine if script or clip
    # For simplicity, search in both dirs?
    # Or frontend sends type? Let's search.
    
    script_path = os.path.join("scenes", "scripts", filename)
    clip_path_dir = os.path.join("scenes", "clips", filename) # For folders?
    clip_path_file = os.path.join("scenes", "clips", filename) # For direct files
    
    target = None
    if os.path.exists(script_path):
        target = script_path
    elif os.path.exists(clip_path_file):
        target = clip_path_file
        
    if not target:
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        os.remove(target)
        
        # Cleanup thumbnail
        thumb_path = os.path.join("scenes", "thumbnails", f"{filename}.png")
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
            
        # Cleanup metadata
        request.app.state.library_manager.delete_entry(filename)
        
        return {"status": "deleted", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{filename}")
def rename_scene(filename: str, request: Request, payload: dict):
    new_name = payload.get("new_name")
    if not new_name:
        raise HTTPException(status_code=400, detail="new_name required")
        
    # Security: prevent directory traversal
    if ".." in new_name or "/" in new_name or "\\" in new_name:
         raise HTTPException(status_code=400, detail="Invalid filename")

    # Preserve extension logic
    _, ext = os.path.splitext(filename)
    if not new_name.endswith(ext):
        new_name += ext

    script_path = os.path.join("scenes", "scripts", filename)
    clip_path = os.path.join("scenes", "clips", filename)
    
    src = None
    dest_dir = None
    if os.path.exists(script_path):
        src = script_path
        dest_dir = os.path.join("scenes", "scripts")
    elif os.path.exists(clip_path):
        src = clip_path
        dest_dir = os.path.join("scenes", "clips")
    
    if not src:
         raise HTTPException(status_code=404, detail="File not found")
         
    dest = os.path.join(dest_dir, new_name)
    if os.path.exists(dest):
        raise HTTPException(status_code=409, detail="Destination already exists")
        
    try:
        # 1. Rename File
        os.rename(src, dest)
        
        # 2. Rename Thumbnail if exists
        # Convention: thumbnails/{filename}.png
        thumb_src = os.path.join("scenes", "thumbnails", f"{filename}.png")
        thumb_dest = os.path.join("scenes", "thumbnails", f"{new_name}.png")
        if os.path.exists(thumb_src):
            if os.path.exists(thumb_dest):
                os.remove(thumb_dest) # Overwrite logic? Or error?
            os.rename(thumb_src, thumb_dest)
            
        # 3. Update Library Metadata
        lib_mgr = request.app.state.library_manager
        lib_mgr.rename_entry(filename, new_name)
        
        # Also, update the "Display Title" to match new name (without ext) for consistency?
        # Or keep old title? User intent: "Rename". Usually implies changing display name too.
        clean_title = os.path.splitext(new_name)[0].replace("_", " ").title()
        lib_mgr.update_metadata(new_name, title=clean_title)

        return {"status": "renamed", "old_name": filename, "new_name": new_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{filename}/thumbnail")
def upload_thumbnail(filename: str, request: Request, file: UploadFile = File(...)):
    # Validate extension
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
         raise HTTPException(status_code=400, detail="Invalid image type")

    thumb_dir = os.path.join("scenes", "thumbnails")
    if not os.path.exists(thumb_dir):
        os.makedirs(thumb_dir)
        
    target_path = os.path.join(thumb_dir, f"{filename}.png")
    
    try:
        with open(target_path, "wb") as f:
            f.write(file.file.read())
        return {"status": "uploaded", "thumbnail": f"{filename}.png"}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import FileResponse

@router.get("/thumbnails/{filename}")
def get_thumbnail(filename: str):
    thumb_path = os.path.join("scenes", "thumbnails", f"{filename}.png")
    if os.path.exists(thumb_path):
        return FileResponse(thumb_path)
    raise HTTPException(status_code=404, detail="Thumbnail not found")
