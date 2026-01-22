from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(
    prefix="/api/palettes",
    tags=["Palettes"]
)

class PaletteModel(BaseModel):
    id: str
    name: str
    colors: List[str]

class CreatePaletteRequest(BaseModel):
    name: str
    colors: List[str]

@router.get("/")
async def get_palettes(request: Request):
    """Get all palettes (default and custom)."""
    manager = request.app.state.palette_manager
    return {
        "default": manager.get_default_palettes(),
        "custom": manager.get_custom_palettes()
    }

@router.get("/{palette_id}")
async def get_palette(request: Request, palette_id: str):
    """Get a specific palette by ID."""
    manager = request.app.state.palette_manager
    palette = manager.get_palette(palette_id)
    if not palette:
        raise HTTPException(status_code=404, detail="Palette not found")
    return palette

@router.post("/")
async def create_palette(request: Request, palette: CreatePaletteRequest):
    """Create a new custom palette."""
    manager = request.app.state.palette_manager
    
    # Generate ID from name (sanitize)
    palette_id = palette.name.lower().replace(" ", "_").replace("-", "_")
    # Remove special characters
    palette_id = "".join(c for c in palette_id if c.isalnum() or c == "_")
    
    # Ensure unique ID
    original_id = palette_id
    counter = 1
    while palette_id in manager.get_custom_palettes() or palette_id in manager.get_default_palettes():
        palette_id = f"{original_id}_{counter}"
        counter += 1
    
    data = {
        "id": palette_id,
        "name": palette.name,
        "colors": palette.colors
    }
    
    try:
        saved = manager.save_palette(palette_id, data)
        return {"status": "ok", "palette": saved}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create palette: {str(e)}")

@router.put("/{palette_id}")
async def update_palette(request: Request, palette_id: str, palette: PaletteModel):
    """Update an existing custom palette."""
    manager = request.app.state.palette_manager
    
    # Cannot update default palettes
    if palette_id in manager.get_default_palettes():
        raise HTTPException(status_code=403, detail="Cannot modify default palettes")
    
    if palette_id not in manager.get_custom_palettes():
        raise HTTPException(status_code=404, detail="Palette not found")
    
    # Ensure ID matches
    palette.id = palette_id
    
    try:
        saved = manager.save_palette(palette_id, palette.dict())
        return {"status": "ok", "palette": saved}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update palette: {str(e)}")

@router.delete("/{palette_id}")
async def delete_palette(request: Request, palette_id: str):
    """Delete a custom palette."""
    manager = request.app.state.palette_manager
    
    try:
        success = manager.delete_palette(palette_id)
        if not success:
            raise HTTPException(status_code=404, detail="Palette not found")
        return {"status": "ok"}
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/{palette_id}/select")
async def select_palette(request: Request, palette_id: str):
    """Select a palette as the active palette for scripts."""
    from app.core.state_manager import StateManager
    
    manager = request.app.state.palette_manager
    state_manager: StateManager = request.app.state.state_manager
    
    # Verify palette exists
    palette = manager.get_palette(palette_id)
    if not palette:
        raise HTTPException(status_code=404, detail="Palette not found")
    
    # Update selected palette setting
    state_manager.update_setting("selected_palette", palette_id)
    
    return {"status": "ok", "selected_palette": palette_id, "palette": palette}
