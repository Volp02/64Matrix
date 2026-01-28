# Implementation Plan: Lajos Matrix Framework (LMF)

**Status:** ✅ **Core Implementation Complete** - All major features implemented and working!

## 1. Directory Structure

```plaintext
/64Matrix (LajosMatrix)
├── /app
│   ├── __init__.py
│   ├── main.py                 # ✅ Entry Point: Launches Web Server & Engine Threads
│   ├── /core                   # ✅ The "Brain" & "Muscle"
│   │   ├── __init__.py
│   │   ├── engine.py           # ✅ Master Render Loop (30 FPS, error handling, preview capture)
│   │   ├── state_manager.py   # ✅ Shared State (Thread-Safe Data Store)
│   │   ├── matrix_driver.py    # ✅ Hardware Abstraction (Real vs Emulator, brightness, preview)
│   │   ├── base_scene.py       # ✅ Base class for all scenes
│   │   ├── library_manager.py  # ✅ Metadata & thumbnail management
│   │   ├── playlist_manager.py# ✅ Playlist persistence & management
│   │   ├── /loaders            # ✅ Content Handlers
│   │   │   ├── clip_loader.py  # ✅ GIF/Image Sequence handler (GifScene)
│   │   │   └── script_loader.py# ✅ Python Script dynamic importer
│   │   └── /scenes
│   │       └── playlist_scene.py # ✅ Playlist scene (sequences scripts & clips)
│   ├── /routers                # ✅ API Endpoints
│   │   ├── __init__.py
│   │   ├── system.py           # ✅ Brightness, Speed, Status, Preview endpoint
│   │   ├── scenes.py           # ✅ Scene CRUD, activation, thumbnails
│   │   ├── playlists.py        # ✅ Playlist CRUD & playback
│   │   ├── integrations.py     # ✅ Home Assistant Webhooks
│   │   └── upload.py           # ✅ File Uploads (scripts & GIFs)
│   ├── /models                 # ✅ Pydantic Schemas (Validation)
│   │   └── schemas.py
│   └── /utils
│       └── file_ops.py         # ✅ JSON saving/loading helpers
├── /scenes                     # ✅ User Content Storage
│   ├── /clips                  # ✅ Uploaded GIFs
│   ├── /scripts                # ✅ Uploaded .py files
│   └── /thumbnails             # ✅ Scene thumbnails
├── /web                        # ✅ Frontend Source Code (Vue.js + Vite)
│   ├── package.json
│   ├── vite.config.js
│   ├── /src
│   │   ├── /components        # ✅ SystemControls, etc.
│   │   ├── /services          # ✅ API client
│   │   ├── /views             # ✅ Home, Library, PlaylistEditor
│   │   └── App.vue
│   └── /dist                   # ✅ Compiled Frontend (Served by FastAPI)
├── /data                       # ✅ Persistence
│   ├── config.json             # ✅ Last known brightness/speed
│   ├── library.json            # ✅ Scene metadata & titles
│   └── playlists.json          # ✅ Playlist definitions
├── emulator_config.json        # ✅ Settings for RGBMatrixEmulator
├── requirements.txt            # ✅ Dependencies
├── Implementation_Plan.md     # This file
└── Scope.md                    # Project scope document
```

## 2. Component Details

### A. Core System (`/app/core`)

#### 1. `matrix_driver.py` ✅ **COMPLETE**

**Purpose:** Hardware abstraction layer that works on both Windows (emulator) and Raspberry Pi (real hardware).

- **Logic:** `try: import rgbmatrix except ImportError: import RGBMatrixEmulator`.
- **Methods:** `set_pixel`, `fill`, `clear`, `swap_canvas`, `set_brightness`, `get_brightness`.
- **Features:**
  - ✅ Automatic emulator detection
  - ✅ Hardware brightness control with software fallback
  - ✅ Shadow buffer for preview capture (mirrors canvas state)
  - ✅ Canvas wrapper intercepts SetPixel/SetImage/Fill/Clear calls
  - ✅ Preview frame capture with fallback methods

#### 2. `state_manager.py` ✅ **COMPLETE** (The Shared Brain)

**Purpose:** Single source of truth for both the Web API and the Render Engine.

- **Concurrency:** ✅ Uses `threading.Lock()` for all writes to prevent race conditions.
- **State Objects:**
  - ✅ `active_scene`: The object currently being rendered.
  - ✅ `global_settings`: Dictionary `{ "brightness": 100, "speed": 1.0 }` with validation.
  - ✅ `external_data`: Dictionary for Home Assistant data `{ "temp_out": 12, "solar": 500 }`.
