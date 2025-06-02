#!/usr/bin/env python3
"""
Vaults.fyi Python SDK Example Implementation

This example demonstrates how to use the vaults.fyi Python SDK to:
0. Check user balances (idle assets)
1. Find the best deposit options for USDC/USDS
2. Generate transaction payloads for depositing into vaults
3. View user positions and balances
"""

import os
import sys
from typing import Dict, Any, List, Optional
from tabulate import tabulate

from vaultsfyi import VaultsSdk


# Example address
USER_ADDRESS = '0xdB79e7E9e1412457528e40db9fCDBe69f558777d'


def format_transaction_blob(transaction: Dict[str, Any]) -> str:
    """Format transaction data into a readable table."""
    if not transaction or not isinstance(transaction, dict):
        return 'No transaction data available'
    
    def truncate_value(key: str, value: str, max_length: int = 50) -> str:
        """Truncate long values for better table formatting."""
        if key == 'data' and len(value) > 20:
            return value[:20] + '...'
        elif len(value) > max_length:
            return value[:max_length] + '...'
        return value
    
    # Create table data for all transaction properties
    table_data = []
    
    # Add basic transaction properties
    for key, value in transaction.items():
        if key == 'actions':
            continue  # Handle separately
        elif value is None or value == "":
            table_data.append([key, 'N/A'])
        else:
            formatted_value = truncate_value(key, str(value))
            table_data.append([key, formatted_value])
    
    # Handle actions array
    if 'actions' in transaction and isinstance(transaction['actions'], list):
        table_data.append(['', ''])  # Empty row for spacing
        table_data.append(['Total Actions', str(len(transaction['actions']))])
        table_data.append(['', ''])  # Empty row for spacing
        
        for i, action in enumerate(transaction['actions']):
            if isinstance(action, dict):
                # Action header
                action_name = action.get('name', f'Action {i+1}')
                truncated_name = truncate_value('name', action_name, 60)
                table_data.append([f'Action {i+1}', truncated_name])
                
                # Transaction details
                tx_details = action.get('tx', {})
                for tx_key, tx_value in tx_details.items():
                    formatted_value = truncate_value(tx_key, str(tx_value))
                    table_data.append([f'  {tx_key}', formatted_value])
                
                # Add spacing between actions
                if i < len(transaction['actions']) - 1:
                    table_data.append(['', ''])
            else:
                truncated_action = truncate_value('action', str(action))
                table_data.append([f'Action {i+1}', truncated_action])
    
    return f"\n🎯 Generated Transaction Blob:\n{tabulate(table_data, headers=['Property', 'Value'], tablefmt='grid', maxcolwidths=[20, 60])}"


def format_deposit_options(deposit_options_response: Dict[str, Any]) -> str:
    """Format deposit options into a readable table."""
    if not deposit_options_response or not deposit_options_response.get('userBalances'):
        return 'No deposit options available'
    
    table_data = []
    headers = ['Asset', 'Balance USD', 'Network', 'Vault Name', 'Protocol', 'APY']
    
    for balance in deposit_options_response.get('userBalances', []):
        for option in balance.get('depositOptions', []):
            asset_symbol = balance.get('asset', {}).get('symbol', 'N/A')
            balance_usd = balance.get('asset', {}).get('balanceUsd')
            balance_usd_formatted = f"${float(balance_usd):.2f}" if balance_usd else 'N/A'
            
            network_name = option.get('network', {}).get('name', 'N/A')
            
            vault_name = option.get('name', 'N/A')
            vault_name_short = vault_name[:18] + '...' if len(vault_name) > 18 else vault_name
            
            protocol_name = option.get('protocol', {}).get('name', 'N/A')
            
            apy = option.get('apy', {}).get('total')
            apy_formatted = f"{apy * 100:.2f}%" if apy else 'N/A'
            
            table_data.append([
                asset_symbol,
                balance_usd_formatted,
                network_name,
                vault_name_short,
                protocol_name,
                apy_formatted
            ])
    
    return tabulate(table_data, headers=headers, tablefmt='grid')


def format_positions(positions: Dict[str, Any]) -> str:
    """Format user positions into a readable table."""
    if not positions or not positions.get('data') or not isinstance(positions.get('data'), list):
        return 'No positions available'
    
    table_data = []
    headers = ['Network', 'Protocol', 'Vault Name', 'Asset', 'Balance USD', 'APY']
    
    has_positions = False
    for position in positions.get('data', []):
        has_positions = True
        
        network_name = position.get('network', {}).get('name', 'N/A')
        protocol_name = position.get('protocol', {}).get('name', 'N/A')
        
        vault_name = position.get('name', 'Unknown Vault')
        vault_name_short = vault_name[:16] + '...' if len(vault_name) > 16 else vault_name
        
        asset_symbol = position.get('asset', {}).get('symbol', 'N/A')
        
        balance_usd = position.get('asset', {}).get('balanceUsd')
        balance_usd_formatted = f"${float(balance_usd):.2f}" if balance_usd else 'N/A'
        
        apy = position.get('apy', {}).get('total')
        apy_formatted = f"{apy * 100:.2f}%" if apy else 'N/A'
        
        table_data.append([
            network_name,
            protocol_name,
            vault_name_short,
            asset_symbol,
            balance_usd_formatted,
            apy_formatted
        ])
    
    return tabulate(table_data, headers=headers, tablefmt='grid') if has_positions else 'No active positions found'


