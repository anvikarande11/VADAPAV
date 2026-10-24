from web3 import Web3
import os

# Get node provider URL from environment or fallback to local testnet (Ganache/Hardhat)
WEB3_PROVIDER_URI = os.getenv("WEB3_PROVIDER_URI", "http://127.0.0.1:8545")

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))

    def is_connected(self) -> bool:
        """Checks if the FastAPI backend has a live connection to the blockchain node."""
        try:
            return self.w3.is_connected()
        except Exception:
            return False

    def get_latest_block(self) -> int:
        """Fetches the latest block number for hackathon status checks."""
        if self.is_connected():
            return self.w3.eth.block_number
        return 0

bc_service = BlockchainService()