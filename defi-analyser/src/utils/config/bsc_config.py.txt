# src/utils/config/bsc_config.py

import os
from .base_config import ChainConfig

def get_bsc_config() -> ChainConfig:
    return ChainConfig(
        rpc_url=os.getenv("BSC_RPC_URL"),
        chain_id=56,
        explorer_api_key=os.getenv("BSCSCAN_API_KEY"),
        explorer_url="https://api.bscscan.com/api",
        flash_loan_providers={
            "pancakeswap": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
            "venus": "0xfD36E2c2a6789Db23113685031d7F16329158384",
            "biswap": "0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8",
            "apeswap": "0xcF0feBd3f17CEf5b47b0cD257aCf6025c5BFf3b7"
        },
        dex_addresses={
            "pancakeswap_v2": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
            "biswap": "0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8",
            "apeswap": "0xcF0feBd3f17CEf5b47b0cD257aCf6025c5BFf3b7",
            "mdex": "0x7DAe51BD3E3376B8c7c4900E9107f12Be3AF1bA8",
            "babyswap": "0x325E343f1dE602396E256B67eFd1F61C3A6B38Bd"
        },
        lending_protocols={
            "venus": "0xfD36E2c2a6789Db23113685031d7F16329158384",
            "cream": "0x589de0f0ccf905477646599bb3e5c622c84cc0ba",
            "alpaca": "0xb23b6c1800659f7d2b6aa8f847ed76cba494e8c5"
        },
        block_time=3.0,
        confirmation_blocks=15,
        native_token="BNB",
        wrapped_native="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WBNB
        stable_coins=[
            "0x55d398326f99059fF775485246999027B3197955",  # USDT
            "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",  # USDC
            "0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3",  # DAI
            "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"   # BUSD
        ],
        bridge_contracts={
            "wormhole": "0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B",
            "anyswap": "0xd1C5966f9F5Ee6881Ff6610f51DB1B0B6d2F7d50",
            "stargate": "0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8",
            "celer": "0x5427FEFA711Eff984124bFBB1AB6fbf5E3DA1820"
        },
        oracle_addresses={
            "chainlink": "0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE",
            "pancakeswap": "0xB6064eD41d4f67e353768aA239cA86f4F73665a1",
            "band": "0xDA7a001b254CD22e46d3eAB04d937489c93174C3"
        },
        amm_pools={
            "pancakeswap": [
                "0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16",  # BUSD-BNB
                "0x7EFaEf62fDdCCa950418312c6C91Aef321375A00"   # USDT-BUSD
            ],
            "biswap": [
                "0x2b30c317ceDFb554Ec525F85E79Ac971fE920714",  # USDT-BSW
                "0xaCAac9311b0096E04Dfe96b6D87dec867d3883Dc"   # BSW-BNB
            ]
        },
        lending_pools={
            "venus": [
                "0xfD36E2c2a6789Db23113685031d7F16329158384",  # Comptroller
                "0xA07c5b74C9B40447a954e1466938b865b6BBea36"   # vBNB
            ],
            "alpaca": [
                "0xb23b6c1800659f7d2b6aa8f847ed76cba494e8c5",  # Vault
                "0x158Da805682BdC8ee32d52833aD41E74bb951E59"   # Controller
            ]
        },
        yield_farms={
            "pancakeswap": "0xa5f8C5Dbd5F286960b9d90548680aE5ebFf07652",
            "biswap": "0xDbc1A13490deeF9c3C12b44FE77b503c1B061739"
        },
        nft_marketplaces={
            "pancake_nft": "0x17539cCa21C7933Df5c980172d22659B8C345C5A",
            "nftkey": "0x48F7068372A0e85c08e0BED5847495233B462187"
        },
        cross_chain_bridges={
            "wormhole": {
                "gateway": "0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B",
                "router": "0x3ee18B2214AFF97000D974cf647E7C347E8fa585"
            },
            "anyswap": {
                "router": "0xd1C5966f9F5Ee6881Ff6610f51DB1B0B6d2F7d50",
                "gateway": "0xC10Ef9F491C9B59f936957026020C321651ac078"
            }
        }
    )