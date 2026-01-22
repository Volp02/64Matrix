from fastapi import APIRouter, Request, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["Settings"])


class HomeAssistantSettings(BaseModel):
    enabled: bool
    url: str
    long_lived_token: str


class AppSettings(BaseModel):
    home_assistant: HomeAssistantSettings


@router.get("/")
def get_settings(request: Request):
    """Get all application settings"""
    settings_manager = request.app.state.app_settings_manager
    return {"settings": settings_manager.get_settings()}


@router.get("/{category}")
def get_category_settings(request: Request, category: str):
    """Get settings for a specific category"""
    settings_manager = request.app.state.app_settings_manager
    category_settings = settings_manager.get_setting(category)
    
    if category_settings is None:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    
    return {"category": category, "settings": category_settings}


@router.put("/{category}")
def update_category_settings(request: Request, category: str, settings: dict):
    """Update settings for a specific category"""
    settings_manager = request.app.state.app_settings_manager
    
    if not settings_manager.update_category(category, settings):
        raise HTTPException(status_code=500, detail="Failed to update settings")
    
    return {"message": "Settings updated successfully", "category": category, "settings": settings_manager.get_setting(category)}


@router.put("/{category}/{key}")
def update_setting(request: Request, category: str, key: str, value: Any = Body(...)):
    """Update a specific setting"""
    settings_manager = request.app.state.app_settings_manager
    
    if not settings_manager.update_setting(category, key, value):
        raise HTTPException(status_code=500, detail="Failed to update setting")
    
    return {"message": "Setting updated successfully", "category": category, "key": key, "value": value}
