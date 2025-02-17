# src/utils/config/zksync_config.py

import os
from .base_config import ChainConfig

def get_zksync_config() -> ChainConfig:
    return ChainConfig(
        rpc_url=os.getenv("ZKSYNC_RPC_URL"),
        chain_id=324,
        explorer_api_key=os.getenv("ZKSYNC_API_KEY"),
        explorer_url="https://api.zksync.io/api",
        flash_loan_providers={
            "syncswap": "0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295",
            "mute": "0x8B791913eB07C32779a16750e3868aA8495F5964",
            "velocore": "0x46dbd39e26a56778d88507d7aEC6967108C0BD26",
            "spacefi": "0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d"
        },
        dex_addresses={
            "syncswap": "0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295",
            "mute": "0x8B791913eB07C32779a16750e3868aA8495F5964",
            "velocore": "0x46dbd39e26a56778d88507d7aEC6967108C0BD26",
            "spacefi": "0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d",
            "maverick": "0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4"
        },
        lending_protocols={
            "reactorfusion": "0x23848c28Af1C3A5dB0026264318E0F5B8a3646B8",
            "zerolend": "0x058F7D7E9351E736006C2Bc61473Ea73250F3F8F",
            "basilisk": "0x1BbD33384869b30A323e15868Ce46013C82B86FB"
        },
        block_time=1.0,
        confirmation_blocks=32,
        native_token="ETH",
        wrapped_native="0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91",  # WETH
        stable_coins=[
            "0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4",  # USDC
            "0x493257fD37EDB34451f62EDf8D2a0C418852bA4C",  # USDT
            "0x012B3a7C8727E8bA2534e3A833436D6bBE399e98",  # DAI
            "0xBBeB516fb02a01611cBBE0453Fe3c580D7281011"   # FRAX
        ],
        bridge_contracts={
            "zksync_bridge": "0x32400084C286CF3E17e7B677ea9583e60a000324",
            "layerzero": "0x9b896c0e23220469C7AE69cb4BbAE391eAa4C8da",
            "stargate": "0x1C3D7326f104F58B51F12A9749c4d21AeCd62C56",
            "orbiter": "0x80C67432656d59144cEFf962E8fAF8926599bCF8"
        },
        oracle_addresses={
            "redstone": "0x0771eC6D6B3cA7C40D96F3d93C2399BF24761960",
            "pyth": "0xf087c864AEccFb6A2Bf1Af6A0382B0d0f6c5D834",
            "dia": "0xD56e4eAb23cb81f43168F9F45211Eb027b9aC7cc"
        },
        amm_pools={
            "syncswap": [
                "0x80115c708E12eDd42E504c1cD52Aea96C547c05c",  # USDC-ETH
                "0xf31e0449Fb431Aa9Ad3bEA6956d6EA9c23C0b776"   # USDT-ETH
            ],
            "mute": [
                "0x0E595bfcAfb552F83E25d24e8a383F88c1Ab48A4",  # USDC-ETH
                "0x8E1e3E95C0718E4D0fC0a1AFb41f6B4BdD26f27B"   # USDT-ETH
            ]
        },
        lending_pools={
            "reactorfusion": [
                "0x23848c28Af1C3A5dB0026264318E0F5B8a3646B8",  # LendingPool
                "0x4d9429246EA989C9CeE203B43F6d1C7D83e3B8F8"   # AddressProvider
            ],
            "zerolend": [
                "0x058F7D7E9351E736006C2Bc61473Ea73250F3F8F",  # Pool
                "0x4d9429246EA989C9CeE203B43F6d1C7D83e3B8F8"   # PoolAddressesProvider
            ]
        },
        yield_farms={
            "syncswap": "0x52E4019F5c59F906e766f8DA7C5F9cC142d9eA29",
            "mute": "0x0BE808376Ecb75A5CF9bB6D237d16cd37893d904",
            "velocore": "0x46dbd39e26a56778d88507d7aEC6967108C0BD26"
        },
        nft_marketplaces={
            "element": "0x47312450B3Ac8b5b8e247a6bB6d523e7605bDb60",
            "tofunft": "0x7C772eb18A0f96E749F95Cf5Ff228F7E48d7EF64"
        },
        cross_chain_bridges={
            "zksync_bridge": {
                "gateway": "0x32400084C286CF3E17e7B677ea9583e60a000324",
                "l1_bridge": "0x57891966931Eb4Bb6FB81430E6cE0A03AAbDe063"
            },
            "layerzero": {
                "endpoint": "0x9b896c0e23220469C7AE69cb4BbAE391eAa4C8da",
                "router": "0x0A3Bb08b3a15A19b4De82F8932B8c844C8a3404A"
            }
        }
    )