from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from ..utils.config import config
from ..utils.logger import logger

@dataclass
class ChainAdapter:
    chain_id: int
    name: str
    rpc_url: str
    fork_block: Optional[int]
    flash_loan_providers: Dict[str, str]
    dex_routers: Dict[str, str]
    oracle_feeds: Dict[str, str]
    native_token: str
    block_time: int
    gas_token: str
    bridges: Dict[str, str]
    stablecoins: Dict[str, str]
    tokens: Dict[str, str]
    pool_factories: Dict[str, str]
    nft_marketplaces: Dict[str, str]
    mev_config: Dict[str, Any]
    amm_pools: Dict[str, str]
    lending_pools: Dict[str, str]
    yield_aggregators: Dict[str, str]
    liquid_staking: Dict[str, str]

class ChainAdapterFactory:
    """Factory for creating chain-specific adapters"""
    
    CHAIN_CONFIGS = {
        1: {  # Ethereum
            'name': 'Ethereum',
            'flash_loans': {
                'aave': '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',
                'balancer': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
                'maker': '0x1EB4CF3A948E7D72A198fe073cCb8C7a948cD853'
            },
            'dexes': {
                'uniswap_v2': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'sushiswap': '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
                'curve': '0x99a58482BD75cbab83b27EC03CA68fF489b5788f'
            },
            'block_time': 12,
            'native_token': 'ETH',
            'lending': {
                'aave_v2': '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',
                'aave_v3': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
                'compound_v2': '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B',
                'compound_v3': '0xc3d688B66703497DAA19211EEdff47f25384cdc3',
                'maker': '0x9759A6Ac90977b93B58547b4A71c78317f391A28'
            },
            'governance': {
                'compound': '0xc0Da02939E1441F497fd74F78cE7Decb17B66529',
                'aave': '0xEC568fffba86c094cf06b22134B23074DFE2252c',
                'uniswap': '0x408ED6354d4973f66138C91495F2f2FCbd8724C3',
                'maker': '0x9ef05f7f6deb616fd37ac3c959a2dDD25A54E4F5'
            },
            'bridges': {
                'wormhole': '0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B',
                'stargate': '0x8731d54E9D02c286767d56ac03e8037C07e01e98',
                'layerzero': '0x66A71Dcef29A0fFBDBE3c6a460a3B5BC225Cd675',
                'hop': '0x3E4a3a4796d16c0Cd582C382691998f7c06420B6',
                'across': '0x4D9079Bb4165aeb4084c526a32695dCfd2F77381'
            },
            'stablecoins': {
                'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
                'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
                'DAI': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
                'FRAX': '0x853d955aCEf822Db058eb8505911ED77F175b99e',
                'LUSD': '0x5f98805A4E8be255a32880FDeC7F6728C6568bA0'
            },
            'tokens': {
                'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
                'WBTC': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',
                'LINK': '0x514910771AF9Ca656af840dff83E8264EcF986CA',
                'UNI': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
                'AAVE': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9'
            },
            'pool_factories': {
                'uniswap_v2': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
                'uniswap_v3': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
                'sushiswap': '0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac',
                'curve': '0xB9fC157394Af804a3578134A6585C0dc9cc990d4'
            },
            'nft_marketplaces': {
                'opensea': '0x00000000006c3852cbEf3e08E8dF289169EdE581',
                'blur': '0x000000000000Ad05Ccc4F10045630fb830B95127',
                'x2y2': '0x74312363e45DCaBA76c59ec49a7Aa8A65a67EeD3',
                'sudoswap': '0x2B2e8cDA09bBA9660dCA5cB6233787738Ad68329'
            },
            'mev_config': {
                'flashbots_relay': 'https://relay.flashbots.net',
                'eden_relay': 'https://api.edennetwork.io/v1/bundle',
                'builder_registration': '0x00000000219ab540356cBB839Cbe05303d7705Fa',
                'searcher_registry': '0x7E9c2D47BA30C8Cb5C5F3af95F6797c33451c2cF'
            },
            'amm_pools': {
                'eth_usdc_univ3': '0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8',
                'eth_usdt_univ3': '0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36',
                'wbtc_eth_univ3': '0xCBCdF9626bC03E24f779434178A73a0B4bad62eD'
            },
            'lending_pools': {
                'aave_v3_pool': '0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2',
                'compound_v3_pool': '0xc3d688B66703497DAA19211EEdff47f25384cdc3',
                'spark_pool': '0xC13e21B648A5Ee794902342038FF3aDAB66BE987'
            },
            'yield_aggregators': {
                'yearn': '0x50c1a2eA0a861A967D9d0FFE2AE4012c2E053804',
                'convex': '0xF403C135812408BFbE8713b5A23a04b3D48AAE31',
                'curve_gauge': '0x2F50D538606Fa9EDD2B11E2446BEb18C9D5846bB'
            },
            'liquid_staking': {
                'lido': '0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84',
                'rocketpool': '0xae78736Cd615f374D3085123A210448E74Fc6393',
                'stakewise': '0xFe2e637202056d30016725477c5da089Ab0A043A'
            }
        },
        56: {  # BSC
            'name': 'BSC',
            'flash_loans': {
                'pancakeswap': '0x10ED43C718714eb63d5aA57B78B54704E256024E',
                'venus': '0xfD36E2c2a6789Db23113685031d7F16329158384',
                'biswap': '0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8'
            },
            'dexes': {
                'pancakeswap': '0x10ED43C718714eb63d5aA57B78B54704E256024E',
                'biswap': '0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8',
                'apeswap': '0xcF0feBd3f17CEf5b47b0cD257aCf6025c5BFf3b7'
            },
            'block_time': 3,
            'native_token': 'BNB',
            'lending': {
                'venus': '0xfD36E2c2a6789Db23113685031d7F16329158384',
                'cream': '0x589de0f0ccf905477646599bb3e5c622c84cc0ba',
                'alpaca': '0xA625AB01B08ce023B2a342Dbb12a16f2C8489A8F'
            },
            'governance': {
                'pancake': '0x0fE9A9295e527f03b03Bd0d19eD935E3147aa23c',
                'venus': '0x0842189729fe41d3b6e4acb60f4aac0521785a3d',
                'alpaca': '0x6d46fb5527bF4B5818F926AaF50B76b76A5c2D21'
            },
            'bridges': {
                'wormhole': '0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B',
                'stargate': '0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
                'layerzero': '0x3c2269811836af69497E5F486A85D7316753cf62',
                'celer': '0x1619DE6B6B20eD217a58d00f37B9d47C7663feca',
                'multichain': '0xC10Ef9F491C9B59f936957026020C321651ac078'
            },
            'stablecoins': {
                'USDT': '0x55d398326f99059fF775485246999027B3197955',
                'USDC': '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
                'BUSD': '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56',
                'DAI': '0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3',
                'MAI': '0x3F56e0c36d275367b8C502090EDF38289b3dEa0d'
            },
            'tokens': {
                'WBNB': '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                'CAKE': '0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82',
                'BTCB': '0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c',
                'ETH': '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
                'XRP': '0x1D2F0da169ceB9fC7B3144628dB156f3F6c60dBE'
            },
            'pool_factories': {
                'pancakeswap_v2': '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73',
                'pancakeswap_v3': '0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865',
                'biswap': '0x858E3312ed3A876947EA49d572A7C42DE08af7EE',
                'apeswap': '0x0841BD0B734E4F5853f0dD8d7Ea041c241fb0Da6'
            },
            'nft_marketplaces': {
                'pancake_nft': '0x17539cCa21C7933Df5c980172d22659B8C345C5A',
                'element': '0x0b84B3F32451ca39e6d6A63673bc2E3F956B6B10',
                'nftkey': '0x48F36F38B20F04366A723F6d0CD0C2F4BB6e6021'
            },
            'mev_config': {
                'flashbots_relay': 'https://bsc-relay.flashbots.net',
                'builder_registration': '0x0000000000000000000000000000000000000000',
                'searcher_registry': '0x0000000000000000000000000000000000000000'
            },
            'amm_pools': {
                'bnb_busd_pancake': '0x58F876857a02D6762E0101bb5C46A8c1ED44Dc16',
                'bnb_usdt_pancake': '0x16b9a82891338f9bA80E2D6970FddA79D1eb0daE',
                'cake_bnb_pancake': '0x0eD7e52944161450477ee417DE9Cd3a859b14fD0'
            },
            'lending_pools': {
                'venus_pool': '0xfD36E2c2a6789Db23113685031d7F16329158384',
                'alpaca_pool': '0xA625AB01B08ce023B2a342Dbb12a16f2C8489A8F',
                'cream_pool': '0x589de0f0ccf905477646599bb3e5c622c84cc0ba'
            },
            'yield_aggregators': {
                'beefy': '0x0d5761D9181C7745855FC985f646a842EB254419',
                'alpaca': '0x0d5761D9181C7745855FC985f646a842EB254419',
                'autofarm': '0x0895196562C7868C5Be92459FaE7f877ED450452'
            },
            'liquid_staking': {
                'ankr_bnb': '0x52F24a5e03aee338Da5fd9Df68D2b6FAe1178827',
                'stader_bnb': '0x7276241a669489E4BBB76f63d2A43Bfe63080F2F',
                'binance_staking': '0x0000000000000000000000000000000000001000'
            }
        },
        137: {  # Polygon
            'name': 'Polygon',
            'flash_loans': {
                'aave': '0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf',
                'balancer': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
                'quickswap': '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff'
            },
            'dexes': {
                'quickswap': '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
                'sushiswap': '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
                'curve': '0x8474DdbE98F5aA3179B3B3F5942D724aFcdec9f6'
            },
            'block_time': 2,
            'native_token': 'MATIC',
            'lending': {
                'aave_v2': '0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf',
                'aave_v3': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'cream': '0x20CA53E2395FA571798623F1cFBD11Fe2C114c24'
            },
            'governance': {
                'aave': '0xc4d4500326981eacE4d0B5735BE73a85E0cA9582',
                'quickswap': '0x5e4be8Bc9637f0EAA1A755019e06A68ce081D58F'
            },
            'bridges': {
                'wormhole': '0x7A4B5a56256163F07b2C80A7cA55aBE66c4ec4d7',
                'polygon_bridge': '0xA0c68C638235ee32657e8f720a23ceC1bFc77C77',
                'hop': '0xb8901acB165ed027E32754E0FFe830802919727f',
                'across': '0x69B5c72837769eF1e7C164Abc6515DcFf217F920',
                'celer': '0x138C20AAc0e1602a92eCd2BF4634098b1d5765F1'
            },
            'stablecoins': {
                'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
                'USDC': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
                'DAI': '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
                'MAI': '0xa3Fa99A148fA48D14Ed51d610c367C61876997F1',
                'FRAX': '0x45c32fA6DF82ead1e2EF74d17b76547EDdFaFF89'
            },
            'tokens': {
                'WMATIC': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
                'WETH': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
                'WBTC': '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6',
                'AAVE': '0xD6DF932A45C0f255f85145f286eA0b292B21C90B',
                'LINK': '0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39'
            },
            'pool_factories': {
                'quickswap_v2': '0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32',
                'quickswap_v3': '0x411b0fAcC3489691f28ad58c47006AF5E3Ab3A28',
                'sushiswap': '0xc35DADB65012eC5796536bD9864eD8773aBc74C4',
                'balancer': '0x8E9aa87E45e92bad84D5F8DD1bff34Fb92637dE9'
            },
            'nft_marketplaces': {
                'quickswap_nft': '0x7E1298EBF3a8B259561df6E797Ff8561756E50EA',
                'opensea': '0x58807baD0B376efc12F5AD86aAc70E78ed67deaE',
                'rarible': '0x7E1298EBF3a8B259561df6E797Ff8561756E50EA'
            },
            'mev_config': {
                'flashbots_relay': 'https://polygon-relay.flashbots.net',
                'builder_registration': '0x0000000000000000000000000000000000000000',
                'searcher_registry': '0x0000000000000000000000000000000000000000'
            },
            'amm_pools': {
                'matic_usdc_quick': '0x6e7a5FAFcec6BB1e78bAE2A1F0B612012BF14827',
                'matic_eth_quick': '0xadbF1854e5883eB8aa7BAf50705338739e558E5b',
                'btc_eth_quick': '0xdC9232E2Df177d7a12FdFf6EcBAb114E2231198D'
            },
            'lending_pools': {
                'aave_v3_pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'aave_v2_pool': '0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf',
                'cream_pool': '0x20CA53E2395FA571798623F1cFBD11Fe2C114c24'
            },
            'yield_aggregators': {
                'beefy': '0xFbdd194376de19a88118e84E279b977f165d01b8',
                'adamant': '0xc3FdbadC7c795EF1D6Ba111e06fF8F16A20Ea539',
                'yearn': '0x9373df4E297bF63c97265052821Bdf4bC82B0F85'
            },
            'liquid_staking': {
                'lido': '0x03b54A6e9a984069379fae1a4fC4dBAE93B3bCCD',
                'stader': '0xC8a35Dd6018eF0D471B8EaB1D0760C978D384818',
                'ankr': '0x24b4A6947274e24B48dF94E72F4A9f8A60A6d2A7'
            }
        },
        42161: {  # Arbitrum
            'name': 'Arbitrum',
            'flash_loans': {
                'aave': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'balancer': '0xBA12222222228d8Ba445958a75a0704d566BF2C8',
                'camelot': '0xc873fEcbd354f5A56E00E710B90EF4201db2448d'
            },
            'dexes': {
                'sushiswap': '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506',
                'camelot': '0xc873fEcbd354f5A56E00E710B90EF4201db2448d',
                'uniswap_v3': '0xE592427A0AEce92De3Edee1F18E0157C05861564'
            },
            'block_time': 0.25,
            'native_token': 'ETH',
            'lending': {
                'aave_v3': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'radiant': '0x2032b9A8e9F7e76768CA9271003d3e43E1616B1F',
                'dforce': '0x8E7e9eA9023B81457Ae7E6D2a51b003D421E5408'
            },
            'governance': {
                'aave': '0xb56c0c7b139c42f4901c8f9e2a5a0cce43eaf7d4',
                'camelot': '0x1d0360bac7299c86ec8e99d0c1c9cc849f05a601'
            },
            'bridges': {
                'arbitrum_bridge': '0x8315177aB297bA92A06054cE80a67Ed4DBd7ed3a',
                'stargate': '0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614',
                'hop': '0x3749C4f034022c39ecafFaBA182555d4508caCCC',
                'across': '0xB88690461dDbaB6f04Dfad7df66B7725942FEb9C',
                'celer': '0x1619DE6B6B20eD217a58d00f37B9d47C7663feca'
            },
            'stablecoins': {
                'USDT': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9',
                'USDC': '0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8',
                'DAI': '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
                'FRAX': '0x17FC002b466eEc40DaE837Fc4bE5c67993ddBd6F',
                'MAI': '0x3F56e0c36d275367b8C502090EDF38289b3dEa0d'
            },
            'tokens': {
                'WETH': '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
                'WBTC': '0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f',
                'LINK': '0xf97f4df75117a78c1A5a0DBb814Af92458539FB4',
                'ARB': '0x912CE59144191C1204E64559FE8253a0e49E6548',
                'GMX': '0xfc5A1A6EB076a2C7aD06eD22C90d7E710E35ad0a'
            },
            'pool_factories': {
                'camelot': '0x6EcCab422D763aC031210895C81787E87B43A652',
                'sushiswap': '0xc35DADB65012eC5796536bD9864eD8773aBc74C4',
                'uniswap_v3': '0x1F98431c8aD98523631AE4a59f267346ea31F984'
            },
            'nft_marketplaces': {
                'trove': '0x2E42F68567B02676b6F86E2f67807eA47079F507',
                'arbitrum_treasure': '0x09986B4e255B3c548041a30A2Ee312Fe176731c2',
                'stratos': '0x51fC0f6660482Ea73330E414eFd7808811a57Fa2'
            },
            'mev_config': {
                'flashbots_relay': 'https://arb1-relay.flashbots.net',
                'builder_registration': '0x52de41D4920d4B16a1fCb81b7f9B4431561C17E1',
                'searcher_registry': '0x7E9c2D47BA30C8Cb5C5F3af95F6797c33451c2cF'
            },
            'amm_pools': {
                'eth_usdc_univ3': '0xC31E54c7a869B9FcBEcc14363CF510d1c41fa443',
                'eth_usdt_camelot': '0x84652bb2539513BAf36e225c930Fdd8eaa63CE27',
                'wbtc_eth_camelot': '0x515e252b2b5c22b4b2b6Df66c2eBeeA871AA4d69'
            },
            'lending_pools': {
                'aave_v3_pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'radiant_pool': '0x2032b9A8e9F7e76768CA9271003d3e43E1616B1F',
                'dforce_pool': '0x8E7e9eA9023B81457Ae7E6D2a51b003D421E5408'
            },
            'yield_aggregators': {
                'yearn': '0x1E95A37Be8A17328fbf4b25b9ce3cE81e271BeB3',
                'beefy': '0x6650e6a8A8eD9464B466Fd2fD5d74ffDA4Fd2fab',
                'jones_dao': '0x7E9c2D47BA30C8Cb5C5F3af95F6797c33451c2cF'
            },
            'liquid_staking': {
                'stader': '0xC339fe15bB423F472ED5170EF6B0965d75260488',
                'ankr': '0x9cD2958E9A7E4d5b8Db5B1B151D5d7b8c2F57A64',
                'origin': '0x2E42F68567B02676b6F86E2f67807eA47079F507'
            }
        },
        10: {  # Optimism
            'name': 'Optimism',
            'flash_loans': {
                'aave': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'velodrome': '0xa132DAB612dB5cB9fC9Ac426A0Cc215A3423F9c9',
                'balancer': '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
            },
            'dexes': {
                'velodrome': '0xa132DAB612dB5cB9fC9Ac426A0Cc215A3423F9c9',
                'uniswap_v3': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
                'curve': '0x2db0E83599a91b508Ac268a6197b8B14F5e72840'
            },
            'block_time': 2,
            'native_token': 'ETH',
            'lending': {
                'aave_v3': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'exactly': '0xA63B831264183D755756ca9AE5190fF5183d65D6',
                'granary': '0x8E7e9eA9023B81457Ae7E6D2a51b003D421E5408'
            },
            'governance': {
                'aave': '0x0E1a3Af1f9cC76A62eD31eDedca291E63632e7c4',
                'velodrome': '0x8A2aa8f1f4A4F3479aB433de4d6C0FBc3409489c'
            },
            'bridges': {
                'optimism_bridge': '0x99C9fc46f92E8a1c0deC1b1747d010903E884bE1',
                'hop': '0x58Cc85b8D04EA49cC6DBd3CbFFd00B4B9E4bb0EC',
                'across': '0x6D1e0220914f562F0973DB9B3947398f608C2133',
                'synapse': '0x2796317b0fF8538F253012862c06787Adfb8cEb6',
                'celer': '0x9D39Fc627A6d9d9F8C831c16995b209548cc3401'
            },
            'stablecoins': {
                'USDC': '0x7F5c764cBc14f9669B88837ca1490cCa17c31607',
                'USDT': '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58',
                'DAI': '0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1',
                'sUSD': '0x8c6f28f2F1A3C87F0f938b96d27520d9751ec8d9',
                'LUSD': '0xc40F949F8a4e094D1b49a23ea9241D289B7b2819'
            },
            'tokens': {
                'WETH': '0x4200000000000000000000000000000000000006',
                'OP': '0x4200000000000000000000000000000000000042',
                'WBTC': '0x68f180fcCe6836688e9084f035309E29Bf0A2095',
                'SNX': '0x8700dAec35aF8Ff88c16BdF0418774CB3D7599B4',
                'LINK': '0x350a791Bfc2C21F9Ed5d10980Dad2e2638ffa7f6'
            },
            'pool_factories': {
                'velodrome_v2': '0xF1046053aa5682b4F9104360B2B9a0D91c917DA7',
                'uniswap_v3': '0x1F98431c8aD98523631AE4a59f267346ea31F984',
                'curve': '0x2db0E83599a91b508Ac268a6197b8B14F5e72840'
            },
            'nft_marketplaces': {
                'quixotic': '0x3Eaf915A8f85D9b9e3B923f3d5A4523Eb5b9F8Eb',
                'optimism_nft': '0x86Bb63148d17d445Ed5398ef26Aa05Bf76dD5b59',
                'tofu': '0x7F5ac0FC127bcf1eAf54E3cd01b00300a0861a62'
            },
            'mev_config': {
                'flashbots_relay': 'https://opt-relay.flashbots.net',
                'builder_registration': '0x8aA931352fEdC5c2Fe75AC74E349E32079334A5e',
                'searcher_registry': '0xE42c837cB4F8d04c426968704dB5EE2dC6Af18cc'
            },
            'amm_pools': {
                'eth_usdc_velo': '0x79c912FEF520be002c2B6e57EC4324e260f38E50',
                'op_usdc_velo': '0x47029bc8f5CBe3b464004E87eF9c9419a48018cd',
                'eth_dai_velo': '0x87C7056DBb3EE462364c933699D71f5A8674A308'
            },
            'lending_pools': {
                'aave_v3_pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'exactly_pool': '0xA63B831264183D755756ca9AE5190fF5183d65D6',
                'sonne_pool': '0x60256D3979Ec427B073A6c0c84aC2aC7A12B9D47'
            },
            'yield_aggregators': {
                'beefy': '0x2A842e01724F10d093aE8a46A01e66aE1cF4699F',
                'yearn': '0x8787D10E1014Bd0EEaE1B5C301e90D95f4d18973',
                'pickle': '0x0c5b4c92c948691EEBf185C17eeB9c230DC019E9'
            },
            'liquid_staking': {
                'lido': '0x1F32b1c2345538c0c6f582fCB022739c4A194Ebb',
                'stader': '0xCf5EA1b38380f6aF39068375516Daf40Ed70D299',
                'ankr': '0x5B14883D4A1e5e5B2Ef375FC7C86AF3444e7C21F'
            }
        },
        43114: {  # Avalanche
            'name': 'Avalanche',
            'flash_loans': {
                'aave': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'trader_joe': '0x60aE616a2155Ee3d9A68541Ba4544862310933d4',
                'platypus': '0x66357dCaCe80431aee0A7507e2E361B7e2402370'
            },
            'dexes': {
                'trader_joe': '0x60aE616a2155Ee3d9A68541Ba4544862310933d4',
                'pangolin': '0xE54Ca86531e17Ef3616d22Ca28b0D458b6C89106',
                'curve': '0x7f90122BF0700F9E7e1F688fe926940E8839F353'
            },
            'block_time': 2,
            'native_token': 'AVAX',
            'lending': {
                'aave_v3': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'benqi': '0x486Af39519B4Dc9a7fCcd318217352830E8AD9b4',
                'vector': '0x825a47C9c758D1D9B5f2e9bF4E7Cd00F4946428A'
            },
            'governance': {
                'aave': '0x3B49E459086BB12d0eB53C7deC8C86d881c26d6d',
                'benqi': '0x2b2C81e08f1Af8835a78Bb2A90AE924ACE0eA4bE',
                'trader_joe': '0x9C2C8910F113181783c249d8F6Aa41b51Cde0f0c'
            },
            'bridges': {
                'avalanche_bridge': '0x8F47416CaE600bccF9530E9F3aeaA06bdD1Caa79',
                'stargate': '0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614',
                'layerzero': '0x3c2269811836af69497E5F486A85D7316753cf62',
                'synapse': '0x0000000000000000000000000000000000000000',
                'celer': '0x5427FEFA711Eff984124bFBB1AB6fbf5E3DA1820'
            },
            'stablecoins': {
                'USDC': '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E',
                'USDT': '0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7',
                'DAI': '0xd586E7F844cEa2F87f50152665BCbc2C279D8d70',
                'MIM': '0x130966628846BFd36ff31a822705796e8cb8C18D',
                'FRAX': '0xD24C2Ad096400B6FBcd2ad8B24E7acBc21A1da64'
            },
            'tokens': {
                'WAVAX': '0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7',
                'WETH': '0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB',
                'WBTC': '0x50b7545627a5162F82A992c33b87aDc75187B218',
                'LINK': '0x5947BB275c521040051D82396192181b413227A3',
                'JOE': '0x6e84a6216eA6dACC71eE8E6b0a5B7322EEbC0fDd'
            },
            'pool_factories': {
                'trader_joe_v2': '0x9Ad6C38BE94206cA50bb0d90783181662f0Cfa10',
                'pangolin': '0xefa94DE7a4656D787667C749f7E1223D71E9FD88',
                'curve': '0x7E0B53B4CB15dB99C9158b1cfa22A4256C2E0A91'
            },
            'nft_marketplaces': {
                'joepegs': '0x7E1298EBF3a8B259561df6E797Ff8561756E50EA',
                'kalao': '0x58807baD0B376efc12F5AD86aAc70E78ed67deaE',
                'nftrade': '0x7E1298EBF3a8B259561df6E797Ff8561756E50EA'
            },
            'mev_config': {
                'flashbots_relay': 'https://avalanche-relay.flashbots.net',
                'builder_registration': '0x0000000000000000000000000000000000000000',
                'searcher_registry': '0x0000000000000000000000000000000000000000'
            },
            'amm_pools': {
                'avax_usdc_joe': '0xf4003F9D9274Cd9E505E8054143c51592eB6Bd0F',
                'avax_eth_joe': '0xFE15c2695F1F920da45C30AAE47d11dE51007AF9',
                'btc_avax_joe': '0x2fD81391E30805Cc7F2Ec827013ce86dc591B806'
            },
            'lending_pools': {
                'aave_v3_pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'benqi_pool': '0x486Af39519B4Dc9a7fCcd318217352830E8AD9b4',
                'vector_pool': '0x825a47C9c758D1D9B5f2e9bF4E7Cd00F4946428A'
            },
            'yield_aggregators': {
                'yield_yak': '0xC3537ef04Ad744174A4B7f1dF27Bb58cB9825F75',
                'beefy': '0xD152c7F25db7F4B95b7658323c5F33d176818EE4',
                'aave': '0x4F01AeD16D97E3aB5ab2B501154DC9bb0F1A5A2C'
            },
            'liquid_staking': {
                'benqi_liquid': '0xE1d70994Be12b43F7quit5E2F39911A77123F83F',
                'ankr': '0x52F24a5e03aee338Da5fd9Df68D2b6FAe1178827',
                'platypus': '0x5857019c749147EEE22b1Fe63500F237F3c1B692'
            }
        },
        250: {  # Fantom
            'name': 'Fantom',
            'flash_loans': {
                'aave': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'spookyswap': '0xF491e7B69E4244ad4002BC14e878a34207E38c29',
                'solidly': '0x777777777777777777777777777777777777777'
            },
            'dexes': {
                'spookyswap': '0xF491e7B69E4244ad4002BC14e878a34207E38c29',
                'spiritswap': '0x16327E3FbDaCA3bcF7E38F5Af2599D2DDc33aE52',
                'curve': '0x0f854EA9F38ceA4B1c2FC79047E9D0134419D5d6'
            },
            'block_time': 1,
            'native_token': 'FTM',
            'lending': {
                'aave_v3': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'geist': '0x9FAD24f572045c7869117160A571B2e50b10d068',
                'cream': '0x4A6803835D43A5F8C8c133cF4aA5f6D0424d5e2A'
            },
            'governance': {
                'aave': '0x4F47bc496083c727C5fBa6643150B3B42c87BbD7',
                'spookyswap': '0x6c5A0C007c8F2F29B74f6d5645E29b8B0eE3B541'
            },
            'bridges': {
                'fantom_bridge': '0xC564EE9f21Ed8A2d8E7e76c085740d5e4c5FaFbE',
                'multichain': '0x1ccca1ce62c62f7Be95d4A67722a8fdbed6eecb4',
                'anyswap': '0x1CcCA1cE62c62F7Be95d4A67722a8FDBed6EEcb4',
                'celer': '0x374B8a9f3eC5eB2D97EcA84Ea27aCa0C094BaAB2',
                'synapse': '0x8F5BBB2BB8c2Ee94639E55d5F41de9b4839C1280'
            },
            'stablecoins': {
                'USDC': '0x04068DA6C83AFCFA0e13ba15A6696662335D5B75',
                'USDT': '0x049d68029688eAbF473097a2fC38ef61633A3C7A',
                'DAI': '0x8D11eC38a3EB5E956B052f67Da8Bdc9bef8Abf3E',
                'MIM': '0x82f0B8B456c1A451378467398982d4834b6829c1',
                'FRAX': '0xdc301622e621166BD8E82f2cA0A26c13Ad0BE355'
            },
            'tokens': {
                'WFTM': '0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83',
                'WETH': '0x74b23882a30290451A17c44f4F05243b6b58C76d',
                'WBTC': '0x321162Cd933E2Be498Cd2267a90534A804051b11',
                'BOO': '0x841FAD6EAe12c286d1Fd18d1d525DFfA75C7EFFE',
                'SPIRIT': '0x5Cc61A78F164885776AA610fb0FE1257df78E59B'
            },
            'pool_factories': {
                'spookyswap': '0x152eE697f2E276fA89E96742e9bB9aB1F2E61bE3',
                'spiritswap': '0x9083EA3756BDE6Ee6f27a6e996806FBD37F6F093',
                'solidly': '0x3fAaB499b519fdC5819e3D7ed0C9a48ecdD71d51'
            },
            'nft_marketplaces': {
                'paintswap': '0x85E139B78Ef1e6A521cd502418EE9B5D470A7d59',
                'nftkey': '0x26D583028989378Cc6cD8c0C745eb4d5BB55dE44',
                'artion': '0x6E746367BdBe9E83A1B6d327c83F37277880dC2B'
            },
            'mev_config': {
                'flashbots_relay': 'https://fantom-relay.flashbots.net',
                'builder_registration': '0x0000000000000000000000000000000000000000',
                'searcher_registry': '0x0000000000000000000000000000000000000000'
            },
            'amm_pools': {
                'ftm_usdc_spooky': '0x2b4C76d0dc16BE1C31D4C1DC53bF9B45987Fc75c',
                'ftm_eth_spooky': '0x613BF4E46b4817015c01c6Bb31C7ae9edAadc26e',
                'btc_eth_spooky': '0xf0702249F4D3A25cD3DED7859a165693685Ab577'
            },
            'lending_pools': {
                'aave_v3_pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'geist_pool': '0x9FAD24f572045c7869117160A571B2e50b10d068',
                'cream_pool': '0x4A6803835D43A5F8C8c133cF4aA5f6D0424d5e2A'
            },
            'yield_aggregators': {
                'beefy': '0xc461E6BaB071b7863a1C86D6BED34b9178F9Bd5e',
                'reaper': '0x7BdBce767B6Bb8c6e6F85D55DEe3F25E9E18e445',
                'tarot': '0x35C052bBf8338b06351782A565aa9AaD173432eA'
            },
            'liquid_staking': {
                'stader': '0x12edeA9cd262006cC3C4E77c90d2CD2DD4b1eb97',
                'ankr': '0xF6C62093B957Fc8742e3A8812dE45F6374d36487',
                'liquid_driver': '0x06D73C1eB9479E2E8C973413fF2C5FB0F9159F99'
            }
        },
        25: {  # Cronos
            'name': 'Cronos',
            'flash_loans': {
                'vvs': '0x145863Eb42Cf62847A6Ca784e6416C1682b1b2Ae',
                'mm_finance': '0x145677FC4d9b8F19B5D56d1820c48e0443049a30',
                'crodex': '0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23'
            },
            'dexes': {
                'vvs': '0x145863Eb42Cf62847A6Ca784e6416C1682b1b2Ae',
                'mm_finance': '0x145677FC4d9b8F19B5D56d1820c48e0443049a30',
                'crodex': '0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23'
            },
            'block_time': 6,
            'native_token': 'CRO',
            'lending': {
                'tectonic': '0xbb10Bc0738D1Fd82E4B60Dd63747Ed3d98486978',
                'mimas': '0x8b8B725F388B4BE5dE9aA5B8394e946E3B7E35aC',
                'iron_bank': '0x2F0b4300074aA34172Af869B7D9d0C3F22c7f350'
            },
            'governance': {
                'vvs': '0x6D5c7fE42c5F3A7C85D72b9E5A8a4c35E34C2f33',
                'mm_finance': '0x1A4bb8E03C35e2B672A0fcE18cab920aa023d7FC'
            },
            'bridges': {
                'cronos_bridge': '0x64C5A4Edd8093dB9Ea62421E31B4B9A4056A9147',
                'celer': '0x0000000000000000000000000000000000000001',
                'multichain': '0xC21223F159260aB1196cCc2b3655629A02eC6b53',
                'axelar': '0x4B3F2c608B2B6B28c6d743C39E0C852A914F8Cad',
                'layerzero': '0x9B896c0E23220469C7AE69cb4BbAE391eAa4C8da'
            },
            'stablecoins': {
                'USDC': '0xc21223F159260aB1196cCc2b3655629A02eC6b53',
                'USDT': '0x66e428c3f67a68878562e79A0234c1F83c208770',
                'DAI': '0xF2001B145b43032AAF5Ee2884e456CCd805F677D',
                'BUSD': '0x6aB6d61428fde76768D7b45D8BFeec19c6eF91A8',
                'MAI': '0x2Ae35c8E3D4bD57e8898FF7cd2bBff87166EF8cB'
            },
            'tokens': {
                'WCRO': '0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23',
                'WETH': '0xe44Fd7fCb2b1581822D0c862B68222998a0c299a',
                'WBTC': '0x062E66477Faf219F25D27dCED647BF57C3107d52',
                'VVS': '0x2D03bECE6747ADC00E1a131BBA1469C15fD11e03',
                'MMF': '0x97749c9B61F878a880DfE312d2594AE07AEd7656'
            },
            'pool_factories': {
                'vvs_factory': '0x3B44B2a187a7b3824131F8db5a74194D0a42Fc15',
                'mm_factory': '0xd590cC180601AEcD6eeADD9B7f2B7611519544f4',
                'crodex_factory': '0xe9c29cB475C0ADe80bE0319B74AD112F1e80058F'
            },
            'nft_marketplaces': {
                'minted': '0x6e1C578AE3f908dA891B71C9b4AF2F5D7cB7Ff73',
                'ebisu': '0x70F3230E23E3Ef92B52A0d6779aF91dA9C83844B',
                'crocos': '0x4e9A46Ea6F8F34b647b50E4EF6aD951F8D9F65B0'
            },
            'mev_config': {
                'flashbots_relay': 'https://cronos-relay.mev.com',
                'builder_registration': '0x0000000000000000000000000000000000000000',
                'searcher_registry': '0x0000000000000000000000000000000000000000'
            },
            'amm_pools': {
                'cro_usdc_vvs': '0x814920D1b8007207db6cB5a2dD92bF0b082BDBa1',
                'cro_eth_vvs': '0xA111C17f8B8303280d3EB01BBcd61000AA7F39F9',
                'btc_eth_vvs': '0x8F09fFf247B8fDB80461E5Cf5E82dD1aE2EBd6d7'
            },
            'lending_pools': {
                'tectonic_pool': '0xbb10Bc0738D1Fd82E4B60Dd63747Ed3d98486978',
                'mimas_pool': '0x8b8B725F388B4BE5dE9aA5B8394e946E3B7E35aC',
                'iron_bank_pool': '0x2F0b4300074aA34172Af869B7D9d0C3F22c7f350'
            },
            'yield_aggregators': {
                'vvs_finance': '0xDccd6455AE04b03d785F12196B492b18129564bc',
                'mm_finance': '0x6bE34986Fdd1A91e4634eb6b9F8017439b7b5EDc',
                'dark_crypto': '0x7C82A23B4C48D796dee36A9cA215b641C6a8709d'
            },
            'liquid_staking': {
                'stader_cro': '0x1c0C5D1b02084959C84FBc1d6dA43Af20D19e536',
                'ankr_cro': '0x9Ac59862934eBC36164Cd46DeD8966A71F1834F5',
                'persistence': '0x8E024516aA574d0342155Df35f52c4E0D08D7D53'
            }
        },
        8453: {  # Base
            'name': 'Base',
            'flash_loans': {
                'aerodrome': '0x2626664c2603336E57B271c5C0b26F421741e481',
                'baseswap': '0x327Df1E6de05895d2ab08513aaDD9313Fe505d86',
                'balancer': '0xBA12222222228d8Ba445958a75a0704d566BF2C8'
            },
            'dexes': {
                'baseswap': '0x327Df1E6de05895d2ab08513aaDD9313Fe505d86',
                'aerodrome': '0x2626664c2603336E57B271c5C0b26F421741e481',
                'uniswap_v3': '0x2626664c2603336E57B271c5C0b26F421741e481'
            },
            'block_time': 2,
            'native_token': 'ETH',
            'lending': {
                'aave_v3': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'moonwell': '0xfBb21d0380beE3312B33c4353c8936a0F13EF26C',
                'sonne': '0x5E40E8C2F40E15A7f1b77f4d7918F228C32e9939'
            },
            'governance': {
                'aave': '0x0D8b5F3242C371d5429F6E6c2A2CDb8af2594ccE',
                'aerodrome': '0x2b0A43DCcBD7d42c18F6A83F86D1a7fbE5579E1D'
            },
            'bridges': {
                'base_bridge': '0x3154Cf16ccdb4C6d922629664174b904d80F2C35',
                'layerzero': '0xb6319cC6c8c27A8F5dAF0dD3DF91EA35C4720dd7',
                'across': '0x4D9079Bb4165aeb4084c526a32695dCfd2F77381',
                'hop': '0x3666f603Cc164936C1b87e207F36BEBa4AC5f18a',
                'synapse': '0x2967E7Bb9DaA5711Ac332cAF874BD47ef99B3820'
            },
            'stablecoins': {
                'USDbC': '0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA',
                'USDC': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
                'DAI': '0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb',
                'USDT': '0x4200000000000000000000000000000000000000',
                'MAI': '0xbf1aeA8670D2528E08334083616dD9C5F3B087aE'
            },
            'tokens': {
                'WETH': '0x4200000000000000000000000000000000000006',
                'cbETH': '0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22',
                'WBTC': '0x77E06c9eCCf2E797fd462A92B6D7642EF85b0A44',
                'COMP': '0x9e1028F5F1D5eDE59748FFceE5532509976840E0',
                'LINK': '0xA5B55Dc1757A68A82Be064C9D61c0088cd5766b7'
            },
            'pool_factories': {
                'aerodrome': '0x420DD381b31aEf6683db6B902084cB0FFEe076115',
                'baseswap': '0x38015D05f4fEC8AFe15D7cc0386a126574e8077B',
                'uniswap_v3': '0x33128a8fC17869897dcE68Ed026d694621f6FDfD'
            },
            'nft_marketplaces': {
                'base_market': '0xd5A6Af33E3E6A671C3Ad62E843C220e5E0Ee6BA1',
                'blur': '0x983e96c26782A8DE39Ae88703aa5c92A0000000b',
                'opensea': '0x1823FfE6C7d3b80D890a8E6E92fA29F8c2dA257C'
            },
            'mev_config': {
                'flashbots_relay': 'https://base-relay.flashbots.net',
                'builder_registration': '0x0000000000000000000000000000000000000000',
                'searcher_registry': '0x0000000000000000000000000000000000000000'
            },
            'amm_pools': {
                'eth_usdc_aero': '0xc44AD482F24fd750cDfA3E6D25C56b25C8829266',
                'eth_dai_aero': '0x36E08E815F36f637A96F39092a02F0d0F22B896C',
                'wbtc_eth_aero': '0x4C36388bE6F416A29C8d8Eee81C771cE6bE14B18'
            },
            'lending_pools': {
                'aave_v3_pool': '0x794a61358D6845594F94dc1DB02A252b5b4814aD',
                'moonwell_pool': '0xfBb21d0380beE3312B33c4353c8936a0F13EF26C',
                'sonne_pool': '0x5E40E8C2F40E15A7f1b77f4d7918F228C32e9939'
            },
            'yield_aggregators': {
                'beefy': '0x4E8B0cF0427D9cAB11D7A758f03fF6A92F5C68B9',
                'yearn': '0x5c8D727b265DBAfaba67E050f2f739cAeEB4A6F9',
                'overnight': '0x8C45969aD19D297c9B85763e90D0344C6E2ac9Ec'
            },
            'liquid_staking': {
                'stader': '0x4C6dEA5Ac82526Eb8F63245F5cdC6E596B3Ff2Eb',
                'kelp': '0x0EDFCC1b8d082cd46d13Db694b849d7d8172fB33',
                'ankr': '0xE01ef2b537f1D5964c4659cB2Aa699c812Aa8238'
            }
        },
        324: {  # zkSync
            'name': 'zkSync',
            'flash_loans': {
                'syncswap': '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295',
                'mute': '0x8B791913eB07C32779a16750e3868aA8495F5964',
                'velocore': '0x46dbd39e26a56778d88507d7aEC6967108C0BD26'
            },
            'dexes': {
                'syncswap': '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295',
                'mute': '0x8B791913eB07C32779a16750e3868aA8495F5964',
                'velocore': '0x46dbd39e26a56778d88507d7aEC6967108C0BD26'
            },
            'block_time': 1,
            'native_token': 'ETH',
            'lending': {
                'reactorfusion': '0x1e8F1099a3fe6D2c1A960528394F4fEB8f8A288D',
                'zerolend': '0x67aA3eCc5831a65A5Ba7be76BED3B5dc7DB60796'
            },
            'governance': {
                'syncswap': '0x9e6b3E9C8401776Ec01c1F4d57B49Fa5C8858aB1',
                'mute': '0x0BE9e53Fd7EDaC9F859882AfdDa116645287C629'
            },
            'bridges': {
                'zksync_bridge': '0x32400084C286CF3E17e7B677ea9583e60a000324',
                'layerzero': '0x9b896c0E23220469C7AE69cb4BbAE391eAa4C8da',
                'stargate': '0x1C3DcD1F8b95D661F7EAd5c9c4C48C3aE82f0C85',
                'orbiter': '0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8',
                'across': '0x7885Cd5731A2F4165e6DbB0C9C0A1B90f7405298'
            },
            'stablecoins': {
                'USDC': '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',
                'USDT': '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',
                'DAI': '0x4B9eb6c0b6ea15176BBF62841C6B2A8a398cb656',
                'LUSD': '0x503234F203fC7Eb888EEC8513210612a43Cf6115',
                'FRAX': '0x722E8BdD2ce80A4422E880164f2079488e115365'
            },
            'tokens': {
                'WETH': '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91',
                'WBTC': '0xBBeB516fb02a01611cBBE0453Fe3c580D7281011',
                'LINK': '0x3A1429d50E89dBc2dE47A7B6B5dAB167d8719a61',
                'MUTE': '0x0e97C7a0F8B2C9885C8ac9fC6136e829CbC21d42',
                'SYNC': '0xE4eDb277e41dc89aB076a1F049f4a3EfA700bCE8'
            },
            'pool_factories': {
                'syncswap': '0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb',
                'mute': '0x40BE1cBa6C5B47cDF9da7f963B6F761F4C60627D',
                'velocore': '0xf0e1f962A6E1F8D4D4A0Bb3E35E0B1e6129D9a9e'
            },
            'nft_marketplaces': {
                'tofunft': '0x7C3b814754f8f9E6F27D14B8d60aE0A6f392d2F2',
                'element': '0x47312450B3Ac8b5b8e247a6bB6d523e7605bDb60',
                'mintverse': '0x0D4C1222F5e839a911e2053860e45F18921D75E9'
            },
            'mev_config': {
                'flashbots_relay': 'https://zksync-relay.flashbots.net',
                'builder_registration': '0x0000000000000000000000000000000000000000',
                'searcher_registry': '0x0000000000000000000000000000000000000000'
            },
            'amm_pools': {
                'eth_usdc_sync': '0x80115c708E12eDd42E504c1cD52Aea96C547c05c',
                'eth_usdt_sync': '0xCf96E6D8ab5a3Aa2E9F8A38B5d97Bf2bA67d2134',
                'wbtc_eth_sync': '0x5b54Aa6BF87b2C78B494Dc41B85e157b2E9Bd4eD'
            },
            'lending_pools': {
                'reactorfusion': '0x1e8F1099a3fe6D2c1A960528394F4fEB8f8A288D',
                'zerolend': '0x67aA3eCc5831a65A5Ba7be76BED3B5dc7DB60796',
                'basilisk': '0x1BbD33384869b30A323e15868Ce46013C82B86FB'
            },
            'yield_aggregators': {
                'nexon': '0x1E95A37Be8A17328fbf4b25b9ce3cE81e271BeB3',
                'reactor': '0x4B9eb6c0b6ea15176BBF62841C6B2A8a398cb656',
                'velocore': '0x46dbd39e26a56778d88507d7aEC6967108C0BD26'
            },
            'liquid_staking': {
                'stader': '0x1BbD33384869b30A323e15868Ce46013C82B86FB',
                'ankr': '0x2E42F68567B02676b6F86E2f67807eA47079F507',
                'renzo': '0x7C82A23B4C48D796dee36A9cA215b641C6a8709d'
            }
        }
    }

    @classmethod
    def get_adapter(cls, chain_id: int) -> ChainAdapter:
        """Get chain-specific adapter"""
        try:
            chain_config = cls.CHAIN_CONFIGS.get(chain_id)
            if not chain_config:
                raise ValueError(f"Unsupported chain ID: {chain_id}")
                
            return ChainAdapter(
                chain_id=chain_id,
                name=chain_config['name'],
                rpc_url=config.get_rpc_url(chain_id),
                fork_block=None,  # Will be set during test setup
                flash_loan_providers=chain_config['flash_loans'],
                dex_routers=chain_config['dexes'],
                oracle_feeds=cls._get_oracle_feeds(chain_id),
                native_token=cls._get_native_token(chain_id),
                block_time=cls._get_block_time(chain_id),
                gas_token=cls._get_gas_token(chain_id),
                bridges=chain_config['bridges'],
                stablecoins=chain_config['stablecoins'],
                tokens=chain_config['tokens'],
                pool_factories=chain_config['pool_factories'],
                nft_marketplaces=chain_config['nft_marketplaces'],
                mev_config=chain_config['mev_config'],
                amm_pools=chain_config['amm_pools'],
                lending_pools=chain_config['lending_pools'],
                yield_aggregators=chain_config['yield_aggregators'],
                liquid_staking=chain_config['liquid_staking']
            )
            
        except Exception as e:
            logger.error(f"Error creating chain adapter: {str(e)}")
            raise

    @classmethod
    def _get_oracle_feeds(cls, chain_id: int) -> Dict[str, str]:
        """Get chain-specific oracle feeds"""
        ORACLE_CONFIGS = {
            1: {  # Ethereum
                'ETH_USD': '0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419',
                'BTC_USD': '0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c',
                'USDC_USD': '0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6',
                'DAI_USD': '0xAed0c38402a5d19df6E4c03F4E2DceD6e29c1ee9',
                'LINK_USD': '0x2c1d072e956AFFC0D435Cb7AC38EF18d24d9127c'
            },
            56: {  # BSC
                'BNB_USD': '0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE',
                'BTC_USD': '0x264990fbd0A4796A3E3d8E37C4d5F87a3aCa5Ebf',
                'USDT_USD': '0xB97Ad0E74fa7d920791E90258A6E2085088b4320',
                'CAKE_USD': '0xB6064eD41d4f67e353768aA239cA86f4F73665a1',
                'BUSD_USD': '0xcBb98864Ef56E9042e7d2efef76141f15731B82f'
            },
            137: {  # Polygon
                'MATIC_USD': '0xAB594600376Ec9fD91F8e885dADF0CE036862dE0',
                'BTC_USD': '0xc907E116054Ad103354f2D350FD2514433D57F6f',
                'ETH_USD': '0xF9680D99D6C9589e2a93a78A04A279e509205945',
                'USDC_USD': '0xfE4A8cc5b5B2366C1B58Bea3858e81843581b2F7',
                'AAVE_USD': '0x72484B12719E23115761D5DA1646945632979bB6'
            },
            42161: {  # Arbitrum
                'ETH_USD': '0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612',
                'BTC_USD': '0x6ce185860a4963106506C203335A2910413708e9',
                'LINK_USD': '0x86E53CF1B870786351Da77A57575e79CB55812CB',
                'USDC_USD': '0x50834F3163758fcC1Df9973b6e91f0F0F0434aD3',
                'ARB_USD': '0xb2A824043730FE05F3DA2efaFa1CBbe83fa548D6'
            },
            10: {  # Optimism
                'ETH_USD': '0x13e3Ee699D1909E989722E753853AE30b17e08c5',
                'BTC_USD': '0xD702DD976Fb76Fffc2D3963D037dfDae5b04E593',
                'OP_USD': '0x0D276FC14719f9292D5C1eA2198673d1f4269246',
                'USDC_USD': '0x16a9FA2FDa030272Ce99B29CF780dFA30361E0f3',
                'SNX_USD': '0x2FCF37343e916eAEd1f1DdaaF84458a359b53877'
            },
            43114: {  # Avalanche
                'AVAX_USD': '0x0A77230d17318075983913bC2145DB16C7366156',
                'BTC_USD': '0x2779D32d5166BAaa2B2b658333bA7e6Ec0C65743',
                'ETH_USD': '0x976B3D034E162d8bD72D6b9C989d545b839003b0',
                'USDC_USD': '0xF096872672F44d6EBA71458D74fe67F9a77a23B9',
                'LINK_USD': '0x49ccd9ca821EfEab2b98c60dC60F518E765EDe9a'
            },
            250: {  # Fantom
                'FTM_USD': '0xf4766552D15AE4d256Ad41B6cf2933482B0680dc',
                'BTC_USD': '0x8e94C22142F4A64b99022ccDd994f4e9EC86E4B4',
                'ETH_USD': '0x11DdD3d147E5b83D01cee7070027092397d63658',
                'USDC_USD': '0x2553f4eeb82d5A26427b8d1106C51499CBa5D99c',
                'LINK_USD': '0x221C773d8647BC3034e91a0c47062e26D20d97B4'
            },
            25: {  # Cronos
                'CRO_USD': '0x5B55012bC6DBf545B6a5ab6237030f79b1E38beD',
                'BTC_USD': '0x0250eb557D7BF7A43d408B5293B47da7F12FB7E8',
                'ETH_USD': '0x66bB235A45Fab133E0378f5490cB6dB961F48E61',
                'USDC_USD': '0x51597f405303C4377E36123cBc172b13269EA163',
                'USDT_USD': '0x1B2103441A0A108daD8848D8F5d790e4D402921F'
            },
            8453: {  # Base
                'ETH_USD': '0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70',
                'BTC_USD': '0xCCADC697c55bbB68dc5bCdf8d3CBe83CdD4E071E',
                'USDC_USD': '0x7e860098F58bBFC8648a4311b374B1D669a2bc6B',
                'DAI_USD': '0x591e79239a7d679378eC8c847e5038150364C78F',
                'LINK_USD': '0x45f7260f7Cc0C4E8507d7FD989529C1e06EE8A3C'
            },
            324: {  # zkSync
                'ETH_USD': '0x6D9bB8C0C154D4dF1F471C485dF12d236699F356',
                'BTC_USD': '0x83A757eAe821Ad7B520D9A65A2C72B8f2D890084',
                'USDC_USD': '0x75D18d8749588F58B4dB6BB207449cF7B8f8c689',
                'USDT_USD': '0x6c5F6B3eB7c68E267E9Af5f37748147A54D70F6b',
                'DAI_USD': '0x48F3F51146B8F28419B36B6E03AE158F31Bb0F24'
            }
        }
        return ORACLE_CONFIGS.get(chain_id, {})

    @classmethod
    def _get_native_token(cls, chain_id: int) -> str:
        """Get chain's native token"""
        chain_config = cls.CHAIN_CONFIGS.get(chain_id)
        return chain_config['native_token'] if chain_config else 'ETH'

    @classmethod
    def _get_block_time(cls, chain_id: int) -> int:
        """Get chain's average block time"""
        chain_config = cls.CHAIN_CONFIGS.get(chain_id)
        return chain_config['block_time'] if chain_config else 12

    @classmethod
    def _get_gas_token(cls, chain_id: int) -> str:
        """Get chain's gas token"""
        return cls._get_native_token(chain_id)  # Gas token is usually native token 