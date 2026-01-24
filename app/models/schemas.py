from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SystemSettings(BaseModel):
    brightness: int
    speed: float
    active_scene: Optional[str] = None
    active_playlist: Optional[str] = None
    active_scene_filename: Optional[str] = None
    selected_palette: Optional[str] = None
    selected_palette_data: Optional[Dict[str, Any]] = None
    version: Optional[str] = None
    fps: Optional[float] = None

class SceneItem(BaseModel):
    filename: str
    name: str
    type: str # "script" or "clip"

class SceneList(BaseModel):
    scenes: List[SceneItem]
    active_scene: Optional[str] = None

class SetSceneRequest(BaseModel):
    filename: str

class IntegrationData(BaseModel):
    key: str
    value: Any
