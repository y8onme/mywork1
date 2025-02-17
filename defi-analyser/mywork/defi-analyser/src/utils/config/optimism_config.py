# src/utils/config/optimism_config.py

import os
from .base_config import ChainConfig

def get_optimism_config() -> ChainConfig:
    return ChainConfig(
        rpc_url=os.getenv("OPTIMISM_RPC_URL"),
        chain_id=10,
        explorer_api_key=os.getenv("OPTIMISM_API_KEY"),
        explorer_url="https://api-optimistic.etherscan.io/api",
        flash_loan_providers={
            "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "velodrome": "0x9c12939390052919aF3155f41Bf4160Fd3666A6f",
            "beethoven": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
            "synthetix": "0x8700dAec35aF8Ff88c16BdF0418774CB3D7599B4"
        },
        dex_addresses={
            "velodrome": "0x9c12939390052919aF3155f41Bf4160Fd3666A6f",
            "uniswap_v3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "curve": "0x0994206dfE8De6Ec6920FF4D779B0d950605Fb53",
            "beethoven": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
            "sushiswap": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
        },
        lending_protocols={
            "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "exactly": "0xBd6957c6F5d1DD6B96793756622992FE8C8336c9",
            "granary": "0x8E7e9eA9023B81457Ae7E6D2a51b003D421E5408"
        },
        block_time=2.0,
        confirmation_blocks=64,
        native_token="ETH",
        wrapped_native="0x4200000000000000000000000000000000000006",  # WETH
        stable_coins=[
            "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",  # USDT
            "0x7F5c764cBc14f9669B88837ca1490cCa17c31607",  # USDC
            "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",  # DAI
            "0x2E3D870790dC77A83DD1d18184Acc7439A53f475"   # FRAX
        ],
        bridge_contracts={
            "optimism_bridge": "0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1",
            "stargate": "0x4200000000000000000000000000000000000010",
            "hop": "0xb8901acB165ed027E32754E0FFe830802919727f",
            "across": "0x4D9079Bb4165aeb4084c526a32695dCfd2F77381"
        },
        oracle_addresses={
            "chainlink": "0x371EAD81c9102C9BF4874A9075FFFf170F2Ee389",
            "uniswap_v3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
            "velodrome": "0x43c3f2d0AA0eC987731A3e0B8c3C8DD0D1A4e839"
        },
        amm_pools={
            "velodrome": [
                "0x79c912FEF520be002c2B6e57EC4324e260f38E50",  # USDC-ETH
                "0x0493Bf8b6DBB159Ce2Db2E0E8403E753Abd1235b"   # USDT-ETH
            ],
            "uniswap_v3": [
                "0x85149247691df622eaF1a8Bd0CaFd40BC45154a9",  # USDC-ETH 0.05%
                "0x03aF20bDAaFfB4cC0A521796a223f7D85e2aAc31"   # USDT-ETH 0.05%
            ]
        },
        lending_pools={
            "aave_v3": [
                "0x794a61358D6845594F94dc1DB02A252b5b4814aD",  # Pool
                "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb"   # PoolAddressesProvider
            ],
            "exactly": [
                "0xBd6957c6F5d1DD6B96793756622992FE8C8336c9",  # Market
                "0x3F0A4A0F0f9d9667148C1658Fc53F20830826704"   # MarketController
            ]
        },
        yield_farms={
            "velodrome": "0x3c8B650257cFb5f272f799F5e2b4e65093a11a05",
            "beethoven": "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
        },
        nft_marketplaces={
            "quixotic": "0x3Eaf3d0F46D47C46BE37C6CbF7d75C8ec53A0ffB",
            "tofu": "0x7F5E7930a5Fc7Fed72C28a3BD8A45064bA7F149d"
        },
        cross_chain_bridges={
            "optimism_bridge": {
                "gateway": "0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1",
                "l1_bridge": "0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1"
            },
            "stargate": {
                "router": "0x4200000000000000000000000000000000000010",
                "factory": "0x55bDb4164D28FBaF0898e0eF14a589ac09Ac9970"
            }
        }
    )