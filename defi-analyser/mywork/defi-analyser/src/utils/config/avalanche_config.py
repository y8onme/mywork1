# src/utils/config/avalanche_config.py

import os
from .base_config import ChainConfig

def get_avalanche_config() -> ChainConfig:
    return ChainConfig(
        rpc_url=os.getenv("AVAX_RPC_URL"),
        chain_id=43114,
        explorer_api_key=os.getenv("SNOWTRACE_API_KEY"),
        explorer_url="https://api.snowtrace.io/api",
        flash_loan_providers={
            "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "traderjoe": "0x60aE616a2155Ee3d9A68541Ba4544862310933d4",
            "benqi": "0x2b2C81e08f1Af8835a78Bb2A90AE924ACE0eA4bE",
            "platypus": "0x66357dCaCe80431aee0A7507e2E361B7e2402370"
        },
        dex_addresses={
            "traderjoe": "0x60aE616a2155Ee3d9A68541Ba4544862310933d4",
            "pangolin": "0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106",
            "curve": "0x0994206dfE8De6Ec6920FF4D779B0d950605Fb53",
            "gmx": "0x5F719c2F1095F7B9fc68a68e35B51194f4b6abe8",
            "sushiswap": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
        },
        lending_protocols={
            "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "benqi": "0x2b2C81e08f1Af8835a78Bb2A90AE924ACE0eA4bE",
            "vector": "0x825a47C699F6D5Ed97DA97D2619e47d8d10cA7d8"
        },
        block_time=2.0,
        confirmation_blocks=12,
        native_token="AVAX",
        wrapped_native="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",  # WAVAX
        stable_coins=[
            "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",  # USDT
            "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",  # USDC
            "0xd586E7F844cEa2F87f50152665BCbc2C279D8d70",  # DAI
            "0x19860CCB0A68fd4213aB9D8266F7bBf05A8dDe98"   # BUSD
        ],
        bridge_contracts={
            "avalanche_bridge": "0x8F2C146bE2763D7535921D1f6fA24911491566Bb",
            "stargate": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
            "celer": "0x5427FEFA711Eff984124bFBB1AB6fbf5E3DA1820",
            "synapse": "0x0EF812f4c68DC84c22A4821EF30BA2ffAB9C2f3A"
        },
        oracle_addresses={
            "chainlink": "0x0A77230d17318075983913bC2145DB16C7366156",
            "traderjoe": "0x2E2969F6A77B29E1Cc5c7474412f34A4F950690E",
            "band": "0x8A6567e91937Aa0EB4F29AF025C5c6f6c8ADd1c4"
        },
        amm_pools={
            "traderjoe": [
                "0x862905a82382Db9405A82D3E95D1787dB1AC8783",  # USDC-AVAX
                "0xf4003F4efBE8691B60249E6afbD307aBE7758adb"   # USDT-AVAX
            ],
            "pangolin": [
                "0xf4003F4efBE8691B60249E6afbD307aBE7758adb",  # USDC-AVAX
                "0x5Fc70cF6A4A858Cf4124013047e408367EBa1ace"   # USDT-AVAX
            ]
        },
        lending_pools={
            "aave_v3": [
                "0x794a61358D6845594F94dc1DB02A252b5b4814aD",  # Pool
                "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb"   # PoolAddressesProvider
            ],
            "benqi": [
                "0x2b2C81e08f1Af8835a78Bb2A90AE924ACE0eA4bE",  # Comptroller
                "0x5C0401e81Bc07Ca70fAD469b451682c0d747Ef1c"   # QiAVAX
            ]
        },
        yield_farms={
            "traderjoe": "0x188bED1968b795d5c9022F6a0bb5931Ac4c18F00",
            "pangolin": "0x1f806f7C8dED893fd3caE279191ad7Aa3798E928"
        },
        nft_marketplaces={
            "joepegs": "0x3D26cefE5fAE96EA2F22F8c99B1AcD31731Af298",
            "kalao": "0x7C2c3405D7E9e358a3958D5B49A8B728420A5025"
        },
        cross_chain_bridges={
            "avalanche_bridge": {
                "gateway": "0x8F2C146bE2763D7535921D1f6fA24911491566Bb",
                "router": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd"
            },
            "stargate": {
                "router": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
                "factory": "0x808d7c71ad2ba3FA531b068a2417C63106BC0949"
            }
        }
    )