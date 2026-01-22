import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def wait_for_server():
    print("Waiting for server...")
    for _ in range(10):
        try:
            requests.get(f"{BASE_URL}/docs")
            print("Server is up!")
            return True
        except requests.ConnectionError:
            time.sleep(1)
    return False

def test_system_status():
    print("Testing /api/system/status...")
    resp = requests.get(f"{BASE_URL}/api/system/status")
    if resp.status_code == 200:
        print("PASS:", resp.json())
    else:
        print("FAIL:", resp.status_code, resp.text)

def test_list_scenes():
    print("Testing /api/scenes/...")
    resp = requests.get(f"{BASE_URL}/api/scenes/")
    if resp.status_code == 200:
        print("PASS:", resp.json())
        return resp.json()['scenes']
    else:
        print("FAIL:", resp.status_code, resp.text)
        return []

def test_activate_scene(scenes):
    if not scenes:
        print("Skipping activation test (no scenes)")
        return

    target = scenes[0]['filename']
    print(f"Testing /api/scenes/activate with {target}...")
    resp = requests.post(f"{BASE_URL}/api/scenes/activate", json={"filename": target})
    if resp.status_code == 200:
        print("PASS:", resp.json())
    else:
        print("FAIL:", resp.status_code, resp.text)

def test_integration_data():
    print("Testing /api/integrations/data...")
    data = {"key": "solar", "value": 5000}
    resp = requests.post(f"{BASE_URL}/api/integrations/data", json=data)
    if resp.status_code == 200:
        print("PASS:", resp.json())
    else:
        print("FAIL:", resp.status_code, resp.text)

if __name__ == "__main__":
    if not wait_for_server():
        print("Server failed to start.")
        sys.exit(1)
        
    test_system_status()
    scenes = test_list_scenes()
    test_activate_scene(scenes)
    test_integration_data()
    print("Verification Complete.")
