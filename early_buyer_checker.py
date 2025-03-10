import requests
import time
from collections import defaultdict
import pandas as pd
from datetime import datetime


BASESCAN_API_KEY = "A8R2H2RP2PFKRVEKHMG762B3WFPB7XEUUE"


CONTRACT_ADDRESSES = [
    "0xc0634090F2Fe6c6d75e61Be2b949464aBB498973",
    "0x937a1cFAF0A3d9f5Dc4D0927F72ee5e3e5F82a00"
]


def fetch_all_transactions(contract_address):
    url = "https://api.basescan.org/api"
    all_transactions = []
    page = 1
    page_size = 1000  
    
    print(f"🔍 Fetching ALL transaction history for contract: {contract_address}...")
    
    while True:
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": contract_address,
            "page": page,
            "offset": page_size,
            "sort": "asc",  
            "apikey": BASESCAN_API_KEY
        }
        
        try:
            print(f"  📄 Fetching page {page}...")
            response = requests.get(url, params=params)
            data = response.json()
            
            if data["status"] != "1":
                print(f"  ❌ Error fetching data: {data.get('message', 'Unknown error')}")
                break
                
            result = data["result"]
            if not result:
                break  
                
            all_transactions.extend(result)
            print(f"  ✅ Fetched {len(result)} transactions. Total: {len(all_transactions)}")
            
            if len(result) < page_size:
                break  
                
            page += 1
            time.sleep(1) 
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request failed: {e}")
            break
            
    return all_transactions


def fetch_dex_swaps(contract_address):
    """
    In a real implementation, you would connect to subgraphs or other data sources
    to get actual price data. This is a simplified simulation.
    """
    print(f"📊 Fetching price data for token {contract_address}...")
    
    
    def generate_simulated_price_data(transactions):
        if not transactions:
            return {}
            
        price_data = {}
        
        
        token_decimals = int(transactions[0].get("tokenDecimal", "18"))
        
        
        current_price = 0.000001  
        
        
        blocks = {}
        for tx in transactions:
            block_num = int(tx["blockNumber"])
            if block_num not in blocks:
                blocks[block_num] = []
            blocks[block_num].append(tx)
        
        
        sorted_blocks = sorted(blocks.keys())
        for i, block_num in enumerate(sorted_blocks):
            block_txs = blocks[block_num]
            
            
            buy_volume = 0
            sell_volume = 0
            
            for tx in block_txs:
                value = int(tx["value"]) / (10 ** token_decimals)
                if tx["to"].lower() == contract_address.lower():
                   
                    buy_volume += value
                elif tx["from"].lower() == contract_address.lower():
                    
                    sell_volume += value
            
           
            net_pressure = buy_volume - sell_volume
            if abs(net_pressure) > 0:
                price_change = net_pressure * 0.01  
                current_price = max(0.000001, current_price * (1 + price_change))
            
            
            price_data[block_num] = current_price
            
            
            if i < len(sorted_blocks) // 3:  
                
                current_price *= 1.01  
            
        return price_data
    
   
    transactions = fetch_all_transactions(contract_address)
    
    
    price_data = generate_simulated_price_data(transactions)
    
    print(f"📊 Generated price data for {len(price_data)} blocks")
    return price_data, transactions


def identify_early_buyers(transactions, price_data, max_buyers=500):
    buyers = {}
    buy_count = 0
    token_decimals = int(transactions[0].get("tokenDecimal", "18"))
    token_symbol = transactions[0].get("tokenSymbol", "TOKEN")
    
    print(f"👨‍💼 Identifying first {max_buyers} buyers of {token_symbol}...")
    
    
    sorted_txs = sorted(transactions, key=lambda x: (int(x["blockNumber"]), int(x["timeStamp"])))
    
    for tx in sorted_txs:
        to_address = tx["to"].lower()
        from_address = tx["from"].lower()
        contract_address = tx["contractAddress"].lower()
        
       
        if to_address == contract_address or from_address == contract_address:
            continue
        
        
        token_amount = int(tx["value"]) / (10 ** token_decimals)
        if token_amount == 0:
            continue

        
        if to_address not in buyers:
            block_number = int(tx["blockNumber"])
            entry_price = price_data.get(block_number, 0)
            
            if entry_price > 0:  
                timestamp = int(tx["timeStamp"])
                date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
                buyers[to_address] = {
                    "wallet": to_address,
                    "amount": token_amount,
                    "entry_price": entry_price,
                    "entry_block": block_number,
                    "entry_time": date_str,
                    "tx_hash": tx["hash"]
                }
                
                buy_count += 1
                
        if buy_count >= max_buyers:
            break
    
    print(f"👨‍💼 Found {len(buyers)} unique early buyers")
    return list(buyers.values())


