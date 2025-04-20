from ib_insync import IB
import time

# Last updated: 2025-04-20

def test_connection():
    ib = IB()
    try:
        print("Attempting to connect to TWS...")
        ib.connect('192.168.1.9', 4002, clientId=1, timeout=15)
        print("\nConnection successful!")
        print(f"TWS Server version: {ib.client.serverVersion()}")
        print(f"Local time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Basic API status check
        if ib.isConnected():
            print("API connection is active")
            try:
                if hasattr(ib.client, 'isReadOnly') and ib.client.isReadOnly():
                    print("Warning: API is in read-only mode")
                else:
                    print("API connection established")
            except:
                print("Basic connection verified (advanced status check unavailable)")
        else:
            print("Warning: Connection status inconsistent")
            
    except Exception as e:
        print(f"\nConnection failed: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("Disconnected from TWS")

if __name__ == '__main__':
    test_connection()