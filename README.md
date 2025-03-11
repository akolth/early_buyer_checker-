# early_buyer_checker
## Setup Instructions                                                                                                       

This document aims to provide a know-how for setting up and using this Tool, this script was created to analyze the contract addresses of two tokens on the Base network and the aim was to have an overview of the buyers within the first 500 transactions, also the buyers have to have held for at least 10x from entry.

## Setup Instructions

### Dependencies

The tool requires:
- Python 3.7 or higher
- pandas (for data handling)
- requests (for API calls)

### Installation Steps

#### For macOS:
 best to run this on cli 
1. **Install Python** :
   - Download and install from [python.org](https://www.python.org/downloads/)
   - Or use Homebrew: `brew install python` via cli 

2. **Install required packages**:
   ```bash
   pip3 install pandas requests
   ```

#### For Windows:

1. **Install Python**:
   - Download and install from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install required packages**:
   - Open Command Prompt as Administrator
   - Run:
     ```
     pip install pandas requests
     ```

## Using the Tool

### Step 1: Prepare Your Configuration

1. Save the script as `early_buyer_checker.py`
2. Open the file in a text editor or with nano/vim from cli
3. Update the following variables at the top of the script:
   - `BASESCAN_API_KEY`: Your Basescan API key (get one at [basescan.org](https://basescan.org/) it's free)
   - `CONTRACT_ADDRESSES`: List of token contract addresses you want to analyze (api could be rate limited, do not use too many addresses)
PS: Edit out the addresses in the script unless if you intend to get analysis for the same tokens i analysed


### Step 2: Run the Analysis

#### On macOS:

1. Open Terminal
2. Navigate to the directory containing the script:
   ```bash
   cd /path/to/script/directory
   ```
3. Run the script:
   ```bash
   python3 early_buyer_checker.py
   ```

#### On Windows:

1. Open Command Prompt
2. Navigate to the directory containing the script:
   ```
   cd C:\path\to\script\directory
   ```
3. Run the script:
   ```
   python early_buyer_checker.py
   ```

### Step 3: Monitor Progress

- The script will display progress information with emoji indicators
- For each contract, you'll see:
  - 🔍 Transaction fetching progress
  - 📊 Price data generation
  - 👨‍💼 Early buyer identification
  - 💰 10x holder analysis
- The analysis might take several minutes depending on the number of transactions, rate limit of api and network strength

### Step 4: View Results

- When analysis is complete, the script will save it as a CSV file for each of the  analyzed contract
- Filename format will show as  `10x_holders_[contract]_[date].csv` (there's a csv per contract address)


## Extracting Unique Wallet Addresses

The csv file will could contain repition of same addresses because the script is tracking each transaction separately, so if a wallet made multiple transactions, it appears multiple times, so sort through this and generate unique addresses you can follow these steps:

### Using Python (Both macOS and Windows):

1. Save this script as `extract_wallets.py`:
   ```python
   import pandas as pd
   import sys

   # Check if filename was provided
   if len(sys.argv) < 2:
       print("Please provide the CSV filename")
       print("Usage: python extract_wallets.py 10x_holders_filename.csv")
       sys.exit(1)

   # Load the CSV file
   filename = sys.argv[1]
   df = pd.read_csv(filename)

   # Extract unique wallet addresses
   unique_wallets = df['wallet'].unique()

   # Print the number of unique wallets
   print(f"Found {len(unique_wallets)} unique wallet addresses")

   # Save unique addresses to a text file, one per line
   output_file = "unique_wallets.txt"
   with open(output_file, "w") as f:
       for wallet in unique_wallets:
           f.write(f"{wallet}\n")

   print(f"Saved unique wallet addresses to {output_file}")
   ```

2. Run it with your CSV file:
   ```bash
   python extract_wallets.py 10x_holders_0xc06340_20250310.csv
   ```

### Using Command Line Tools (shorter and preferable):

#### On macOS:
```bash
tail -n +2 10x_holders_0xc06340_20250310.csv | cut -d, -f1 | sort | uniq > unique_wallets.txt
```

#### On Windows:
```powershell
Import-Csv .\10x_holders_0xc06340_20250310.csv | Select-Object -Property wallet -Unique | ForEach-Object { $_.wallet } | Out-File -FilePath unique_wallets.txt
```

## Troubleshooting

- **API Rate Limits**: If you see errors about API rate limits, increase the `time.sleep()` values in the script
- **Missing Data**: If no transactions are found, double-check your contract addresses and API key
- **Memory Errors**: For tokens with very large transaction histories, you might need to limit the analysis timeframe

## Limitations

- The price data is simulated based on transaction patterns and may not reflect actual market prices
- For more accurate analysis, consider connecting to DEX (Decentralized Exchange) APIs for real price data
- The tool analyzes on-chain data only and cannot track off-chain transfers

---

For questions or improvements, please reach out to [https://x.com/gridrrr] on X(fka Twitter) or @akolth on telegram.
