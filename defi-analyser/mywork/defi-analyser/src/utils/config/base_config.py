# src/utils/config/base_config.py

from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ChainConfig:
    rpc_url: str
    chain_id: int
    explorer_api_key: str
    explorer_url: str
    flash_loan_providers: Dict[str, str]  # Protocol name -> Contract address
    dex_addresses: Dict[str, str]  # DEX name -> Router address
    lending_protocols: Dict[str, str]  # Protocol name -> Contract address
    block_time: float
    confirmation_blocks: int
    native_token: str
    wrapped_native: str
    stable_coins: List[str]
    bridge_contracts: Dict[str, str]  # Bridge name -> Contract address
    oracle_addresses: Dict[str, str]  # Oracle name -> Contract address
    amm_pools: Dict[str, List[str]]  # Protocol -> List of pool addresses
    lending_pools: Dict[str, List[str]]  # Protocol -> List of pool addresses
    yield_farms: Dict[str, str]  # Protocol name -> Contract address
    nft_marketplaces: Dict[str, str]  # Marketplace name -> Contract address
    cross_chain_bridges: Dict[str, Dict[str, str]]  # Bridge name -> {gateway, router}

@dataclass
class AIConfig:
    model_path: str
    hidden_size: int
    learning_rate: float
    batch_size: int
    max_epochs: int
    early_stopping_patience: int
    transformer_layers: int
    attention_heads: int
    dropout_rate: float
    llm_api_key: str
    model_name: str
    temperature: float
    max_tokens: int

@dataclass
class SecurityConfig:
    min_confirmations: Dict[int, int]  # Chain ID -> Required confirmations
    max_gas_price: Dict[int, float]  # Chain ID -> Max gas price in gwei
    timeout_seconds: int
    max_retries: int
    blacklisted_contracts: List[str]
    security_checks: List[str]

@dataclass
class DBConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    pool_size: int
    max_overflow: int

class Config:
    def __init__(self):
        ...