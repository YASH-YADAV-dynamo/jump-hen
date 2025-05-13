from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.transaction import Transaction
from solana.system_program import SYS_PROGRAM_ID
import base58
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class WalletHandler:
    def __init__(self):
        # Initialize Solana client (using devnet for testing)
        self.client = Client("https://api.devnet.solana.com", commitment=Confirmed)
        
        # Token program ID (SPL Token program)
        self.token_program_id = PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        
        # Your token mint address (replace with your deployed token)
        self.token_mint = PublicKey(os.getenv('TOKEN_MINT_ADDRESS'))
        
        # Reward amount in lamports (0.01 SOL = 10,000,000 lamports)
        self.reward_amount = 10_000_000
        
        self.connected_wallet = None
        
    def connect_wallet(self, public_key):
        """Connect a Solana wallet"""
        try:
            # Convert public key string to PublicKey object
            wallet_pubkey = PublicKey(public_key)
            
            # Verify the account exists
            account_info = self.client.get_account_info(wallet_pubkey)
            if not account_info.value:
                return False, "Wallet account not found"
            
            self.connected_wallet = wallet_pubkey
            return True, "Connected to Solana wallet"
            
        except Exception as e:
            return False, f"Error connecting wallet: {str(e)}"
    
    def get_balance(self):
        """Get the connected wallet's SOL balance"""
        if not self.connected_wallet:
            return 0
            
        try:
            balance = self.client.get_balance(self.connected_wallet)
            return balance.value / 1e9  # Convert lamports to SOL
        except Exception as e:
            print(f"Error getting balance: {str(e)}")
            return 0
        
    def send_reward(self, score):
        """Send reward SOL based on score"""
        if not self.connected_wallet:
            return False, "No wallet connected"
            
        if score < 100:
            return False, "Score too low for reward"
            
        try:
            # Create a new transaction
            transaction = Transaction()
            
            # Add transfer instruction
            transaction.add(
                self.client.transfer(
                    from_pubkey=self.connected_wallet,
                    to_pubkey=self.connected_wallet,  # In real app, this would be the player's wallet
                    lamports=self.reward_amount
                )
            )
            
            # Sign and send transaction
            # Note: In a real app, you'd need the player's wallet to sign this
            # For testing, we're using a dummy keypair
            keypair = Keypair()
            result = self.client.send_transaction(
                transaction,
                keypair,
                opts={"skip_confirmation": False}
            )
            
            return True, f"Reward sent! Transaction signature: {result.value}"
            
        except Exception as e:
            return False, f"Error sending reward: {str(e)}"
            
    def get_network_name(self):
        """Get the current network name"""
        try:
            # Get cluster nodes to determine network
            nodes = self.client.get_cluster_nodes()
            if "devnet" in str(nodes.value):
                return "Solana Devnet"
            elif "testnet" in str(nodes.value):
                return "Solana Testnet"
            else:
                return "Solana Mainnet"
        except:
            return "Unknown Network"
            
    def get_token_balance(self):
        """Get the connected wallet's token balance"""
        if not self.connected_wallet:
            return 0
            
        try:
            # Get token accounts for the wallet
            token_accounts = self.client.get_token_accounts_by_owner(
                self.connected_wallet,
                {"mint": self.token_mint}
            )
            
            if not token_accounts.value:
                return 0
                
            # Get the first token account's balance
            balance = self.client.get_token_account_balance(
                token_accounts.value[0].pubkey
            )
            
            return float(balance.value.amount) / 10 ** balance.value.decimals
            
        except Exception as e:
            print(f"Error getting token balance: {str(e)}")
            return 0 