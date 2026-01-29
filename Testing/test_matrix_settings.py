#!/usr/bin/env python3
"""
Matrix Settings Diagnostic Tool
Tests different multiplexing and row_address_type combinations to find optimal settings.

Usage: sudo python test_matrix_settings.py

Press ENTER to cycle through each setting.
Press 'q' + ENTER to quit.
"""

import time
import sys

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    EMULATED = False
except ImportError:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions
    EMULATED = True
    print("⚠️  Running in emulator mode - settings won't affect real hardware")

# All multiplexing options (0-18)
MULTIPLEXING_OPTIONS = {
    0: "Direct (default)",
    1: "Stripe",
    2: "Checker (ZnZ)",
    3: "Spiral",
    4: "Z-Stripe /8",
    5: "Z-Stripe /4",
    6: "Z-Stripe /8 Half",
    7: "Coreman ABC Shift",
    8: "Kaler2Scan",
    9: "P10-128x4-Z",
    10: "QiangLiQ8",
    11: "InversedZStripe",
    12: "P10Outdoor1R1G1B-1",
    13: "P10Outdoor1R1G1B-2",
    14: "P10Outdoor1R1G1B-3",
    15: "P10Coreman",
    16: "P8Outdoor1R1G1B",
    17: "FlippedStripe",
    18: "P10Outdoor32x16HalfScan",
}

# Row address types (0-4)
ROW_ADDRESS_OPTIONS = {
    0: "Direct (default)",
    1: "AB-Addressed",
    2: "Direct AB-Addressed",
    3: "ABC-Addressed",
    4: "ABC Shift + DE",
}

def create_matrix(multiplexing, row_address_type):
    """Create a matrix with the given settings."""
    options = RGBMatrixOptions()
    
    # Panel settings for P3 64x64-32S
    options.rows = 64
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'adafruit-hat'
    
    # Anti-flicker settings
    options.gpio_slowdown = 4
    options.pwm_bits = 11
    options.pwm_lsb_nanoseconds = 130
    options.brightness = 50  # Keep brightness low for testing
    
    # Test settings
    options.multiplexing = multiplexing
    options.row_address_type = row_address_type
    options.show_refresh_rate = True  # Show refresh rate for diagnostics
    
    return RGBMatrix(options=options)

def draw_test_pattern(canvas, width, height):
    """Draw a simple vertical stripe test pattern."""
    for x in range(width):
        for y in range(height):
            # Vertical stripes in Red, Green, Blue
            if x % 12 < 4:
                canvas.SetPixel(x, y, 255, 0, 0)  # Red
            elif x % 12 < 8:
                canvas.SetPixel(x, y, 0, 255, 0)  # Green
            else:
                canvas.SetPixel(x, y, 0, 0, 255)  # Blue

def main():
    print("=" * 60)
    print("Matrix Settings Diagnostic Tool")
    print("Panel: P3 64x64-32S (1/32 scan)")
    print("=" * 60)
    print()
    print("This will test different multiplexing and row_address_type")
    print("combinations to find the best settings for your panel.")
    print()
    print("Controls:")
    print("  ENTER = Next setting")
    print("  'q' + ENTER = Quit")
    print("  's' + ENTER = Save current setting (prints to console)")
    print()
    input("Press ENTER to start...")
    
    current_multiplexing = 0
    current_row_address = 0
    
    best_settings = None
    
    while True:
        print()
        print("-" * 60)
        print(f"Testing: multiplexing={current_multiplexing} ({MULTIPLEXING_OPTIONS.get(current_multiplexing, 'Unknown')})")
        print(f"         row_address_type={current_row_address} ({ROW_ADDRESS_OPTIONS.get(current_row_address, 'Unknown')})")
        print("-" * 60)
        
        try:
            matrix = create_matrix(current_multiplexing, current_row_address)
            canvas = matrix.CreateFrameCanvas()
            
            # Draw test pattern
            draw_test_pattern(canvas, matrix.width, matrix.height)
            canvas = matrix.SwapOnVSync(canvas)
            
            # Wait for user input
            print("Look at the display. Is it correct?")
            user_input = input("[ENTER=next, 's'=save this setting, 'q'=quit]: ").strip().lower()
            
            # Cleanup matrix before next iteration
            del matrix
            
            if user_input == 'q':
                print("\nExiting...")
                break
            elif user_input == 's':
                best_settings = (current_multiplexing, current_row_address)
                print(f"\n✅ SAVED: multiplexing={current_multiplexing}, row_address_type={current_row_address}")
                print("Add these to matrix_driver.py:")
                print(f"    self.options.multiplexing = {current_multiplexing}")
                print(f"    self.options.row_address_type = {current_row_address}")
            
            # Move to next setting
            current_row_address += 1
            if current_row_address > 4:
                current_row_address = 0
                current_multiplexing += 1
                
            if current_multiplexing > 18:
                print("\n✅ All settings tested!")
                break
                
        except Exception as e:
            print(f"❌ Error with this setting: {e}")
            print("Skipping to next...")
            current_row_address += 1
            if current_row_address > 4:
                current_row_address = 0
                current_multiplexing += 1
            time.sleep(0.5)
    
    if best_settings:
        print()
        print("=" * 60)
        print("BEST SETTINGS FOUND:")
        print(f"  multiplexing = {best_settings[0]}")
        print(f"  row_address_type = {best_settings[1]}")
        print("=" * 60)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