- **Features:**
  - ✅ Persistent settings (saves to `data/config.json`)
  - ✅ Value validation (brightness 0-100, speed 0.1-2.0)
  - ✅ Scene lifecycle hooks (enter/exit methods)
  - ✅ Thread-safe getters/setters

#### 3. `engine.py` ✅ **COMPLETE** (The Heartbeat)

- **Loop:** ✅ Fully implemented
  - ✅ **Input:** Check `state_manager` for the active scene instance.
  - ✅ **Logic:** Call `scene.update(dt)` (passing delta time adjusted by global speed).
  - ✅ **Render:** Call `scene.draw(canvas)`.
  - ✅ **Preview:** Capture frame periodically (every 200ms = 5 FPS).
  - ✅ **Output:** `matrix.swap_canvas()`.
  - ✅ **Timing:** `time.sleep()` dynamically to maintain target FPS (30 FPS).
- **Features:**
  - ✅ Error handling with consecutive error counting
  - ✅ Delta time capping (prevents huge jumps from system sleep)
  - ✅ Automatic scene clearing on too many errors
  - ✅ Preview frame capture and storage
  - ✅ Thread-safe preview frame access

#### 4. Loaders (`/app/core/loaders`) ✅ **COMPLETE**

- ✅ `script_loader.py`: Uses `importlib` to dynamically load `.py` files from `/scenes/scripts`. Injects matrix and `state_manager` into scripts. Scans directory for available scripts.
- ✅ `clip_loader.py`: Loads GIF files as `GifScene` instances. Handles frame extraction, timing, and playback. Supports multiple frame durations.
- ✅ `base_scene.py`: Abstract base class defining the scene interface (`update`, `draw`, `enter`, `exit` methods).

### B. Backend API (`/app/routers`) ✅ **COMPLETE**

#### 1. `system.py` ✅

- ✅ **GET `/api/system/status`**: Returns current brightness, speed, active scene info, active playlist.
- ✅ **POST `/api/system/settings`**: Updates brightness and speed (with hardware application).
- ✅ **GET `/api/system/preview`**: Returns latest preview frame as PNG (scaled 4x for visibility).

#### 2. `scenes.py` ✅

- ✅ **GET `/api/scenes/`**: Lists all available scenes (scripts & clips) with metadata.
- ✅ **POST `/api/scenes/activate`**: Activates a scene by filename (auto-detects script vs clip).
- ✅ **DELETE `/api/scenes/{filename}`**: Deletes a scene and its thumbnail/metadata.
- ✅ **PUT `/api/scenes/{filename}`**: Renames a scene.
- ✅ **POST `/api/scenes/{filename}/thumbnail`**: Uploads a thumbnail image.
- ✅ **GET `/api/scenes/thumbnails/{filename}`**: Serves thumbnail images.

#### 3. `playlists.py` ✅

- ✅ **GET `/api/playlists/`**: Lists all playlists.
- ✅ **POST `/api/playlists/`**: Creates/updates a playlist.
- ✅ **DELETE `/api/playlists/{id}`**: Deletes a playlist.
- ✅ **POST `/api/playlists/{id}/play`**: Activates a playlist (creates PlaylistScene).

#### 4. `integrations.py` ✅ (Home Assistant)

- ✅ **Endpoint:** `POST /api/integrations/data`
- ✅ **Payload:** JSON `{ "key": "solar_power", "value": 1200 }`
- ✅ **Action:** Updates `state_manager.external_data`. Scripts can read `self.state_manager.get_data('solar_power')`.

#### 5. `upload.py` ✅

- ✅ **Logic:**
  - If **GIF**: Save to `/scenes/clips/{filename}`.
  - If **PY**: Save to `/scenes/scripts/{filename}.py`.
- ✅ **Features:**
  - File size validation (10MB limit)
  - Security checks (prevents directory traversal)
  - Auto-creates metadata entries
  - Error handling with cleanup

### C. Core Managers ✅ **COMPLETE**

#### 1. `library_manager.py` ✅

- ✅ Manages scene metadata (titles, thumbnails, custom data).
- ✅ Persists to `data/library.json`.
- ✅ Handles rename/delete operations.

#### 2. `playlist_manager.py` ✅

- ✅ Manages playlist definitions.
- ✅ Persists to `data/playlists.json`.
- ✅ CRUD operations for playlists.

#### 3. `playlist_scene.py` ✅

- ✅ Composite scene that sequences multiple scenes.
- ✅ Supports both scripts and clips in playlists.
- ✅ Configurable duration per item.
- ✅ Automatic scene transitions.

## 3. Implementation Checklist

