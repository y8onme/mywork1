# src/utils/config/eth_config.py

import os
from .base_config import ChainConfig

def get_eth_config() -> ChainConfig:
    return ChainConfig(
        rpc_url=os.getenv("ETH_RPC_URL"),
        chain_id=1,
        explorer_api_key=os.getenv("ETHERSCAN_API_KEY"),
        explorer_url="https://api.etherscan.io/api",
        flash_loan_providers={
            "aave_v2": "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
            "aave_v3": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
            "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
            "dydx": "0x1E0447b19BB6EcFdAe1e4AE1694b0C3659614e4e",
            "maker": "0x9759A6Ac90977b93B58547b4A71c78317f391A28"
        },
        dex_addresses={
            "uniswap_v2_router": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            "uniswap_v3_router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "uniswap_v3_factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
            "sushiswap_router": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
            "curve_router": "0x99a58482BD75cbab83b27EC03CA68fF489b5788f",
            "balancer_vault": "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
        },
        lending_protocols={
            "aave_v2": "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",
            "aave_v3": "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2",
            "compound_v2": "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B",
            "compound_v3": "0xc3d688B66703497DAA19211EEdff47f25384cdc3",
            "maker": "0x9759A6Ac90977b93B58547b4A71c78317f391A28"
        },
        block_time=12.0,
        confirmation_blocks=12,
        native_token="ETH",
        wrapped_native="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        stable_coins=[
            "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
            "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
            "0x4Fabb145d64652a948d72533023f6E7A623C7C53",  # BUSD
            "0x956F47F50A910163D8BF957Cf5846D573E7f87CA"   # FEI
        ],
        bridge_contracts={
            "arbitrum": "0x8315177aB297bA92A06054cE80a67Ed4DBd7ed3a",
            "optimism": "0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1",
            "polygon": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
            "wormhole": "0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B",
            "stargate": "0x8731d54E9D02c286767d56ac03e8037C07e01e98",
            "hop": "0xb8901acB165ed027E32754E0FFe830802919727f"
        },
        oracle_addresses={
            "chainlink": "0x47Fb2585D2C56Fe188D0E6ec628a38b74fCeeeDf",
            "uniswap_v3": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
            "band": "0xDA7a001b254CD22e46d3eAB04d937489c93174C3"
        },
        amm_pools={
            "uniswap_v2": [
                "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc",  # USDC-ETH
                "0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852"   # ETH-USDT
            ],
            "uniswap_v3": [
                "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8",  # USDC-ETH 0.3%
                "0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36"   # ETH-USDT 0.3%
            ]
        },
        lending_pools={
            "aave_v2": [
                "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9",  # LendingPool
                "0x057835Ad21a177dbdd3090bB1CAE03EaCF78Fc6d"   # WETHGateway
            ],
            "compound": [
                "0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B",  # Comptroller
                "0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5"   # cETH
            ]
        },
        yield_farms={
            "convex": "0xF403C135812408BFbE8713b5A23a04b3D48AAE31",
            "yearn": "0x50c1a2eA0a861A967D9d0FFE2AE4012c2E053804"
        },
        nft_marketplaces={
            "opensea": "0x00000000006c3852cbEf3e08E8dF289169EdE581",
            "blur": "0x000000000000Ad05Ccc4F10045630fb830B95127"
        },
        cross_chain_bridges={
            "arbitrum": {
                "gateway": "0x8315177aB297bA92A06054cE80a67Ed4DBd7ed3a",
                "router": "0x72Ce9c846789fdB6fC1f34aC4AD25Dd9ef7031ef"
            },
            "optimism": {
                "gateway": "0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1",
                "router": "0x0000000000000000000000000000000000000000"
            }
        }
    )