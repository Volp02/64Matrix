from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Any
from app.core.scenes.playlist_scene import PlaylistScene

router = APIRouter(
    prefix="/api/playlists",
    tags=["Playlists"]
)

class PlaylistItem(BaseModel):
    type: str = "script" # script, clip
    filename: str
    duration: float = 10.0
    palette: Optional[str] = None  # Optional palette ID for this item (script scenes only)

class PlaylistModel(BaseModel):
    id: str
    name: str
    items: List[PlaylistItem]
    settings: Optional[dict] = {}
    default_palette: Optional[str] = None  # Default palette for the playlist

class CreatePlaylistRequest(BaseModel):
    name: str
    items: List[PlaylistItem]

@router.get("/", response_model=dict)
async def get_playlists(request: Request):
    manager = request.app.state.playlist_manager
    return {"playlists": manager.get_all()}

@router.post("/")
async def save_playlist(request: Request, playlist: PlaylistModel):
    manager = request.app.state.playlist_manager
    # Convert to dict and ensure all fields are present
    playlist_dict = playlist.dict()
    # Ensure settings exists (for backward compatibility)
    if "settings" not in playlist_dict:
        playlist_dict["settings"] = {}
    saved = manager.save_playlist(playlist.id, playlist_dict)
    return {"status": "ok", "playlist": saved}

@router.delete("/{playlist_id}")
async def delete_playlist(request: Request, playlist_id: str):
    manager = request.app.state.playlist_manager
    success = manager.delete_playlist(playlist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return {"status": "ok"}

@router.post("/{playlist_id}/play")
async def play_playlist(request: Request, playlist_id: str):
    manager = request.app.state.playlist_manager
    playlist_data = manager.get_by_id(playlist_id)
    
    if not playlist_data:
        raise HTTPException(status_code=404, detail="Playlist not found")
        
    # Instantiate the PlaylistScene
    # We need access to the matrix and state_manager, which are in app.state?
    # Actually engine has the matrix. state_manager is in app.state.
    
    engine = request.app.state.engine
    state_manager = request.app.state.state_manager
    script_loader = request.app.state.script_loader
    clip_loader = request.app.state.clip_loader
    
    # Create the scene instance
    # Note: Matrix driver is inside engine...? 
    # BaseScene expects 'matrix'. Engine has 'matrix_driver'.
    
    # We need to access the matrix driver instance.
    # In main.py: engine = Engine(matrix_driver, state_manager)
    # The engine probably stores it.
    
    if hasattr(engine, 'matrix'): 
        matrix = engine.matrix
    else:
        # Fallback if engine implementation differs
        matrix = request.app.state.matrix_driver # Assuming we put it there too?
        
    if not matrix:
         raise HTTPException(status_code=500, detail="Matrix driver not found")

    scene = PlaylistScene(matrix, state_manager, playlist_data, script_loader, clip_loader)
    
    # Activate it
    # We use state_manager.set_scene or engine.set_scene?
    # Engine calls state_manager.get_active_scene().
    # So we set it on state_manager.
    
    state_manager.set_scene(scene)
    
    return {"status": "playing", "playlist": playlist_id}
