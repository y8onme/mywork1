# src/utils/config/arbitrum_config.py

import os
from .base_config import ChainConfig

def get_arbitrum_config() -> ChainConfig:
    return ChainConfig(
        rpc_url=os.getenv("ARBITRUM_RPC_URL"),
        chain_id=42161,
        explorer_api_key=os.getenv("ARBISCAN_API_KEY"),
        explorer_url="https://api.arbiscan.io/api",
        flash_loan_providers={
            "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "camelot": "0xc873fEcbd354f5A56E00E710B90EF4201db2448d",
            "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
            "gmx": "0x489ee077994B6658eAfA855C308275EAd8097C4A"
        },
        dex_addresses={
            "camelot": "0xc873fEcbd354f5A56E00E710B90EF4201db2448d",
            "sushiswap": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
            "uniswap_v3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "curve": "0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf",
            "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
            "gmx_router": "0xaBBc5F99639c9B6bCb58544ddf04EFA6802F4064"
        },
        lending_protocols={
            "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "radiant": "0x2032b9A8e9F7e76768CA9271003d3e43E1616B1F",
            "dforce": "0x8E7e9eA9023B81457Ae7E6D2a51b003D421E5408"
        },
        block_time=0.25,  # 250ms
        confirmation_blocks=64,
        native_token="ETH",
        wrapped_native="0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",  # WETH
        stable_coins=[
            "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",  # USDT
            "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",  # USDC
            "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",  # DAI
            "0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F"   # FRAX
        ],
        bridge_contracts={
            "arbitrum_bridge": "0x8315177aB297bA92A06054cE80a67Ed4DBd7ed3a",
            "stargate": "0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614",
            "hop": "0xC8A7c425f0928C261b2D1Cb09c31AA90cCb3c2A6",
            "across": "0xB88690461dDbaB6f04Dfad7df66B7725942FEb9C"
        },
        oracle_addresses={
            "chainlink": "0xb2A824043730FE05F3DA2efaFa1CBbe83fa548D6",
            "uniswap_v3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
            "gmx": "0x2d68011bcA022ed0E474264145F46CC4de96a002"
        },
        amm_pools={
            "camelot": [
                "0x84652bb2539513BAf36e225c930Fdd8eaa63CE27",  # USDC-ETH
                "0x7bB26c044D7AE59A3Ca47Db0A8BA27E957DbD2c9"   # USDT-ETH
            ],
            "uniswap_v3": [
                "0xC31E54c7a869B9FcBEcc14363CF510d1c41fa443",  # USDC-ETH 0.05%
                "0x641C00A822e8b671738d32a431a4Fb6074E5c79d"   # USDT-ETH 0.05%
            ]
        },
        lending_pools={
            "aave_v3": [
                "0x794a61358D6845594F94dc1DB02A252b5b4814aD",  # Pool
                "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb"   # PoolAddressesProvider
            ],
            "radiant": [
                "0x2032b9A8e9F7e76768CA9271003d3e43E1616B1F",  # LendingPool
                "0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1"   # LendingPoolAddressProvider
            ]
        },
        yield_farms={
            "gmx": "0x489ee077994B6658eAfA855C308275EAd8097C4A",
            "camelot": "0x6BC938abA940fB828D39Daa23A94dfc522120C11"
        },
        nft_marketplaces={
            "trove": "0x72E9D7C9f7812aB42Dfd0C6ba0C8B6E419B367E7",
            "stratos": "0x0Af85a5624D24E2C6e7Af3c0a0B102a28E36CeA3"
        },
        cross_chain_bridges={
            "arbitrum_bridge": {
                "gateway": "0x8315177aB297bA92A06054cE80a67Ed4DBd7ed3a",
                "router": "0x72Ce9c846789fdB6fC1f34aC4AD25Dd9ef7031ef"
            },
            "stargate": {
                "router": "0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614",
                "factory": "0x55bDb4164D28FBaF0898e0eF14a589ac09Ac9970"
            }
        }
    )