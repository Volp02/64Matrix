# Implementation Plan: Lajos Matrix Framework (LMF)

## 1. Directory Structure

```plaintext
/LajosMatrix
├── /app
│   ├── __init__.py
│   ├── main.py                 # Entry Point: Launches Web Server & Engine Threads
│   ├── /core                   # The "Brain" & "Muscle"
│   │   ├── __init__.py
│   │   ├── engine.py           # Master Render Loop (High Priority)
│   │   ├── state_manager.py    # Shared State (Thread-Safe Data Store)
│   │   ├── matrix_driver.py    # Hardware Abstraction (Real vs Emulator)
│   │   └── /loaders            # Content Handlers
│   │       ├── clip_loader.py  # Image Sequence / GIF handler
│   │       └── script_loader.py# Python Script dynamic importer
│   ├── /routers                # API Endpoints
│   │   ├── __init__.py
│   │   ├── system.py           # Brightness, Speed, Power
│   │   ├── scenes.py           # Scene selection & Playlist management
│   │   ├── integrations.py     # Home Assistant Webhooks
│   │   └── upload.py           # File Uploads
│   ├── /models                 # Pydantic Schemas (Validation)
│   │   └── schemas.py
│   └── /utils
│       └── file_ops.py         # JSON saving/loading helpers
├── /scenes                     # User Content Storage
│   ├── /clips                  # Uploaded GIFs/ZIPs
│   └── /scripts                # Uploaded .py files
├── /web                        # Frontend Source Code (Vue.js + Vite)
│   ├── package.json
│   ├── vite.config.js
│   ├── /src
│   └── /dist                   # Compiled Frontend (Served by FastAPI)
├── /data                       # Persistence (GitIgnored)
│   ├── config.json             # Last known brightness/speed
│   └── scenes.json             # Playlist definitions
├── emulator_config.json        # Settings for RGBMatrixEmulator
├── requirements.txt
└── README.md
```

## 2. Component Details

### A. Core System (`/app/core`)

#### 1. `matrix_driver.py`

**Purpose:** Prevents code crashes on Windows.

- **Logic:** `try: import rgbmatrix except ImportError: import RGBMatrixEmulator`.
- **Methods:** `set_pixel`, `fill`, `clear`, `swap_canvas`.

#### 2. `state_manager.py` (The Shared Brain)

**Purpose:** Single source of truth for both the Web API and the Render Engine.

- **Concurrency:** Must use `threading.Lock()` for all writes to prevent race conditions.
- **State Objects:**
  - `active_scene`: The object currently being rendered.
  - `global_settings`: Dictionary `{ "brightness": 100, "speed": 1.0 }`.
  - `external_data`: Dictionary for Home Assistant data `{ "temp_out": 12, "solar": 500 }`.

#### 3. `engine.py` (The Heartbeat)

- **Loop:**
  - **Input:** Check `state_manager` for the active scene instance.
  - **Logic:** Call `scene.update(dt)` (passing delta time adjusted by global speed).
  - **Render:** Call `scene.draw(canvas)`.
  - **Output:** `matrix.swap_on_vsync(canvas)`.
  - **Timing:** `time.sleep()` dynamically to maintain target FPS (e.g., 30 or 60).

#### 4. Loaders (`/app/core/loaders`)

- `script_loader.py`: Uses `importlib` to dynamically load `.py` files from `/scenes/scripts`. It must inject the matrix object and `state_manager` into the script so the user's code can draw things and read sensor data.

### B. Backend API (`/app/routers`)

#### 1. `integrations.py` (Home Assistant)

- **Endpoint:** `POST /api/integrations/data`
- **Payload:** JSON `{ "key": "solar_power", "value": 1200 }`
- **Action:** Updates `state_manager.external_data`. This allows any Python script to simply read `self.data['solar_power']` to visualize it.

#### 2. `upload.py`

- **Logic:**
  - If **ZIP/GIF**: Unpack to `/scenes/clips/{name}/`.
  - If **PY**: Save to `/scenes/scripts/{name}.py`.
- **Auto-Discovery:** Trigger a `state_manager.refresh_scenes()` to update the list immediately.

## 3. Implementation Checklist

### Phase 1: The Engine (Python Only)

- [ ] **Scaffold**: Create folders and `matrix_driver.py`.
- [ ] **State Manager**: Implement the class with `threading.Lock`.
- [ ] **Loaders**: Write the `ScriptLoader` that imports a file and instantiates a class.
- [ ] **Engine**: Write the main loop.
- [ ] **Test**: Create a `bouncing_ball.py` in `/scenes/scripts` and run `main.py` to see it on the Emulator.

### Phase 2: The API (FastAPI)

- [ ] **Server**: Set up FastAPI in `main.py` and thread the `Engine.run()` function.
- [ ] **Endpoints**: Create the System and Scene routers.
- [ ] **HA Integration**: specific endpoint for data injection.
- [ ] **Validation**: Ensure the API runs alongside the Engine without blocking it.

### Phase 3: The Frontend (Vue.js)

- [ ] **Setup**: `npm create vite@latest` in `/web`.
- [ ] **API Client**: Create a JS module to fetch status/scenes.
- [ ] **Grid**: Render the list of scenes.
- [ ] **Upload**: File input handling.
- [ ] **Build**: Configure FastAPI to serve the `/web/dist` folder as static files.

### Phase 4: Polish

- [ ] **Persistence**: Ensure `config.json` is loaded on startup so brightness/playlist settings are remembered.
- [ ] **Optimization**: Profiling the Render Loop to ensure it stays under 33ms (30FPS).

## 4. Verification Plan

### Automated Tests

- **Emulator Check**: Running the engine on Windows should immediately open a PyGame window.
- **API Check**: `curl http://localhost:8000/api/system/status` should return JSON while the animation is playing smoothly.

### Manual Verification

- **Hot-Swap**: While an animation is playing, upload a new script via the API (Swagger UI). The system should not crash, and the new script should appear in the list.
- **HA Data**: Send a POST request with fake solar data. Verify the "Power" scene updates its graph instantly.
