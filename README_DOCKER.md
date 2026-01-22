# Docker Installation Guide for Raspberry Pi

This guide explains how to run the Matrix Display application using Docker on your Raspberry Pi.

## Prerequisites

- **Raspberry Pi** (Model 3B or newer recommended).
- **Raspberry Pi OS** (64-bit Lite recommended also works on Desktop).
- **Docker & Docker Compose** installed.
  ```bash
  curl -sSL https://get.docker.com | sh
  sudo usermod -aG docker $USER
  # (Log out and back in for group changes to take effect)
  ```

## Installation Steps

1.  **Clone the Repository** (if you haven't already):

    ```bash
    git clone https://github.com/your-username/64Matrix.git
    cd 64Matrix
    ```

2.  **Build and Run**:
    Run the following command to build the Docker image and start the container.

    > **Note**: The first build will take **5-10 minutes** because it compiles the matrix hardware library from source on the Pi.

    ```bash
    docker compose up -d --build
    ```

3.  **Verify Status**:
    Check if the container is running and healthy:

    ```bash
    docker compose ps
    docker compose logs -f
    ```

    You should see logs indicating the server started on port 8000.

4.  **Access the Dashboard**:
    Open your browser and navigate to:
    `http://<your-pi-ip>:8000`

## Important Notes

- **Hardware Access**: The container runs in `privileged` mode to access the GPIO pins for the LED matrix. Ensure no other service (like the `led-image-viewer` demo or another instance) is using the potential pins.
- **Persistence**: Your settings, uploaded scenes, and playlists are saved in the `./data` and `./scenes` folders, which are mapped into the container.
- **Updates**: To update the code, pull the latest changes and restart:
  ```bash
  git pull
  docker compose down
  docker compose up -d --build
  ```