def format_user_balances(idle_assets: Dict[str, Any]) -> str:
    """Format user balances into a readable table."""
    if not idle_assets or not idle_assets.get('data') or not isinstance(idle_assets.get('data'), list):
        return 'No idle assets available'
    
    table_data = []
    headers = ['Asset', 'Balance', 'Balance USD', 'Network']
    
    has_balances = False
    for asset in idle_assets.get('data', []):
        has_balances = True
        
        symbol = asset.get('symbol', 'N/A')
        
        balance_native = asset.get('balanceNative')
        balance_formatted = f"{float(balance_native):.6f} {symbol}" if balance_native else 'N/A'
        
        balance_usd = asset.get('balanceUsd')
        balance_usd_formatted = f"${float(balance_usd):.2f}" if balance_usd else 'N/A'
        
        network_name = asset.get('network', {}).get('name', 'N/A')
        
        table_data.append([
            symbol,
            balance_formatted,
            balance_usd_formatted,
            network_name
        ])
    
    return tabulate(table_data, headers=headers, tablefmt='grid') if has_balances else 'No idle assets found'


def get_user_balances(client: VaultsSdk) -> Optional[Dict[str, Any]]:
    """Get user's idle assets/balances."""
    try:
        idle_assets = client.get_idle_assets(USER_ADDRESS)
        print('💰 User balances:')
        print(format_user_balances(idle_assets))
        return idle_assets
    except Exception as error:
        print(f'Error fetching user balances: {error}')
        return None


def get_best_deposit_options(client: VaultsSdk) -> Optional[Dict[str, Any]]:
    """Get best deposit options filtered for USDC/USDS."""
    try:
        deposit_options = client.get_deposit_options(
            USER_ADDRESS,
            allowed_assets=['USDC', 'USDS']
        )
        
        print('📊 Best deposit options (USDC/USDS only):')
        print(format_deposit_options(deposit_options))
        return deposit_options
    except Exception as error:
        print(f'Error fetching deposit options: {error}')
        return None


def generate_deposit_transaction_with_asset(
    client: VaultsSdk,
    vault_address: str,
    amount: str,
    user_address: str,
    network: str = 'mainnet',
    asset_address: str = None
) -> Optional[Dict[str, Any]]:
    """Generate deposit transaction for specified vault and asset."""
    try:
        transaction = client.get_actions(
            action='deposit',
            user_address=user_address,
            network=network,
            vault_address=vault_address,
            amount=amount,
            asset_address=asset_address,
            simulate=False
        )
        
        print(format_transaction_blob(transaction))
        return transaction
    except Exception as error:
        print(f'❌ Transaction generation failed: {error}')
        return {
            'success': False,
            'message': 'Transaction generation failed',
            'error': str(error)
        }


def get_user_positions(client: VaultsSdk) -> Optional[Dict[str, Any]]:
    """Get user's positions across all vaults."""
    try:
        positions = client.get_positions(USER_ADDRESS)
        print('💼 User positions:')
        print(format_positions(positions))
        return positions
    except Exception as error:
        print(f'Error fetching user positions: {error}')
        return None


def run_example_implementation():
    """Run the complete example implementation."""
    print('🔷 ===== Vaults.fyi Python SDK Example Implementation ===== 🔷\n')
    
    # Check for API key
    api_key = os.getenv('VAULTS_FYI_API_KEY')
    if not api_key:
        print('Please set VAULTS_FYI_API_KEY environment variable')
        return
    
    # Initialize the SDK
    client = VaultsSdk(api_key=api_key)
    
    # 0. Show user balances
    print('💰 0. Checking user balances...')
    get_user_balances(client)
    
    # 1. Get best deposit options
    print('\n📈 1. Finding best deposit options...')
    top_options = get_best_deposit_options(client)
    
    # 2. Generate a deposit transaction (if we have deposit options)
    user_balances = top_options.get('userBalances', []) if top_options else []
    if user_balances and len(user_balances) > 0:
        first_asset = user_balances[0]
        deposit_options = first_asset.get('depositOptions', [])
        
        if len(deposit_options) >= 3:  # Use 3rd vault (index 2)
            first_deposit_option = deposit_options[2]
            vault_name = first_deposit_option.get('name', 'Unknown vault')
            print(f'\n💳 2. Generating deposit transaction into {vault_name}...')
            
            # Extract vault address and asset address from the deposit option
            vault_address = first_deposit_option.get('address')
            asset_address = first_asset.get('asset', {}).get('address')
            
            # Extract network string from the deposit option
            network = 'mainnet'  # Default
            if first_deposit_option.get('network'):
                network_data = first_deposit_option.get('network')
                if isinstance(network_data, str):
                    network = network_data
                elif isinstance(network_data, dict):
                    network = network_data.get('name', 'mainnet')
            
            if vault_address and asset_address:
                amount = '1000000'  # 1 USDC (6 decimals)
                
                generate_deposit_transaction_with_asset(
                    client,
                    vault_address,
                    amount,
                    USER_ADDRESS,
                    network,
                    asset_address
                )
            else:
                print('❌ Could not find vault address or asset address in deposit option')
                print(f'Vault address: {vault_address}')
                print(f'Asset address: {asset_address}')
        else:
            print('❌ Not enough deposit options available (need at least 3)')
    else:
        print('❌ No deposit options available')
    
    # 3. View user positions
    print('\n💼 3. Checking user positions...')
    get_user_positions(client)
    
    print('\n🎉 === Example Implementation Complete === 🎉')


if __name__ == '__main__':
    run_example_implementation()