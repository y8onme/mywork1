# src/utils/config/fantom_config.py

import os
from .base_config import ChainConfig

def get_fantom_config() -> ChainConfig:
    return ChainConfig(
        rpc_url=os.getenv("FTM_RPC_URL"),
        chain_id=250,
        explorer_api_key=os.getenv("FTMSCAN_API_KEY"),
        explorer_url="https://api.ftmscan.com/api",
        flash_loan_providers={
            "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "spookyswap": "0xd42a19f5c0b9aF549CC1945eBB6C3E004A66fBF7",
            "spiritswap": "0x2b4C76d0dc16BE1C31D4C1DC53bF9B45987Fc75c",
            "solidly": "0x777777777777777777777777777777777777777"
        },
        dex_addresses={
            "spookyswap": "0xF491e7B69E4244ad4002BC14e878a34207E38c29",
            "spiritswap": "0x16327E3FbDaCA3bcF7E38F5Af2599D2DDc33aE52",
            "solidly": "0x777777777777777777777777777777777777777",
            "curve": "0x0994206dfE8De6Ec6920FF4D779B0d950605Fb53",
            "sushiswap": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"
        },
        lending_protocols={
            "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "geist": "0x9FAD24f572045c7869117160A571B2e50b10d068",
            "cream": "0x4A6e91335dE92C89441777f7A0DaB5a3D1dCE38d"
        },
        block_time=1.0,
        confirmation_blocks=5,
        native_token="FTM",
        wrapped_native="0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83",  # WFTM
        stable_coins=[
            "0x04068DA6C83AFCFA0e13ba15A6696662335D5B75",  # USDC
            "0x049d68029688eAbF473097a2fC38ef61633A3C7A",  # USDT
            "0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E",  # DAI
            "0xdc301622e621166BD8E82f2cA0A26c13Ad0BE355"   # FRAX
        ],
        bridge_contracts={
            "anyswap": "0x1CCa3EC2E7EAd00B16AA7e16A5D25A4Dd7B5b7B5",
            "multichain": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
            "celer": "0x374B8a9f3eC5eB2D97EcA84Ea3176259a458F555",
            "synapse": "0xF42dBcf004a93ae6D5922282B767E598A8cf8C17"
        },
        oracle_addresses={
            "chainlink": "0xf4766552D15AE4d256Ad41B6cf2933482B0680dc",
            "band": "0x56E2898E0ceFF0D1222827759B56B28Ad812f92F"
        },
        amm_pools={
            "spookyswap": [
                "0x2b4C76d0dc16BE1C31D4C1DC53bF9B45987Fc75c",  # USDC-FTM
                "0x5965E53aa80a0bcF1CD6dbDd72e6A9b2AA047410"   # USDT-FTM
            ],
            "spiritswap": [
                "0x30748322B6E34545DBe0788C421886AEB5297789",  # USDC-FTM
                "0x0d94584d339f43E8E9B8A7c665d9Be91A3eC8751"   # USDT-FTM
            ]
        },
        lending_pools={
            "aave_v3": [
                "0x794a61358D6845594F94dc1DB02A252b5b4814aD",  # Pool
                "0xa97684ead0e402dC232d5A977953DF7ECBaB3CDb"   # PoolAddressesProvider
            ],
            "geist": [
                "0x9FAD24f572045c7869117160A571B2e50b10d068",  # LendingPool
                "0x22F9dCF4647084d6C31b2765F6910cd85C178C18"   # AddressProvider
            ]
        },
        yield_farms={
            "spookyswap": "0x18b4f774fdC7BF685daeeF66c2990b1dDd9ea6aD",
            "spiritswap": "0x9083EA3756BDE6Ee6f27a6e996806FBD37F6F093"
        },
        nft_marketplaces={
            "paintswap": "0x85E139B042827C6e1e559BAD620f0F77E1532186",
            "artion": "0x6E382b0f7E1086EA0A7561b32F66AB5D7B46E8E8"
        },
        cross_chain_bridges={
            "multichain": {
                "router": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
                "anyswap_router": "0x1CCa3EC2E7EAd00B16AA7e16A5D25A4Dd7B5b7B5"
            },
            "celer": {
                "bridge": "0x374B8a9f3eC5eB2D97EcA84Ea3176259a458F555",
                "message_bus": "0x5a5a30aB3e5ddf56448DC33ed92d9E787673A44E"
            }
        }
    )