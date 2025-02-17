# src/utils/config/base_chain_config.py

import os
from .base_config import ChainConfig

def get_base_config() -> ChainConfig:
    return ChainConfig(
        rpc_url=os.getenv("BASE_RPC_URL"),
        chain_id=8453,
        explorer_api_key=os.getenv("BASESCAN_API_KEY"),
        explorer_url="https://api.basescan.org/api",
        flash_loan_providers={
            "aerodrome": "0x9A172A563BC0cBE432A488B6C9A061C7c4E7E5e9",
            "baseswap": "0x327Df1E6de05895d2ab08513aaDD9313Fe505d86",
            "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
            "sushiswap": "0x8B396ddF906D552b2F98AE36b4cE411663Bb9FDc"
        },
        dex_addresses={
            "aerodrome": "0x9A172A563BC0cBE432A488B6C9A061C7c4E7E5e9",
            "baseswap": "0x327Df1E6de05895d2ab08513aaDD9313Fe505d86",
            "uniswap_v3": "0x03A520b32C04BF3bE5F46662355D666079DD7667",
            "sushiswap": "0x8B396ddF906D552b2F98AE36b4cE411663Bb9FDc",
            "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
        },
        lending_protocols={
            "moonwell": "0xfBb21d0380beE3312B33c4353c8936a0F13EF26C",
            "aave_v3": "0x43955b0899Ab7232E3a454cf84AedD22Ad46FD33",
            "compound": "0x45939657d1CA34A8FA39A924B71D28Fe8431e581"
        },
        block_time=2.0,
        confirmation_blocks=64,
        native_token="ETH",
        wrapped_native="0x4200000000000000000000000000000000000006",  # WETH
        stable_coins=[
            "0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA",  # USDC
            "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",  # DAI
            "0x4A3A6Dd60A34bB2Aba60D73B4C88315E9CeB6A3D",  # USDT
            "0xbf1aeA8670D2528E08334083616dD9C5F3B087aE"   # MAI
        ],
        bridge_contracts={
            "base_bridge": "0x49048044D57e1C92A77f79988d21Fa8fAF74E97e",
            "layerzero": "0xb6319cC6c8c27A8F5dAF0dD3DF91EA35C4720dd7",
            "across": "0x09aea4b2242abC8bb4BB78D537A67a245A7bEC64",
            "hop": "0x3666f603Cc164936C1b87e207F36BEBa4AC5f18a"
        },
        oracle_addresses={
            "chainlink": "0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70",
            "uniswap_v3": "0x3A9690f4c9a2eaE6F6E6b159f2887E9e543f7A41",
            "pyth": "0x8250f4aF4B972684F7b336503E2D6dFeDeB1487a"
        },
        amm_pools={
            "aerodrome": [
                "0x0D7c4b40018969f81750D0A164c3839A77353EFB",  # USDC-ETH
                "0x06519DD5278A3E19fe1fF6994F66a2DC1C34d8c7"   # USDC-USDbC
            ],
            "baseswap": [
                "0x7Fb35b3967798c4Fd1f0E1Cdc1Ac58c484c4a42B",  # USDC-ETH
                "0x4C36388Be6F416A29C8d8Eee81C771cE6bE14B18"   # USDC-USDbC
            ]
        },
        lending_pools={
            "moonwell": [
                "0xfBb21d0380beE3312B33c4353c8936a0F13EF26C",  # Comptroller
                "0xE8F4dF45E4Ea7b4bDE0C5C0F46E11b6bAa2107C8"   # WETH Market
            ],
            "aave_v3": [
                "0x43955b0899Ab7232E3a454cf84AedD22Ad46FD33",  # Pool
                "0x0D1Fe8eAdb0a3e44C4Cc9D73De8dA50C1E475832"   # PoolAddressesProvider
            ]
        },
        yield_farms={
            "aerodrome": "0x420DD381b31aEf6683db6B902084cB0FFEe5a86C",
            "baseswap": "0x5546B5B4C56F0463cB14BC4F21E6F587224Cc653",
            "beefy": "0x4E8B0cF0F2298e24E91776d21471C7F65558Bc88"
        },
        nft_marketplaces={
            "basepaint": "0x8462E4412218eF8e0E1642D6292fcB67CdD7eE32",
            "mintbase": "0x0Bf5c22D5DF6e7B8DAe50bbA8F7E20D6Cd0F7d00"
        },
        cross_chain_bridges={
            "base_bridge": {
                "gateway": "0x49048044D57e1C92A77f79988d21Fa8fAF74E97e",
                "l1_bridge": "0x3154Cf16ccdb4C6d922629664174b904d80F2C35"
            },
            "layerzero": {
                "endpoint": "0xb6319cC6c8c27A8F5dAF0dD3DF91EA35C4720dd7",
                "router": "0x45f1A95A4D3f3836523F5c83673c797f4d4d263B"
            }
        }
    )