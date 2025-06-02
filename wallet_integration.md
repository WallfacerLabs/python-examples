# Wallet Integration

The example will:
- Check user balances (idle assets) and display them in a formatted table
- Display the best deposit options filtered for USDC/USDS only
- Generate a transaction payload for the 3rd vault option with full transaction details
- Show all user positions across different vaults

## Prerequisites

- Python 3.8+
- An API key from vaults.fyi
- Basic understanding of DeFi and Ethereum addresses

## Setup

1. Clone or download this example project
2. Create virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Set your API key as an environment variable:
```bash
export VAULTS_FYI_API_KEY="your_api_key_here"
```

## Usage

### Running the Example

```
python wallet_integration.py
```


### Example Code Structure

```python
from vaultsfyi import VaultsSdk

# Initialize the SDK
client = VaultsSdk(api_key="your_api_key_here")

# Get user's idle assets
idle_assets = client.get_idle_assets(user_address)

# Get best deposit options (filtered for USDC/USDS)
deposit_options = client.get_deposit_options(
    user_address,
    allowed_assets=["USDC", "USDS"]
)

# Get user positions
positions = client.get_positions(user_address)

# Generate deposit transaction
transaction = client.get_actions(
    action="deposit",
    user_address=user_address,
    network="mainnet",
    vault_address=vault_address,
    amount="1000000",
    asset_address=asset_address,
    simulate=False
)
```




