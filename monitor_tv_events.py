#!/usr/bin/env python3
"""
Simple script to monitor all WebSocket events from Samsung Frame TV.
Run this to see what events the TV broadcasts in real-time.
"""

import sys
import json
import time
from datetime import datetime

sys.path.append('samsung-tv-ws-api')
from samsungtvws import SamsungTVWS

TV_IP = "192.168.86.25"  # Change this to your TV IP

def event_callback(event_type, data):
    """Called whenever the TV sends an event."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    print(f"\n{'='*80}")
    print(f"[{timestamp}] EVENT: {event_type}")
    print(f"{'='*80}")

    # Pretty print the data
    if isinstance(data, dict):
        print(json.dumps(data, indent=2))
    else:
        print(data)

    print(f"{'='*80}\n")


def main():
    print(f"Connecting to TV at {TV_IP}...")
    print("\n⚠️  IMPORTANT:")
    print("When you see the connection attempt, a popup will appear on your TV.")
    print("You must click ALLOW on the TV within a few seconds!\n")
    input("Press ENTER when ready to connect (make sure you can see your TV)...")

    print("\n📺 Connecting now... WATCH YOUR TV FOR THE POPUP!")
    print("Listening for events... (Press Ctrl+C to stop)")
    print("\nNow try:")
    print("  - Change artwork using TV remote")
    print("  - Adjust brightness")
    print("  - Change color temperature")
    print("  - Turn art mode on/off")
    print("  - Use Samsung SmartThings app")
    print("  - Launch an app on the TV")
    print("\n")

    tv = None
    try:
        # Try simple connection without token (like backend does)
        print("Attempting connection...")
        tv = SamsungTVWS(host=TV_IP, name="EventMonitor")

        # Start listening to events
        tv.start_listening(callback=event_callback)

        print("✅ Connected! Monitoring events...\n")

        # Keep the script running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nStopping event monitor...")
        if tv:
            tv.close()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure your TV is ON and on the same network")
        print("  2. Check if art mode is enabled on the TV")
        print("  3. The TV might require you to:")
        print("     - Go to Settings > General > External Device Manager")
        print("     - Enable 'Device Connect Manager'")
        print("  4. Try turning the TV off and on again")
        print("\nIf you still see 'unauthorized', your TV may have security settings")
        print("that require you to accept connections from the TV's menu.")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
