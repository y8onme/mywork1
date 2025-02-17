# src/utils/config/polygon_config.py

import os
from .base_config import ChainConfig

def get_polygon_config() -> ChainConfig:
    return ChainConfig(
        rpc_url=os.getenv("POLYGON_RPC_URL"),
        chain_id=137,
        explorer_api_key=os.getenv("POLYGONSCAN_API_KEY"),
        explorer_url="https://api.polygonscan.com/api",
        flash_loan_providers={
            "aave_v2": "0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf",
            "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
            "quickswap": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"
        },
        dex_addresses={
            "quickswap": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
            "sushiswap": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
            "uniswap_v3": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            "curve": "0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf",
            "balancer": "0xBA12222222228d8Ba445958a75a0704d566BF2C8"
        },
        lending_protocols={
            "aave_v2": "0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf",
            "aave_v3": "0x794a61358D6845594F94dc1DB02A252b5b4814aD",
            "cream": "0x20CA53E2395FA571798623F1cFBD11Fe2C114c24"
        },
        block_time=2.0,
        confirmation_blocks=256,
        native_token="MATIC",
        wrapped_native="0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",  # WMATIC
        stable_coins=[
            "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",  # USDT
            "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",  # USDC
            "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",  # DAI
            "0x9C9e5fD8bbc25984B178FdCE6117Defa39d2db39"   # BUSD
        ],
        bridge_contracts={
            "polygon_pos": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
            "wormhole": "0x7A4B5a56256163F07b2C80A7cA55aBE66c4ec4d7",
            "stargate": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
            "hop": "0x553bC791D746767166fA3888432038193cEED5E2"
        },
        oracle_addresses={
            "chainlink": "0xAB594600376Ec9fD91F8e885dADF0CE036862dE0",
            "quickswap": "0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23",
            "band": "0xDA7a001b254CD22e46d3eAB04d937489c93174C3"
        },
        amm_pools={
            "quickswap": [
                "0x853Ee4b2A13f8a742d64C8F088bE7bA2131f670d",  # USDC-MATIC
                "0x604229c960e5CACF2aaEAc8Be68Ac07BA9dF81c3"   # USDT-MATIC
            ],
            "sushiswap": [
                "0xc2755915a85C6f6c1C0F3a86ac8C058F11Caa9C9",  # USDC-WETH
                "0xc2755915a85C6f6c1C0F3a86ac8C058F11Caa9C9"   # WMATIC-WETH
            ]
        },
        lending_pools={
            "aave_v2": [
                "0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf",  # LendingPool
                "0x1e4b7A6b903680eab0c5dAbcb8fD429cD2a9598c"   # WETHGateway
            ],
            "aave_v3": [
                "0x794a61358D6845594F94dc1DB02A252b5b4814aD",  # Pool
                "0x794a61358D6845594F94dc1DB02A252b5b4814aD"   # PoolAddressesProvider
            ]
        },
        yield_farms={
            "quickswap": "0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23",
            "sushiswap": "0x0769fd68dFb93167989C6f7254cd0D766Fb2841F"
        },
        nft_marketplaces={
            "opensea": "0x207Fa8Df3a17D96Ca7EA4f2893fcdCb78a304101",
            "nftrade": "0x7f462B9c8c0D3b9C9C994b7c147D4D5dE5e884E3"
        },
        cross_chain_bridges={
            "polygon_pos": {
                "root_chain": "0x86E4Dc95c7FBdBf52e33D563BbDB00823894C287",
                "state_sender": "0x28e4F3a7f651294B9564800b2D01f35189A5bFbE"
            },
            "wormhole": {
                "gateway": "0x7A4B5a56256163F07b2C80A7cA55aBE66c4ec4d7",
                "router": "0x3ee18B2214AFF97000D974cf647E7C347E8fa585"
            }
        }
    )