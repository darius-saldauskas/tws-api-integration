from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import *
import threading
import time

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False

    def nextValidId(self, orderId: int):
        print(f"Next valid order ID: {orderId}")
        self.connected = True

    def error(self, reqId: TickerId, errorCode: int, errorString: str, advancedOrderRejectJson=""):
        print(f"Error: {reqId} {errorCode} {errorString}")
        if advancedOrderRejectJson:
            print(f"Advanced reject info: {advancedOrderRejectJson}")

def run_connection_test():
    app = IBapi()
    app.connect("192.168.1.9", 4002, clientId=1)
    
    # Start the socket in a thread
    api_thread = threading.Thread(target=app.run)
    api_thread.start()
    
    # Wait for connection
    time.sleep(1)
    
    if app.connected:
        print("Successfully connected to TWS!")
        print(f"Server version: {app.serverVersion()}")
        print(f"Connection time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("Connection failed")
    
    # Disconnect
    app.disconnect()
    api_thread.join()

if __name__ == "__main__":
    run_connection_test()