### Phase 1: The Engine (Python Only) ✅ **COMPLETE**

- [x] **Scaffold**: Create folders and `matrix_driver.py`.
- [x] **State Manager**: Implement the class with `threading.Lock`.
- [x] **Loaders**: Write the `ScriptLoader` that imports a file and instantiates a class.
- [x] **Clip Loader**: Implement GIF loading and playback.
- [x] **Engine**: Write the main loop with error handling.
- [x] **Test**: Created `bouncing_ball.py` and `physics_balls.py` - both working on Emulator.

### Phase 2: The API (FastAPI) ✅ **COMPLETE**

- [x] **Server**: Set up FastAPI in `main.py` and thread the `Engine.run()` function.
- [x] **Endpoints**: Created System, Scenes, Playlists, Integrations, and Upload routers.
- [x] **HA Integration**: Endpoint for data injection implemented.
- [x] **Validation**: API runs alongside Engine without blocking (verified).
- [x] **Preview**: Added preview endpoint for live display visualization.

### Phase 3: The Frontend (Vue.js) ✅ **COMPLETE**

- [x] **Setup**: Vue.js + Vite project in `/web`.
- [x] **API Client**: JS module to fetch status/scenes/playlists.
- [x] **Dashboard**: Home view with status, controls, and live preview.
- [x] **Library**: Scene grid with thumbnails, activation, delete, rename.
- [x] **Playlist Editor**: Create and manage playlists with drag-and-drop.
- [x] **Upload**: File upload handling for scripts and GIFs.
- [x] **Build**: FastAPI serves `/web/dist` folder as static files.

### Phase 4: Polish ✅ **COMPLETE**

- [x] **Persistence**: `config.json` loaded on startup (brightness/speed remembered).
- [x] **Library Metadata**: Scene titles and thumbnails persisted.
- [x] **Playlists**: Playlist definitions persisted to `playlists.json`.
- [x] **Error Handling**: Comprehensive error handling throughout.
- [x] **Preview**: Live preview of matrix display in web dashboard.
- [x] **Brightness Control**: Hardware brightness with software fallback.
- [x] **Clip Support**: Full GIF support in playlists and scenes.
- [x] **Optimization**: Render loop maintains 30 FPS target.

### Phase 5: Additional Features ✅ **COMPLETE**

- [x] **Live Preview**: Real-time preview of matrix display in web UI.
- [x] **Thumbnail Management**: Upload and serve scene thumbnails.
- [x] **Scene Metadata**: Title management and display names.
- [x] **Playlist Support**: Sequences of scripts and clips with durations.
- [x] **Security**: File upload validation and directory traversal prevention.
- [x] **Error Recovery**: Automatic scene clearing on repeated errors.

## 4. Verification Plan ✅ **VERIFIED**

### Automated Tests ✅

- ✅ **Emulator Check**: Running the engine on Windows opens RGBMatrixEmulator browser window (port 8888).
- ✅ **API Check**: `GET http://localhost:8000/api/system/status` returns JSON with current state.
- ✅ **Preview Check**: `GET http://localhost:8000/api/system/preview` returns PNG image of current frame.

### Manual Verification ✅

- ✅ **Hot-Swap**: Upload new scripts/GIFs via web UI - appears immediately in scene list.
- ✅ **Scene Activation**: Clicking scenes in library activates them instantly.
- ✅ **Playlist Playback**: Playlists cycle through scenes with correct durations.
- ✅ **Brightness/Speed**: Sliders update display in real-time.
- ✅ **HA Data**: `POST /api/integrations/data` updates external data store.
- ✅ **Preview**: Live preview updates every 200ms showing current matrix state.
- ✅ **Thumbnails**: Scene thumbnails display correctly in library.

## 5. Current Status & Known Issues

### ✅ Working Features

- Core rendering engine (30 FPS)
- Script scene loading and execution
- GIF clip loading and playback
- Playlist creation and playback
- Web API (all endpoints)
- Frontend dashboard
- Live preview (with fallback methods)
- Brightness and speed controls
- Scene management (CRUD operations)
- Thumbnail management
- Home Assistant integration
- File uploads with validation

### 🔧 Recent Improvements

- Fixed duplicate imports in `main.py`
- Added clip support to playlists
- Implemented hardware brightness control
- Enhanced error handling throughout
- Added live preview functionality
- Fixed scene name display (shows titles instead of class names)
- Improved canvas wrapper for preview capture

### 📝 Future Enhancements (Optional)

- [✅] OTA updates via DockerHub
- [ ] Multi-matrix support
- [ ] Scene scheduling (time-based playlists)
- [ ] WebSocket for real-time updates (instead of polling)
