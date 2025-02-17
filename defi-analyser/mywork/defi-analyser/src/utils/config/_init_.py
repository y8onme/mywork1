# src/utils/config/__init__.py

import os
from dotenv import load_dotenv
from typing import Dict

from .base_config import ChainConfig, AIConfig, SecurityConfig, DBConfig
from .eth_config import get_eth_config
from .bsc_config import get_bsc_config
from .polygon_config import get_polygon_config
from .arbitrum_config import get_arbitrum_config
from .optimism_config import get_optimism_config
from .avalanche_config import get_avalanche_config
from .fantom_config import get_fantom_config
from .cronos_config import get_cronos_config
from .base_chain_config import get_base_config
from .zksync_config import get_zksync_config

class Config:
    def __init__(self):
        load_dotenv()
        
        # Initialize all chain configurations
        self.chains: Dict[int, ChainConfig] = {
            1: get_eth_config(),
            56: get_bsc_config(),
            137: get_polygon_config(),
            42161: get_arbitrum_config(),
            10: get_optimism_config(),
            43114: get_avalanche_config(),
            250: get_fantom_config(),
            25: get_cronos_config(),
            8453: get_base_config(),
            324: get_zksync_config()
        }

        # AI Configuration
        self.ai_config = AIConfig(
            model_path="models/attack_optimizer.pt",
            hidden_size=256,
            learning_rate=0.001,
            batch_size=64,
            max_epochs=1000,
            early_stopping_patience=10,
            transformer_layers=6,
            attention_heads=8,
            dropout_rate=0.1,
            llm_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=2000
        )

        # Security Configuration
        self.security_config = SecurityConfig(
            min_confirmations={
                1: 12,    # Ethereum
                56: 15,   # BSC
                137: 256, # Polygon
                42161: 64,  # Arbitrum
                10: 64,     # Optimism
                43114: 12,  # Avalanche
                250: 5,     # Fantom
                25: 10,     # Cronos
                8453: 64,   # Base
                324: 32     # zkSync Era
            },
            max_gas_price={
                1: 300,     # Gwei for Ethereum
                56: 10,     # Gwei for BSC
                137: 100,   # Gwei for Polygon
                42161: 1.5, # Gwei for Arbitrum
                10: 0.1,    # Gwei for Optimism
                43114: 100, # Gwei for Avalanche
                250: 500,   # Gwei for Fantom
                25: 5000,   # Gwei for Cronos
                8453: 0.1,  # Gwei for Base
                324: 0.25   # Gwei for zkSync Era
            },
            timeout_seconds=30,
            max_retries=3,
            blacklisted_contracts=[],
            security_checks=[
                "reentrancy",
                "overflow",
                "access_control",
                "flash_loan",
                "price_manipulation",
                "front_running",
                "sandwich_attack"
            ]
        )

        # Database Configuration
        self.db_config = DBConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            database=os.getenv("DB_NAME", "defi_analyzer"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            pool_size=20,
            max_overflow=10
        )

    def get_chain_config(self, chain_id: int) -> ChainConfig:
        """Get configuration for a specific chain"""
        if chain_id not in self.chains:
            raise ValueError(f"Configuration for chain ID {chain_id} not found")
        return self.chains[chain_id]

    def get_all_chain_ids(self) -> list:
        """Get list of all supported chain IDs"""
        return list(self.chains.keys())

    def is_chain_supported(self, chain_id: int) -> bool:
        """Check if a chain ID is supported"""
        return chain_id in self.chains

# Create a global config instance
config = Config()