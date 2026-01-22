# Project Scope: Lajos Matrix Framework (LMF) v2.1

## 1. Project Overview

**Project Name:** Lajos Matrix Framework (LMF)

**Objective:** To create a self-hosted, modular LED display platform. The system allows for dynamic "Hot-Swapping" of content, enabling the user to upload new art, animations, and code directly via a web browser without rebooting the device.

## 2. Hardware Architecture

- **Compute:** Raspberry Pi 3 Model B (OS: Raspberry Pi OS Lite 64-bit).
- **Interface:** Adafruit RGB Matrix Bonnet.
- **Display:** 64x64 RGB LED Matrix (HUB75).
- **Power:** 5V 4A+ PSU.

## 3. Technology Stack

### A. Core System (Python)

- **Driver:** rpi-rgb-led-matrix (hzeller).
- **Architecture (Master Loop Design):**
  - **Render Engine (Master Loop):** The primary blocking loop. It maintains frame-perfect timing and queries the State Manager for the next frame to draw on every tick.
  - **State Manager:** A Logic Module (not a thread) that tracks the current scene, playlist progress, and transitions. It responds instantly to the Render Engine's requests.
  - **Web Server Thread:** A separate thread/process (FastAPI) handling UI requests and API calls. It communicates with the Master Loop via thread-safe queues/events to trigger state changes.
    _Note: This architecture avoids Python GIL (Global Interpreter Lock) stuttering issues by keeping logic synchronous within the render cycle._

- **Content Definitions:**
  - **"Clips" (Animated Scenes):** Pre-rendered static assets like Uploaded GIFs or Image Sequences.
  - **"Scripts" (Programmed Scenes):** Dynamic Python code files handling Physics-based animations, Logic, or Live Data (e.g., from Home Assistant or APIs).

- **Dynamic Loader:** System to import/reload Python modules at runtime.

### B. Web Server (The Controller)

- **Backend:** FastAPI (Python). Modern, fast, and handles concurrent requests.
- **Frontend:** HTML5/JavaScript (Vue.js or Vanilla JS).

## 4. Functional Requirements

### Feature Set 1: The Scene Engine

- **Hybrid Rendering:** Supports both **Clips** (pixel-perfect playback) and **Scripts** (live drawing).
- **Global Variables:**
  - **Brightness:** 0-100% hardware dimming.
  - **Speed:** 0.1x to 2.0x time dilation.
- **Hot-Loading:** Watched folders for auto-registering new uploads.

### Feature Set 2: The Web Interface (UI)

A "Dashboard" style web app optimized for mobile and desktop.

#### 1. The Scene Grid (Dashboard)

- Displays Thumbnails and Names of all available content.
- Clicking a tile activates that Clip, Script, or Custom Scene.
- Visual indicator for the active item.

#### 2. Global Controls

- **Brightness Slider:** Real-time adjustment.
- **Animation Speed Slider:** 0% to 200%.

#### 3. The Creator Studio (Upload Center)

- **Upload Clips:** Drag-and-drop ZIPs/GIFs. Auto-unpacks to create a Clip.
- **Upload Scripts:** Text editor/upload for `.py` files. Validates and installs.
- **Thumbnail Generator:** Custom preview images.

#### 4. The Scene Builder (Playlist Editor)

A specific page to create and manage custom **Composite Scenes** (Playlists):

- **Create Scene:** Ability to name and create a new Scene entry.
- **Composition:** Select from available **Clips** and **Scripts** to build a sequence.
- **Order & Settings:** Arrange the order of animations and set a custom loop speed.
- **Persistence (JSON):** All Scenes and Playlists are saved to a simple `scenes.json` or `config.json` file. This flat-file approach is preferred over a database for easy manual editing and backup.

### Feature Set 3: Smart Integrations

- **Home Assistant Hook:** API endpoint (`/api/data`) for storing external JSON payloads (Temperatures, Solar, Notifications) in a shared "Data Store" for **Scripts**.

## 5. Development Roadmap (Updated)

### Phase 1: The Engine (Python)

- [ ] Build Master Loop Render Engine.
- [ ] Implement Synchronous State Manager.
- [ ] Create "Clip Player" (Image sequence handler).
- [ ] Create "Script Runner" (Python module handler).

### Phase 2: The API (FastAPI)

- [ ] Endpoints to list/switch content.
- [ ] File Upload endpoints.
- [ ] **JSON Persistence Layer** (Read/Write `scenes.json`).

### Phase 3: The Frontend (Web)

- [ ] Scene Grid UI.
- [ ] Upload Form.
- [ ] **Scene Builder Page** (Drag-and-drop playlist creation).

### Phase 4: More animations and Ideas

- [ ] OTA Update. (updating the webserver and Program code in an easy way, maybe just via github)
- [ ] Animations, inspired by this: https://tidbyt.com/pages/apps
