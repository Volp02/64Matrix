# Setup Instructions

## Running on Raspberry Pi

### Prerequisites

1. **Python 3.8+** (usually pre-installed on Raspberry Pi OS)
2. **Node.js and npm** (for building the frontend)
3. **Real RGBMatrix library** (optional - for actual hardware, otherwise uses emulator)

### Step 1: Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python and build tools
sudo apt install -y python3-pip python3-venv build-essential

# Install Node.js (if not already installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# For real RGBMatrix hardware (optional):
# Follow instructions at: https://github.com/hzeller/rpi-rgb-led-matrix
# This typically involves:
# sudo apt install -y python3-dev python3-pillow
# git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
# cd rpi-rgb-led-matrix
# make build-python PYTHON=$(which python3)
# sudo make install-python PYTHON=$(which python3)
```

### Step 2: Clone/Transfer Project

```bash
# If using git:
git clone <your-repo-url>
cd jsw

# Or transfer files via SCP/SFTP
```

### Step 3: Build Frontend

```bash
cd web
npm install
npm run build
cd ..
```

### Step 4: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Run the Application

```bash
# Make sure you're in the project root directory
python -m app.main

# Or if using virtual environment:
source venv/bin/activate
python -m app.main
```

The application will:
- Start on `http://0.0.0.0:8000` (accessible from any device on your network)
- Auto-detect if real RGBMatrix hardware is available
- Fall back to emulator if hardware not found
- Serve the web interface at the root URL

### Step 6: Access the Web Interface

Open a browser and navigate to:
- `http://localhost:8000` (from the Pi itself)
- `http://<raspberry-pi-ip>:8000` (from another device on the network)

### Running as a Service (Optional)

Create a systemd service file `/etc/systemd/system/matrix-display.service`:

```ini
[Unit]
Description=Matrix Display Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/jsw
Environment="PATH=/home/pi/jsw/venv/bin"
ExecStart=/home/pi/jsw/venv/bin/python -m app.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable matrix-display.service
sudo systemctl start matrix-display.service
sudo systemctl status matrix-display.service
```

## Docker Setup

### Quick Start

1. **Build the Docker image:**
```bash
docker build -t matrix-display .
```

2. **Run with emulator (for testing):**
```bash
docker run -d \
  --name matrix-display \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/scenes:/app/scenes \
  matrix-display
```

3. **Run with real hardware (Raspberry Pi only):**
```bash
docker run -d \
  --name matrix-display \
  --privileged \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/scenes:/app/scenes \
  --device=/dev/mem \
  matrix-display
```

### Access the Web Interface

- `http://localhost:8000` (from host)
- `http://<raspberry-pi-ip>:8000` (from network)

### Notes on Docker

- **Hardware Access**: Real RGBMatrix requires direct hardware access. Use `--privileged` flag or specific device mounts.
- **Performance**: Running in Docker may have slight performance overhead.
- **Data Persistence**: Volumes are mounted to preserve playlists, palettes, and settings.
- **Emulator Mode**: Works great for testing without hardware!
