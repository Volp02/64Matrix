# Performance Optimization Guide

This document explains the performance optimizations required for stable RGB LED matrix operation on Raspberry Pi.

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
