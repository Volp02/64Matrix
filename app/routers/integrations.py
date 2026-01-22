from fastapi import APIRouter, Request
from app.models.schemas import IntegrationData
from app.core.state_manager import StateManager

router = APIRouter(prefix="/api/integrations", tags=["Integrations"])

@router.post("/data")
def update_data(request: Request, data: IntegrationData):
    state_manager: StateManager = request.app.state.state_manager
    
    state_manager.set_data(data.key, data.value)
    
    return {"status": "ok", "key": data.key, "value": data.value}
