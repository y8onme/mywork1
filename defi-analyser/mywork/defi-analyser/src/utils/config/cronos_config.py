# src/utils/config/cronos_config.py

import os
from .base_config import ChainConfig

def get_cronos_config() -> ChainConfig:
    return ChainConfig(
        rpc_url=os.getenv("CRONOS_RPC_URL"),
        chain_id=25,
        explorer_api_key=os.getenv("CRONOSCAN_API_KEY"),
        explorer_url="https://api.cronoscan.com/api",
        flash_loan_providers={
            "vvs": "0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23",
            "mm_finance": "0x145863Eb42Cf62847A6Ca784e6416C1682b1b2Ae",
            "crodex": "0xe44Fd7fCb2b1581822D0c862B68222998a0c299a",
            "dark_crypto": "0x3f6C9dC72B69f1B1A65B9e46E416dDB9F6E5d767"
        },
        dex_addresses={
            "vvs": "0x145863Eb42Cf62847A6Ca784e6416C1682b1b2Ae",
            "mm_finance": "0x145677FC4d9b8F19B5D56d1820c48e0443049a30",
            "crodex": "0xe44Fd7fCb2b1581822D0c862B68222998a0c299a",
            "crystl": "0x145677FC4d9b8F19B5D56d1820c48e0443049a30",
            "dark_auto": "0x6C6fB22bd23eE36E7Dc9527BCb2d5CA5B9a54752"
        },
        lending_protocols={
            "tectonic": "0xb3831584acb95ED9cCb0C11f677B5AD01DeaeEc0",
            "mimas": "0x7d3C61Db7515D76bF95f66A8B6897C2931764492",
            "annex": "0x3F6C9dC72B69f1B1A65B9e46E416dDB9F6E5d767"
        },
        block_time=6.0,
        confirmation_blocks=10,
        native_token="CRO",
        wrapped_native="0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23",  # WCRO
        stable_coins=[
            "0x66e428c3f67a68878562e79A0234c1F83c208770",  # USDT
            "0xc21223249CA28397B4B6541dfFaEcC539BfF0c59",  # USDC
            "0xF2001B145b43032AAF5Ee2884e456CCd805F677D",  # DAI
            "0x6aB6d61428fde76768D7b45D8BFeec19c6eF91A8"   # MAI
        ],
        bridge_contracts={
            "celer": "0x374B8a9f3eC5eB2D97EcA84Ea3176259a458F555",
            "multichain": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
            "axelar": "0x4F4495243837681061C4743b74B3eEdf548D56A5",
            "layerzero": "0x9740FF91F1985D8d2B71494aE1A2f723bb3Ed9E4"
        },
        oracle_addresses={
            "chainlink": "0x0625aE3B6B31F92A58b56c665249f2E6B10784F9",
            "band": "0x40FE45E6Aa55536E474B3aAA1A04cA5320B90b5B",
            "dia": "0xf35E127aC7087A8361C2F8aE4Ff707E74f1433Ee"
        },
        amm_pools={
            "vvs": [
                "0x814920D1b8007207db6cB5a2dD92bF0b082BDBa1",  # USDC-CRO
                "0x3d2180DB9E1B909f35C398BC39EF36108C0FC8c3"   # USDT-CRO
            ],
            "mm_finance": [
                "0x5F3455505A35C534cd8364E56b88Fdb7B5963eff",  # USDC-CRO
                "0x39cC0E14795A8e6e9D02A21091b81FE0d61D82f9"   # USDT-CRO
            ]
        },
        lending_pools={
            "tectonic": [
                "0xb3831584acb95ED9cCb0C11f677B5AD01DeaeEc0",  # Comptroller
                "0x46c02949D8CA3AF76eE81361C897d3a130AD23E4"   # WCRO Market
            ],
            "mimas": [
                "0x7d3C61Db7515D76bF95f66A8B6897C2931764492",  # Comptroller
                "0x8379BAA817aE5F6BBB5aaF3a1785A2917E1D2954"   # WCRO Market
            ]
        },
        yield_farms={
            "vvs": "0xDccd6455AE04b03d785F12196B492b18129564bc",
            "mm_finance": "0x6bE34986Fdd1A91e4634eb6b9F8017439b7b5EDc",
            "dark_auto": "0x6C6fB22bd23eE36E7Dc9527BCb2d5CA5B9a54752"
        },
        nft_marketplaces={
            "minted": "0x2E1873cb0D45285E7592B6A4B674177C30027C46",
            "ebisu": "0x95772E5D8F654A4B1Cf7C9d8936f6D3A0B61e956"
        },
        cross_chain_bridges={
            "celer": {
                "bridge": "0x374B8a9f3eC5eB2D97EcA84Ea3176259a458F555",
                "message_bus": "0x5a5a30aB3e5ddf56448DC33ed92d9E787673A44E"
            },
            "multichain": {
                "router": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
                "anyswap_router": "0x1CCa3EC2E7EAd00B16AA7e16A5D25A4Dd7B5b7B5"
            }
        }
    )