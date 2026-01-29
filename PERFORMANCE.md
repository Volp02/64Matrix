## Performance Optimization Guide

### ⚡ Why was my script slow? (The "SetPixel" Trap)

**The Problem:**
Python is an interpreted language. Calling a function like `canvas.SetPixel(x, y, r, g, b)` has a small overhead. But if you call it **4096 times** (64x64 pixels) every frame (30 times a second), that's **122,880 function calls per second**.
This overwhelms the CPU, causing the framerate to drop from 30 FPS to ~8 FPS.

**The Solution: Vectorized Drawing (PIL)**
Instead of setting pixels one by one in Python, we use the **Python Imaging Library (PIL)**.
PIL is written in **C**. When you tell it to `draw.ellipse()` or `img.paste()`, it loops over the pixels **in C**, which is 100x faster than Python.

**❌ SLOW (Pure Python Loops)**

```python
# Don't do this!
for x in range(64):
    for y in range(64):
        canvas.SetPixel(x, y, 255, 0, 0) # 4096 slow calls
```

**✅ FAST (PIL Image)**

```python
from PIL import Image, ImageDraw
# Create image once
img = Image.new('RGB', (64, 64), (255, 0, 0)) # 1 fast C call
# Send to matrix
canvas.SetImage(img)
```

### 🧠 Threading & Architecture

The application runs in two main threads:

1.  **Web Server Thread (FastAPI)**: Handles API requests, serves the dashboard.
2.  **Engine Thread**: The "Heartbeat" of the matrix. It runs `engine.run_threaded()`.

This separation ensures that:

- The web UI stays responsive even if the animation lags.
- The animation stays smooth even if the web server is busy.
- Python's GIL (Global Interpreter Lock) is released during the heavy C++ matrix operations, allowing true parallelism.

### Hardware Tuning

## Critical Optimizations

### 1. Disable Onboard Audio (REQUIRED)

The Raspberry Pi's onboard audio driver (`snd_bcm2835`) uses PWM, which conflicts with the precise timing required by the RGB matrix library. This causes:

- Flickering
- Ghosting
- Poor refresh rates
- Frame drops

**Solution**: Blacklist the audio driver

```bash
# Create blacklist file
echo "blacklist snd_bcm2835" | sudo tee /etc/modprobe.d/blacklist-rgb-matrix.conf

# Reboot to apply
sudo reboot
```

**Note**: This disables the 3.5mm audio jack and HDMI audio. Use USB audio devices if you need sound.

### 2. CPU Core Isolation (RECOMMENDED)

Isolating a CPU core for the matrix reduces jitter and improves stability by preventing the kernel from scheduling other processes on that core.

**For Raspberry Pi 4/5** (4 cores):

```bash
# Edit boot config
sudo nano /boot/firmware/cmdline.txt

# Add to the end of the single line (do not create new lines):
isolcpus=3
```

**For Raspberry Pi 3** (4 cores):

```bash
# Edit boot config
sudo nano /boot/cmdline.txt

# Add to the end of the single line:
isolcpus=3
```

**Reboot** after making changes:

```bash
sudo reboot
```

### 3. Disable Bluetooth (OPTIONAL)

Bluetooth can cause minor interference. If you don't need it:

```bash
# Edit config
sudo nano /boot/firmware/config.txt

# Add these lines:
dtoverlay=disable-bt

# Disable bluetooth service
sudo systemctl disable hciuart.service
sudo systemctl disable bluealsa.service
sudo systemctl disable bluetooth.service

# Reboot
sudo reboot
```

## Verification

### Check if Audio is Disabled

```bash
# Should return nothing if audio is properly disabled
lsmod | grep snd_bcm2835
```

### Check CPU Isolation

```bash
# Should show isolcpus=3 in the output
cat /proc/cmdline
```

### Monitor Performance

```bash
# Check CPU usage while running
htop

# Monitor frame timing (if you have debug logging enabled)
journalctl -u matrix-display -f
```

## Docker Considerations

When running in Docker, the container needs:

1. **Privileged mode** or specific device access:

   ```bash
   docker run --privileged ...
   # OR
   docker run --device=/dev/mem --device=/dev/gpiomem ...
   ```

2. **Host network mode** (optional, for best performance):
   ```bash
   docker run --network=host ...
   ```

## Troubleshooting

### Flickering or Ghosting

- ✅ Verify audio is disabled: `lsmod | grep snd_bcm2835` (should be empty)
- ✅ Check power supply (5V 4A+ recommended)
- ✅ Verify proper grounding
- ✅ Try isolating CPU cores

### Poor Performance

- ✅ Enable CPU isolation
- ✅ Disable Bluetooth if not needed
- ✅ Check system load: `htop`
- ✅ Ensure you're running with `sudo` (hardware access required)

### Matrix Not Detected

- ✅ Check hardware connections
- ✅ Verify you're running with `sudo`
- ✅ Check `/dev/mem` permissions
- ✅ In Docker: ensure `--privileged` or proper device mounts

## Performance Benchmarks

Expected performance on Raspberry Pi 4:

- **Refresh Rate**: 60-120 Hz (configurable)
- **Frame Rate**: 30 FPS (application default)
- **CPU Usage**: 15-30% (one core)
- **Latency**: <16ms frame time

## Additional Resources

- [rpi-rgb-led-matrix GitHub](https://github.com/hzeller/rpi-rgb-led-matrix)
- [Adafruit RGB Matrix Guide](https://learn.adafruit.com/adafruit-rgb-matrix-bonnet-for-raspberry-pi)
