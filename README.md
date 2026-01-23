# Lajos Matrix Framework (LMF) v1.0.0

A self-hosted, modular LED display platform for Raspberry Pi with 64x64 RGB LED matrices. The system enables dynamic "hot-swapping" of content, allowing you to upload new art, animations, and code directly via a web browser without rebooting the device.

## Features

- 🎨 **Hybrid Rendering**: Supports both pre-rendered clips (GIFs) and dynamic Python scripts
- 🌐 **Web Interface**: Modern Vue.js dashboard for managing scenes, playlists, and settings
- 🔄 **Hot-Loading**: Upload and activate new content without restarting
- 📋 **Playlists**: Create sequences of scenes with customizable durations
- 🎨 **Color Palettes**: Apply color schemes to compatible scenes
- 🔌 **Integrations**: Home Assistant webhook support for automation
- 🖼️ **Live Preview**: Real-time preview of the current display
- ⚡ **Real-time Control**: Adjust brightness and speed on the fly

## Hardware Requirements

- **Raspberry Pi** (Model 3B or newer recommended)
- **Raspberry Pi OS** (64-bit Lite or Desktop)
- **Adafruit RGB Matrix Bonnet** (or compatible HUB75 interface)
- **64x64 RGB LED Matrix** (HUB75)
- **5V 4A+ Power Supply**

## Quick Start

### Docker Installation (Recommended)

The easiest way to get started is using Docker:

```bash
# Clone the repository
git clone https://github.com/your-username/64Matrix.git
cd 64Matrix

# Start the application
docker compose up -d --build
```

The application will be available at `http://<your-pi-ip>:8000`

For detailed Docker setup instructions, see [README_DOCKER.md](README_DOCKER.md).

### Manual Installation

For manual setup without Docker, see [README_SETUP.md](README_SETUP.md).

## Project Structure

```
64Matrix/
├── app/                    # Python backend application
│   ├── core/              # Core engine, state management, drivers
│   ├── routers/           # FastAPI API endpoints
│   ├── models/            # Pydantic schemas
│   └── utils/             # Utility functions
├── web/                   # Vue.js frontend
│   └── src/               # Frontend source code
├── scenes/                # User content
│   ├── scripts/           # Python animation scripts
│   ├── clips/             # GIF/image sequences
│   └── thumbnails/        # Auto-generated thumbnails
└── data/                  # Persistent data (playlists, settings)
```

## Architecture

The system uses a **Master Loop Design** to ensure frame-perfect timing:

- **Render Engine**: Primary blocking loop maintaining 30 FPS
- **State Manager**: Thread-safe state tracking (current scene, settings)
- **Web Server**: FastAPI thread handling UI requests and API calls

This architecture avoids Python GIL stuttering by keeping rendering logic synchronous within the render cycle.

## Content Types

### Scripts (Dynamic Scenes)
Python files that generate animations in real-time. Examples include:
- Physics simulations
- Particle effects
- Live data visualizations
- Interactive games

### Clips (Pre-rendered)
Animated GIFs or image sequences that play back pixel-perfect.

## API Documentation

The API is available at `/api/` when the server is running. Key endpoints:

- `GET /api/system/status` - Get system status and version
- `POST /api/system/settings` - Update brightness, speed, palette
- `GET /api/scenes` - List available scenes
- `POST /api/scenes/activate` - Activate a scene
- `GET /api/playlists` - List playlists
- `POST /api/upload` - Upload new scenes or clips

## Version

Current version: **1.0.0** (Testing/Release Candidate)

Version information is available via the `/api/system/status` endpoint.

**⚠️ Status**: This version is currently under testing. The Docker Hub build and publish process is being validated. Some features may be unstable or untested.

## Docker Hub

Pre-built Docker images are available on Docker Hub (currently testing):

```bash
docker pull volp02/matrix-display-64:latest
# or for a specific version:
docker pull volp02/matrix-display-64:v1.0.0
```

**Note**: The Docker Hub images are being tested for build and deployment. If you encounter issues, please report them via GitHub issues.

## Development

### Building the Frontend

```bash
cd web
npm install
npm run build
```

### Running Tests

```bash
cd Testing
python verify.py
python verify_api.py
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]

## Support

For issues and questions, please open an issue on GitHub.

---

## ⚠️ Current Status

**v1.0.0 Release Candidate** - This version is currently being tested:

- ✅ Docker build configuration complete
- ✅ GitHub Actions workflow configured for Docker Hub publishing
- 🔄 **In Progress**: Testing Docker Hub build and publish process
- 🔄 **In Progress**: Validating image download and deployment from Docker Hub
- ⚠️ **Not fully tested**: Some features may be unstable or untested

This release is intended to validate the Docker Hub deployment pipeline. Once testing is complete and any issues are resolved, a stable release will be published.

**For testing purposes**: Pull `volp02/matrix-display-64:latest` and report any issues you encounter.
