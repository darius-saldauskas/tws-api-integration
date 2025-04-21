import pandas as pd
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.common import *
from ibapi.contract import Contract
import threading
import time
from datetime import datetime

class OrderBookApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.orderbook_ready = False
        self.bids = []
        self.asks = []
        self.snapshot_time = None
        
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        print(f"Error: {reqId} {errorCode} {errorString}")
        
    def nextValidId(self, orderId: int):
        self.connected = True
        print("Connection confirmed")
        
    def updateMktDepth(self, reqId, position, operation, side, price, size):
        """Handle order book updates"""
        entry = {
            'position': position,
            'operation': operation,
            'price': price,
            'size': size,
            'timestamp': datetime.now(),
            'side': 'bid' if side == 0 else 'ask'
        }
        
        if side == 0:  # Bid
            self.bids.append(entry)
        else:  # Ask
            self.asks.append(entry)
            
    def updateMktDepthL2(self, reqId, position, marketMaker, operation, 
                        side, price, size, isSmartDepth):
        """Handle level 2 order book updates"""
        entry = {
            'position': position,
            'market_maker': marketMaker,
            'operation': operation,
            'price': price,
            'size': size,
            'is_smart': isSmartDepth,
            'timestamp': datetime.now(),
            'side': 'bid' if side == 0 else 'ask'
        }
        
        if side == 0:  # Bid
            self.bids.append(entry)
        else:  # Ask
            self.asks.append(entry)
            
    def get_orderbook_df(self):
        """Combine bids and asks into a single DataFrame"""
        bids_df = pd.DataFrame(self.bids)
        asks_df = pd.DataFrame(self.asks)
        
        if not bids_df.empty and not asks_df.empty:
            return pd.concat([bids_df, asks_df], ignore_index=True)
        elif not bids_df.empty:
            return bids_df
        elif not asks_df.empty:
            return asks_df
        else:
            return pd.DataFrame()

def create_tsla_contract():
    """Create TSLA stock contract for NASDAQ"""
    contract = Contract()
    contract.symbol = "TSLA"
    contract.secType = "STK"
    contract.exchange = "NASDAQ"
    contract.currency = "USD"
    return contract

def main():
    app = OrderBookApp()
    app.connect("192.168.1.9", 4002, clientId=1)
    
    # Start socket in thread
    api_thread = threading.Thread(target=app.run)
    api_thread.start()
    
    # Wait for connection
    while not app.connected:
        time.sleep(0.1)
    
    # Create contract and request market depth
    tsla = create_tsla_contract()
    req_id = 1  # Unique request identifier
    app.reqMktDepth(req_id, tsla, 10, False, [])  # Request 10 levels
    
    # Wait for order book data
    print("Collecting order book data...")
    time.sleep(5)  # Allow time for data collection
    
    # Get DataFrame
    orderbook_df = app.get_orderbook_df()
    
    # Clean up
    try:
        app.cancelMktDepth(req_id, False)  # False for isSmartDepth
        print("Market depth subscription cancelled")
    except Exception as e:
        print(f"Error cancelling market depth: {e}")
    
    app.disconnect()
    api_thread.join()
    print("Disconnected from TWS")
    
    # Process and display results
    if not orderbook_df.empty:
        print("\nTSLA Order Book Snapshot:")
        print(orderbook_df.to_string())
        
        # Add additional processing if needed
        orderbook_df['price'] = pd.to_numeric(orderbook_df['price'])
        orderbook_df['size'] = pd.to_numeric(orderbook_df['size'])
        
        print("\nSummary Statistics:")
        print(orderbook_df.groupby('side').agg({
            'price': ['count', 'mean', 'min', 'max'],
            'size': ['sum', 'mean']
        }))
    else:
        print("No order book data received")

if __name__ == "__main__":
    main()