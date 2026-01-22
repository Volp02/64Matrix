import sys

print("1. Checking Python version...")
print(sys.version)

print("\n2. Checking Libraries...")
try:
    import numpy
    print("   [OK] Numpy")
except ImportError as e:
    print(f"   [FAIL] Numpy: {e}")

try:
    import pygame
    print("   [OK] Pygame")
except ImportError as e:
    print(f"   [FAIL] Pygame: {e}")

try:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    print("   [OK] RGBMatrixEmulator")
except ImportError as e:
    print(f"   [FAIL] Emulator: {e}")
    print("   (This usually means a dependency like 'bdfparser' is missing)")

print("\n3. Launching Test Window (Close window to finish)...")
try:
    options = RGBMatrixOptions()
    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()

    # Draw a red X
    for i in range(64):
        canvas.SetPixel(i, i, 255, 0, 0)
        canvas.SetPixel(i, 63-i, 255, 0, 0)

    matrix.SwapOnVSync(canvas)
    print("   [OK] Window created! Press CTRL+C in terminal to stop.")

    # Keep window open
    import time
    while True:
        time.sleep(1)

except Exception as e:
    print(f"   [FAIL] Window Error: {e}")