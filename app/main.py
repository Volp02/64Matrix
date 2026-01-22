import sys
import os
import time
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.matrix_driver import MatrixDriver
from app.core.state_manager import StateManager
from app.core.engine import Engine
from app.core.loaders.script_loader import ScriptLoader
from app.core.loaders.clip_loader import ClipLoader
from app.core.loaders.clip_loader import ClipLoader
from app.core.library_manager import LibraryManager
from app.core.playlist_manager import PlaylistManager

# Import Routers
from app.routers import system, scenes, integrations, upload, playlists

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global State Container for FastAPI
class AppState:
    matrix: MatrixDriver
    state_manager: StateManager
    engine: Engine
    script_loader: ScriptLoader
    clip_loader: ClipLoader

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Core Components...")
    try:
        matrix = MatrixDriver()
        state_manager = StateManager()
        engine = Engine(matrix, state_manager)
        loader = ScriptLoader(matrix, state_manager)
        clip_loader = ClipLoader(matrix, state_manager)
        clip_loader = ClipLoader(matrix, state_manager)
        library_manager = LibraryManager()
        playlist_manager = PlaylistManager()
        
        # Store in app.state for routers to access
        app.state.matrix_driver = matrix
        app.state.state_manager = state_manager
        app.state.engine = engine
        app.state.script_loader = loader
        app.state.clip_loader = clip_loader
        app.state.library_manager = library_manager
        app.state.playlist_manager = playlist_manager
        
        # Load Initial Scene
        scripts = loader.list_available_scripts()
        if "bouncing_ball.py" in scripts:
            scene = loader.get_scene("bouncing_ball.py")
            if scene:
                state_manager.set_scene(scene)
        
        # Start Engine in separate thread
        engine.run_threaded()
        
    except Exception as e:
        logger.critical(f"Failed to initialize: {e}")
        sys.exit(1)
        
    yield
    
    # Shutdown
    logger.info("Shutting down Engine...")
    app.state.engine.stop()

app = FastAPI(title="Lajos Matrix Framework", lifespan=lifespan)

# Include Routers
app.include_router(system.router)
app.include_router(scenes.router)
app.include_router(integrations.router)
app.include_router(integrations.router)
app.include_router(upload.router)
app.include_router(playlists.router)

# Mount Static Files (Frontend)
if os.path.exists("web/dist"):
    app.mount("/", StaticFiles(directory="web/dist", html=True), name="static")
else:
    logger.warning("Frontend /web/dist not found. Run 'npm run build' in /web to serve UI.")

def main():
    # Run Uvicorn Config
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