def find_10x_holders(early_buyers, transactions, price_data):
    
    wallet_balances = defaultdict(float)
    wallet_data = {buyer["wallet"]: buyer for buyer in early_buyers}
    ten_x_holders = []
    
    
    token_decimals = int(transactions[0].get("tokenDecimal", "18"))
    token_symbol = transactions[0].get("tokenSymbol", "TOKEN")
    
    print(f"💰 Analyzing wallets for 10x holding behavior for {token_symbol}...")
    
    
    sorted_txs = sorted(transactions, key=lambda x: (int(x["blockNumber"]), int(x["timeStamp"])))
    
    
    for tx in sorted_txs:
        to_address = tx["to"].lower()
        from_address = tx["from"].lower()
        token_amount = int(tx["value"]) / (10 ** token_decimals)
        block_number = int(tx["blockNumber"])
        
        
        if token_amount > 0:
            wallet_balances[to_address] += token_amount
            wallet_balances[from_address] -= token_amount
        
        
        current_price = price_data.get(block_number, 0)
        if current_price == 0:
            continue
        
        
        if from_address in wallet_data and to_address != from_address:
            buyer_data = wallet_data[from_address]
            entry_price = buyer_data["entry_price"]
            
            
            if current_price >= entry_price * 10:
                
                if wallet_balances[from_address] > 0:
                    
                    if from_address not in ten_x_holders:
                        timestamp = int(tx["timeStamp"])
                        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        
                        print(f"  💎 {from_address} held through 10x! Entry: ${entry_price:.6f}, Current: ${current_price:.6f}")
                        print(f"     Entry time: {buyer_data['entry_time']}, 10x reached: {date_str}")
                        
                        ten_x_holders.append({
                            "wallet": from_address,
                            "entry_price": entry_price,
                            "peak_price": current_price,
                            "multiple": current_price / entry_price,
                            "entry_time": buyer_data["entry_time"],
                            "peak_time": date_str,
                            "current_balance": wallet_balances[from_address]
                        })
    
    print(f"💰 Found {len(ten_x_holders)} wallets that held through 10x price increase")
    return ten_x_holders


def save_results(ten_x_holders, contract_address):
    if not ten_x_holders:
        print("⚠️ No results to save")
        return
        
    
    df = pd.DataFrame(ten_x_holders)
    
    
    filename = f"10x_holders_{contract_address[:8]}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    
    df.to_csv(filename, index=False)
    print(f"📄 Results saved to {filename}")
    
    return filename


def analyze_contract(contract_address):
    print("=" * 80)
    print(f"🚀 Starting analysis for contract: {contract_address}")
    print("=" * 80)
    
    
    price_data, transactions = fetch_dex_swaps(contract_address)
    
    if not transactions:
        print(f"⚠️ No transactions found for {contract_address}. Skipping...")
        return []
    
    if not price_data:
        print(f"⚠️ Could not generate price data for {contract_address}. Skipping...")
        return []
    
    
    early_buyers = identify_early_buyers(transactions, price_data, max_buyers=500)
    
    if not early_buyers:
        print(f"⚠️ No early buyers identified for {contract_address}. Skipping...")
        return []
    
    
    ten_x_holders = find_10x_holders(early_buyers, transactions, price_data)
    
    
    if ten_x_holders:
        print("\n📜 Wallets that held through 10x price increase:")
        for i, holder in enumerate(ten_x_holders[:10], 1):  
            print(f"{i}. {holder['wallet']}")
            print(f"   Entry: ${holder['entry_price']:.6f}, Peak: ${holder['peak_price']:.6f} ({holder['multiple']:.1f}x)")
            print(f"   Entry time: {holder['entry_time']}, Peak time: {holder['peak_time']}")
            print(f"   Current balance: {holder['current_balance']:.4f}")
            print()
        
        if len(ten_x_holders) > 10:
            print(f"...and {len(ten_x_holders) - 10} more wallets")
        
        
        save_results(ten_x_holders, contract_address)
    else:
        print("\n⚠️ No wallets found that held through 10x price increase")
    
    print("-" * 80)
    return ten_x_holders


def main():
    all_holders = []
    
    for contract_address in CONTRACT_ADDRESSES:
        holders = analyze_contract(contract_address)
        all_holders.extend(holders)
        time.sleep(3)
    
    print("\n" + "=" * 80)
    print(f"✅ Analysis complete! Found {len(all_holders)} total 10x holders across all contracts")
    print("=" * 80)

if __name__ == "__main__":
    main()
