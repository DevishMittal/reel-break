import requests
import time
import json
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SP_URL = os.getenv("SCREENPIPE_URL", "http://localhost:3030")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
INTERVAL = int(os.getenv("CHECK_INTERVAL", "15"))  # Check every 15 seconds by default
MAX_RETRIES = 3

def get_screenpipe_activity():
    """Get latest OCR info from ScreenPipe"""
    print("🔍 Fetching latest OCR data from ScreenPipe...")
    retries = 0

    while retries < MAX_RETRIES:
        try:
            response = requests.get(
                f"{SP_URL}/search?limit=1&offset=0&content_type=ocr", timeout=(10, 20)
            )
            response.raise_for_status()
            print("✅ OCR data fetched successfully!")
            data = response.json()

            if not data.get("data"):
                print("⚠️ No OCR data found. Skipping this cycle.")
                return None
            
            # Add timestamp for tracking purposes
            data["timestamp"] = datetime.datetime.now().isoformat()
            return data

        except requests.exceptions.Timeout:
            print(f"⚠️ Request timed out. Retrying ({retries+1}/{MAX_RETRIES})...")
            retries += 1
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching ScreenPipe data: {e}")
            return None
    
    print("❌ Max retries reached. Skipping this cycle.")
    return None

def main():
    """Run OCR processing on an interval"""
    print("🚀 Starting ScreenBreak client...")
    print(f"📡 Connecting to ScreenPipe at {SP_URL}")
    print(f"📡 Connecting to ScreenBreak server at {BACKEND_URL}")
    
    while True:
        ocr_data = get_screenpipe_activity()
        if not ocr_data:
            print(f"⏳ Snoozing for {INTERVAL} seconds before next check...")
            time.sleep(INTERVAL)
            continue

        print(f"📤 Posting OCR data to backend")
        try:
            response = requests.post(f"{BACKEND_URL}/process_screen", json=ocr_data, timeout=(10, 20))
            response.raise_for_status()
            print(f"✅ Request posted successfully! Response: {response.status_code}")
            
            # Check if we need to show an intervention
            if response.json().get("intervention_required", False):
                intervention_data = response.json().get("intervention_data", {})
                print(f"⚠️ Intervention required! Type: {intervention_data.get('type')}")
                
                # Display notification or intervention depending on the type
                if intervention_data.get("type") == "notification":
                    # In a full implementation, this would trigger a system notification
                    print(f"📢 NOTIFICATION: {intervention_data.get('message')}")
                elif intervention_data.get("type") == "overlay":
                    # In a full implementation, this would display an overlay
                    print(f"🛑 OVERLAY: {intervention_data.get('message')}")
            
        except requests.exceptions.Timeout:
            print("⚠️ Backend request timed out. Skipping this cycle.")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error posting to backend: {e}")

        print(f"⏳ Snoozing for {INTERVAL} seconds before next check...")
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()