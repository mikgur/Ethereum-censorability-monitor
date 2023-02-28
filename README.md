<p align="center">
  <img src="https://raw.githubusercontent.com/mikgur/Ethereum-censorability-monitor/b6c764e278b7330a9a580f5e25c2c3950d94c928/img/cover.png" align="middle"  width="600" />
</p>


<h2 align="center">
 Ethereum Censorability Monitor
</h2S>
 <h1 align="center">
 Neutrality Watch
</h2S>

<h4 align="center">

![1](https://img.shields.io/badge/python-3.10-blue.svg)
![2](https://img.shields.io/badge/os-linux-green.svg)
![3](https://img.shields.io/github/stars/mikgur/Ethereum-censorability-monitor?color=ccf)
![4](https://img.shields.io/github/license/mikgur/Ethereum-censorability-monitor)

</h4>

-----------------------------------------------

<h4 align="center">
  <a href=#-problem> Problem </a> |
  <a href=#-lego-grant> LEGO grant </a> |
  <a href=#-project_components> Project Components </a> |
  <a href=#-metrics> Metrics </a> |
  <a href=#-installation> Installation </a> |
  <a href=#-quick-start> Quick Start </a> |
  <a href=#-mongo_db_metrics_scheme> Mongo DB metrics scheme  </a> |
  <a href=#-api-reference> API Reference </a> |
  <a href=#-community> Community </a>
  <a href=#-acknowledgments> Acknowledgments </a>
</h4>

-----------------------------------------------
## &#128204; Problem

  The problem of censorship for non compliant transactions on the Ethereum blockchain is that certain transactions may be blocked or censored by node operators or validators who comply with some lists of forbidden addresses.

## &#128204; LEGO grant

[Lido RFP Ethereum Censorability Monitor](https://research.lido.fi/t/rfp-ethereum-censorability-monitor/3330)

Our project meets the first grant criteria in the following ways:

- We propose several metrics for tracking service degradation for censorable transactions, please refer to section <a href=#-metrics> Metrics </a> for more info.

- Our platform tracks the impact of Lido and Lido’s node operators on service degradation. (e.g. <a href=#4-censorship-latency>Censorship Latency</a> and <a href=#5-lido-adjusted-censorship-latency>Lido-adjusted censorship latency</a>)

- We have developed an API to access our data, and we plan to open up access to it in March upon request, for more info please refer to <a href=#-api-reference> API Reference </a> section.

- Our project has been designed to be easily maintainable by a small team of developers (1-2 in total), with low complexity and cost.

- We compare impact of Lido and Lido’s node operators to other staking pools, where applicable. (e.g. <a href=#1-non-ofac-and-ofac-compliance-ratio-metrics>Non-OFAC and OFAC Compliance Ratio Metrics</a>, <a href=#2-censorship-resistance-index>Censorship Resistance Index</a>)

- Our project is open-source.

## &#128204; Project Components

  #### Project Components:

1. __Data collection service__ - includes _data_collector.py_ and _censorability_monitor_ module. This component collects data from the mempool and blockchain.
2. __Analytics service__ - includes _censorship_analytics.py_ and _censorability_monitor_ module. This component gathers data from various sources, evaluates censorship, and calculates metrics.
3. __Backend__ - serves as the bridge between the analytics module and the frontend. It exposes an API that the frontend can use to request data and metrics.
4. __Frontend__

<p align="center">
  <img src="https://raw.githubusercontent.com/mikgur/Ethereum-censorability-monitor/feature/documentation/img/structure.png" align="middle"  width="600" />
</p>

## &#128204; Metrics

We proposed following metrics:

### <b>1) Non-OFAC and OFAC Compliance Ratio Metrics</b>

For each validator we calculate:

1. Non-OFAC Compliance Ratio: the percentage of non-OFAC compliant transactions that are included in blocks proposed by the validator.
2. OFAC Compliance Ratio: the percentage of OFAC compliant transactions that are included in blocks proposed by the validator.

These metrics help us understand the relative likelihood of a validator including non-OFAC compliant transactions versus OFAC compliant ones.

### <b>2) Censorship Resistance Index</b>

The metric we calculate is the ratio of the share of non-OFAC compliant transactions included by a validator to the share of OFAC compliant transactions included by the same validator. This metric provides insight into whether a particular validator is more likely to include non-compliant transactions in blocks compared to compliant transactions.

The possible values of this index range from zero to infinity. An index of one means that the validator includes non-compliant and compliant transactions at the same rate. An index greater than one means that the validator includes non-compliant transactions more often than compliant transactions. Conversely, an index less than one indicates that the validator includes non-compliant transactions less frequently than compliant transactions. Overall, a low Censorship Resistance Index could be an indication of potential censorship by a validator.

### <b>3) Lido Censorship Resistance Index and Other Validators Censorship Resistance Index.</b>

We calculate Censorship Resistance Index for all the Lido validators and compare it to all the other validators in total.

### <b>4) Censorship Latency</b>

The Censorship Latency metric measures the difference in average waiting time for transactions with similar features, except for their OFAC compliance status. We use a binary classifier with high accuracy to predict the number of blocks for which non-OFAC compliant transactions were not included due to censorship. This number is then multiplied by 12 to calculate the Censorship Latency metric.

### <b>5) Lido-adjusted censorship latency</b>

We also compute a modified version of the Censorship Latency metric by assuming that the Lido validators do not engage in censorship. This adjusted metric helps to understand the impact of censorship by other validators on the overall network.

Please find details in our [notion page](https://accidental-eyelash-d3a.notion.site/Transaction-analysis-and-metrics-calculation-991b4e30fbc146469398860073547016)

## &#128204; Installation

### __Data collection service__ and  __Analytics service__

- create __.env file__, example (you can use same MongoDB instance for both _db_collector_ and _db_analytics_):

```# MongoDB
db_collector_url = localhost
db_collector_port = 27017
db_collector_username = root
db_collector_password = some_password
db_collector_name = ethereum_mempool

db_analytics_url = otherhost
db_analytics_port = 27017
db_analytics_username = root
db_analytics_password = another_password
db_analytics_name = ethereum_censorship_monitor


# Ethereum node
node_url = /path_to/geth.ipc
node_connection_type = ipc

# Beacon
beacon_url = http://localhost:5052

# Classifier
model_path = models/classifier_isotonic_20000_blocks.pkl
```

- create poetry environment:

```poetry install```

### __Backend__

- Build docker image via typing following command to your terminal\command line 
> `docker build -t api ./api`

### __Frontend__

- Build docker image via typing following command to your terminal\command line 
> `docker build -t frontend ./frontend`

## &#128204; Quick start

### __Data collection service__ and  __Analytics service__

```poetry run python data_collector.py
poetry run python censorship_analytics.py
```

### __Backend__

- Run docker container typing following command to your terminal\command line 
> `docker run --network host --name api -d api`
- Just enjoy your api running at localhost:8000

### __Frontend__

- Run docker container typing following command to your terminal\command line 
> `docker run --network host --name frontend -d frontend`
- Just enjoy your web application running at localhost:5173

## &#128204; Mongo DB metrics scheme 

The analytics module of the project utilizes a MongoDB database with several collections:
- ofac_addresses
- validators
- censored_txs
- validators_metrics
- block_numbers_slots
- processed_blocks

### ofac_addresses
<p>The <b>ofac_addresses</b> collection stores snapshots of sanctions lists.</p>

Example:

```
{
    timestamp: 1677196277,
    addresses: [
        '0xD691F27f38B395864Ea86CfC7253969B409c362d',
        ...
        '0x8576acc5c05d6ce88f4e49bf65bdf0c62f91353c'
    ]
}
```

### validators
<p>The <b>validators</b> collection contains information on known validators' public keys and validator pools.</p>

Example:

```
{
    pubkey: '0x81b4ae61a898396903897f94bea0e062c3a6925ee93d30f4d4aee93b533b49551ac337da78ff2ab0cfbb0adb380cad94',
    pool_name: 'Lido',
    name: 'Staking Facilities',
    timestamp: 1676729376
}
```

### censored_txs
<p>The <b>censored_txs</b> collection stores information about transactions that were censored</p>

<p> The <b><i>censored</i></b> field contains a list of block numbers and validators who did not include a transaction in a block, despite our classifier indicating that it should have been included. </p>

<p> The <b><i>non_ofac_compliant<i></b> field is set to <b><i>False</i></b> for transactions that are noncompliant with OFAC regulations. However, for transactions that are compliant with regulations but flagged as censored by our classifier, the non_ofac_compliant field will be set to <b><i>True<i></b>.</p>

Example:

```
{
    hash: '0xa4e6597135d9f3b7999170903e8068b8852668a9c789e052aad4f30b149d1814',
    censored: [
        {
            block_number: 16649638,
            validator: 'RockX'
        },
        {
            block_number: 16649639,
            validator: 'Other'
        },
        {
            block_number: 16649640,
            validator: 'Other'
        }
    ],
    first_seen: 1676651657,
    block_number: 16649641,
    block_ts: 1676651699,
    date: '17-02-23',
    non_ofac_compliant: true,
    validator: 'Simply Staking'
}
```

### validators_metrics

<p>The <b><i></i></b> collection contains the following information for each day:</p>
<p>- the number of blocks proposed by a validator - <b>num_blocks</b></p>
<p>- the number of compliant transactions in these blocks - <b>num_ofac_compliant_txs</b></p>
<p>- the total number of transactions in these blocks - <b>num_txs</b></p>
<p>- The <b>non_censored_blocks</b> field contains a list of block numbers proposed by the validator that have non-compliant  transactions in them. Can be omitted.</p>
<p>- The <b>non_ofac_compliant_txs</b> field contains a list of non-compliant transactions in these blocks. Can be omitted.</p>
<p>- The <b>censored_block</b> field is a list of blocks with censorship proposed by the validator. Can be omitted.</p>

```
{
    name: 'SkillZ',
    '17-02-23': {
        num_blocks: 41,
        num_ofac_compliant_txs: 6622,
        num_txs: 6624,
        non_censored_blocks: [
            16649665,
            16651173
        ],
        non_ofac_compliant_txs: [
            '0xf35893b1ad307c0936deafeb9c4b7830ac5f9b6c33c71b63584946c74805a37b',
            '0xc4c727a0dc9db3de4f6fd220532e55e3bf69fc7c7a9398574e4376255dc9745e'
        ]
    },
    '18-02-23': {
        num_blocks: 101,
        num_ofac_compliant_txs: 15032,
        num_txs: 15034,
        non_censored_blocks: [
            16654317,
            16658345
        ],
        non_ofac_compliant_txs: [
            '0xb9286c30a90d3e72ab71b2fbef5af2ba6e1f8b72a62a9c227c8b28751c75a73b',
            '0x20e99a9f32f9fde23868f63c02600730606847744b13db9a608b119ec900c10a'
        ],
        censored_block: [
            16655813
        ]
    }
}
```

## &#128204; API Reference

Thanks to the API, you can receive data without accessing the database and in a more convenient format

<b>API endpoint</b>: `/data/validators`</br>
<b>Parameters</b>: Api key - key string for api </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/validators?api_key=123`</br>
<b>Response example</b>: 
```
[
    {
        'pubkey':'0x81b4ae61a898396903897f94bea0e062c3a6925ee93d30f4d4aee93b533b49551ac337da78ff2ab0cfbb0adb380cad94',
        'pool_name': 'Lido',
        'name': 'Staking Facilities',
        'timestamp': 1676729376
    },
    {
        'pubkey': '0x953805708367b0b5f6710d41608ccdd0d5a67938e10e68dd010890d4bfefdcde874370423b0af0d0a053b7b98ae2d6ed',
        'pool_name': 'Lido',
        'name': 'Staking Facilities',
        'timestamp': 1676729376
    }
]
```

<b>API endpoint</b>: `/data/metrics`</br>
<b>Parameters</b>: Api key - key string for api </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/metrics?api_key=123`</br>
<b>Response example</b>: 
```
[
    {
        'name': 'Certus One',
        '17-02-23': {
            'num_blocks': 6,
            'num_ofac_compliant_txs': 956,
            'num_txs': 956
        },
        '18-02-23': {
            'num_blocks': 14,
            'num_ofac_compliant_txs': 1950,
            'num_txs': 1950
        }
    },
    {
        'name': 'InfStones',
        '17-02-23': {
            'num_blocks': 20,
            'num_ofac_compliant_txs': 3381,
            'num_txs': 3381
        },
        '18-02-23': {
            'num_blocks': 75,
            'num_ofac_compliant_txs': 10153,
            'num_txs': 10154,
            'censored_block': [
                16656151
            ],
            'non_censored_blocks': [
                16656383
            ],
            'non_ofac_compliant_txs': [
                '0x0e999d6fcfd15db925f1baf371eaa50f478205211b003c36a5cac23f36853413'
            ]
        }
    }
]
```

<b>API endpoint</b>: `/data/metrics_by_day`</br>
<b>Parameters</b>: Api key - key string for api, Date - date in dd-mm-yy format </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/metrics_by_day?api_key=123&date=18-02-23`</br>
<b>Response example</b>: 
```
[
    {
        'name': 'Figment',
        '18-02-23': {
            'num_blocks': 85,
            'num_ofac_compliant_txs': 12015,
            'num_txs': 12015,
            'censored_block': [
                16652200,
                16654567,
                16655187, 
                16655997
            ]
        }
    },
    {
        'name': 'RockX',
        '18-02-23': {
            'num_blocks': 91,
            'num_ofac_compliant_txs': 12273,
            'num_txs': 12274,
            'non_censored_blocks': [
                16653366
            ],
            'non_ofac_compliant_txs': [
                '0xe92207df0fa3d97fea2263f47186718b5212e0dd9d8e63422036669d7e2c00da'
            ],
            'censored_block': [
                16657321
            ]
        }
    }
]
```

<b>API endpoint</b>: `/data/metrics_by_validators`</br>
<b>Parameters</b>: Api key - key string for api, Names - validators' names </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/metrics_by_day?api_key=123&names=stakefish&names=BridgeTower`</br>
<b>Response example</b>: 
```
[
    {
        'name': 'stakefish',
        '17-02-23': {
            'num_blocks': 17,
            'num_ofac_compliant_txs': 2753,
            'num_txs': 2753},
            '18-02-23': {
                'num_blocks': 91,
                'num_ofac_compliant_txs': 9505,
                'num_txs': 9507,
                'non_censored_blocks': [
                    16653655, 
                    16656982
                ],
                'non_ofac_compliant_txs': [
                    '0x1e36ab8d3055f0b7f385d455a537b7885e1d874f620e0bcfb9478cc73aa377b0',
                    '0x020ccc01520f8378e2928a1977159eb997f2206cf0de4b11428d1bdae55fbeaa'
                ]
            }
        },
    {
        'name': 'BridgeTower',
        '17-02-23': {
            'num_blocks': 40,
            'num_ofac_compliant_txs': 6373,
            'num_txs': 6376,
            'non_censored_blocks': [
                16649944, 
                16649973, 
                16650400
            ],
            'non_ofac_compliant_txs': [
                '0x698fc76f971c1470c8e70bfa52cc4c3f6525756747c8770dd634b05b1c8e60c0',
                '0x52ee75fff1e152347482b6491334c2e1f3b18b88c5f353552c76d118da347302',
                '0x66a773542290c15d68f2748678906aad79c8c025c94955166cea906c00ef674a'
            ],
            'censored_block': [
                16651285
            ]
        },
        '18-02-23': {
            'num_blocks': 94,
            'num_ofac_compliant_txs': 13370,
            'num_txs': 13374,
            'non_censored_blocks': [
                16654535, 
                16655950
            ],
            'non_ofac_compliant_txs': [
                '0x44b9420c4a89e60eff7cbb6a9a10f087b2aa383fe9edecde8c73bf906034b903',
                '0xe09559639b8cde02d25c3bbfcbe880faf98044e0ee6167b46dd0c08afa361dea',
                '0x726034837fb82fc4323908a19273c05e5985b88ee70441e8e43c1bed18f30246',
                '0xd601760596ac3cac7a2cd6bdd94026907bc35324ed5d4d25b9a36ec9f803fa8b'
            ]
        }
    }
]
```

<b>API endpoint</b>: `/data/metrics_by_daterange`</br>
<b>Parameters</b>: Api key - key string for api, Start date - date in dd-mm-yy format, End date - date in dd-mm-yy format </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/metrics_by_daterange?api_key=123&start_date=16-02-23&end_date=17-02-23`</br>
<b>Response example</b>: 
```
[
    {
        'name': 'Blockdaemon',
        '17-02-23': {
            'num_blocks': 10,
            'num_ofac_compliant_txs': 1506,
            'num_txs': 1506
        }
    },
    {
        'name': 'Anyblock Analytics',
        '17-02-23': {
            'num_blocks': 15,
            'num_ofac_compliant_txs': 2256,
            'num_txs': 2256,
            'censored_block': [
                16651070
            ]
        }
    }
]
```

<b>API endpoint</b>: `/data/metrics_by_validators_by_day`</br>
<b>Parameters</b>: Api key - key string for api, Date - date in dd-mm-yy format, Names - validators' names </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/metrics_by_validators_by_day?api_key=123&date=17-02-23&names=Sigma Prime&names=Stakin`</br>
<b>Response example</b>: 
```
[
    {
        'name': 'Stakin',
        '17-02-23': {
            'num_blocks': 31,
            'num_ofac_compliant_txs': 4707,
            'num_txs': 4707
        }
    },
    {
        'name': 'Sigma Prime',
        '17-02-23': {
            'num_blocks': 21,
            'num_ofac_compliant_txs': 3454,
            'num_txs': 3454
        }
    }
]
```

<b>API endpoint</b>: `/data/metrics_by_validators_by_daterange`</br>
<b>Parameters</b>: Api key - key string for api, Start date - date in dd-mm-yy format, End date - date in dd-mm-yy format, Names - validators' names </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/metrics_by_validators_by_daterange?api_key=123&start_date=17-02-23&end_date=19-02-23&names=Stakely&names=ChainLayer`</br>
<b>Response example</b>: 
```
[
    {
        'name': 'Stakin',
        '17-02-23': {
            'num_blocks': 31,
            'num_ofac_compliant_txs': 4707,
            'num_txs': 4707
        },
        '18-02-23': {
            'num_blocks': 65,
            'num_ofac_compliant_txs': 9631,
            'num_txs': 9632,
            'non_censored_blocks': [16656772],
            'non_ofac_compliant_txs': [
                '0x64d519bbdae8f54784fec9e113d903f839df63bc9b38332f699ebb688f2ed940'
            ]
        }
    },
    {
        'name': 'Sigma Prime',
        '17-02-23': {
            'num_blocks': 21,
            'num_ofac_compliant_txs': 3454,
            'num_txs': 3454
        },
        '18-02-23': {
            'num_blocks': 32,
            'num_ofac_compliant_txs': 4468,
            'num_txs': 4468
        }
    }
]
```

<b>API endpoint</b>: `/data/censored_transactions`</br>
<b>Parameters</b>: Api key - key string for api </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/censored_transactions?api_key=123`</br>
<b>Response example</b>: 
```
[
    {
        "hash":"0x0a7eef822d16d7bfa45fe3387e4b7692311ab375ffa956582b17996a7062be3d",
        "censored":[],
        "first_seen":1676665298,
        "block_number":16650761.0,
        "block_ts":1676665307.0,
        "date":"17-02-23",
        "non_ofac_compliant":1.0,
        "validator":"Other"
    },
    {
        "hash":"0x1177c5dff2bd5d8abcdcc8cd72875675699b1c4543e1dccda8adaf3ccadb2650",
        "censored":[
            {
                "block_number":16651065,
                "validator":"Other"
            },
            {
                "block_number":16651066,
                "validator":"Other"
            }
        ],
        "first_seen":1676669047,
        "block_number":16651067.0,
        "block_ts":1676669075.0,
        "date":"17-02-23",
        "non_ofac_compliant":1.0,
        "validator":"Other"
    }
]
```

<b>API endpoint</b>: `/data/censored_transactions_by_day`</br>
<b>Parameters</b>: Api key - key string for api, Date - date in dd-mm-yy format </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/censored_transactions_by_day?api_key=123&date=17-02-23`</br>
<b>Response example</b>: 
```
[
    {
        "hash":"0x0a7eef822d16d7bfa45fe3387e4b7692311ab375ffa956582b17996a7062be3d",
        "censored":[],
        "first_seen":1676665298,
        "block_number":16650761.0,
        "block_ts":1676665307.0,
        "date":"17-02-23",
        "non_ofac_compliant":1.0,
        "validator":"Other"
    },
    {
        "hash":"0x1177c5dff2bd5d8abcdcc8cd72875675699b1c4543e1dccda8adaf3ccadb2650",
        "censored":[
            {
                "block_number":16651065,
                "validator":"Other"
            },
            {
                "block_number":16651066,
                "validator":"Other"
            }
        ],
        "first_seen":1676669047,
        "block_number":16651067.0,
        "block_ts":1676669075.0,
        "date":"17-02-23",
        "non_ofac_compliant":1.0,
        "validator":"Other"
    }
]
```

<b>API endpoint</b>: `/data/censored_transactions_by_daterange`</br>
<b>Parameters</b>: Api key - key string for api, Start date - date in dd-mm-yy format, End date - date in dd-mm-yy format </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/censored_transactions_by_daterange?api_key=123&start_date=17-02-23&end_date=19-02-23`</br>
<b>Response example</b>: 
```
[
    {
        "hash":"0x0a7eef822d16d7bfa45fe3387e4b7692311ab375ffa956582b17996a7062be3d",
        "censored":[],
        "first_seen":1676665298,
        "block_number":16650761.0,
        "block_ts":1676665307.0,
        "date":"17-02-23",
        "non_ofac_compliant":1.0,
        "validator":"Other"
    },
    {
        "hash":"0x1177c5dff2bd5d8abcdcc8cd72875675699b1c4543e1dccda8adaf3ccadb2650",
        "censored":[
            {
                "block_number":16651065,
                "validator":"Other"
            },
            {
                "block_number":16651066,
                "validator":"Other"
            }
        ],
        "first_seen":1676669047,
        "block_number":16651067.0,
        "block_ts":1676669075.0,
        "date":"17-02-23",
        "non_ofac_compliant":1.0,
        "validator":"Other"
    }
]
```

<b>API endpoint</b>: `/data/ofac_addresses`</br>
<b>Parameters</b>: Api key - key string for api </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/ofac_addresses?api_key=123`</br>
<b>Response example</b>: 
```
[
    {
        "timestamp":1676623295,
        "addresses":[
            "0xf4B067dD14e95Bab89Be928c07Cb22E3c94E0DAA",
            "0xCC84179FFD19A1627E79F8648d09e095252Bc418",
            "0xA160cdAB225685dA1d56aa342Ad8841c3b53f291",
            "0x09193888b3f38C82dEdfda55259A82C0E7De875E",
            ...
            "0xaf4c0B70B2Ea9FB7487C7CbB37aDa259579fe040",
            "0xD21be7248e0197Ee08E0c20D4a96DEBdaC3D20Af",
            "0xd47438C816c9E7f2E2888E060936a499Af9582b3",
            "0xd90e2f925DA726b50C4Ed8D0Fb90Ad053324F31b",
            "0x901bb9583b24d97e995513c6778dc6888ab6870e",
            "0x0E3A09dDA6B20aFbB34aC7cD4A6881493f3E7bf7"
        ]
    },
    {
        "timestamp":1676709695,
        "addresses":[
            "0xf4B067dD14e95Bab89Be928c07Cb22E3c94E0DAA",
            "0xCC84179FFD19A1627E79F8648d09e095252Bc418",
            "0xA160cdAB225685dA1d56aa342Ad8841c3b53f291",
            "0x09193888b3f38C82dEdfda55259A82C0E7De875E",
            "0xdf231d99Ff8b6c6CBF4E9B9a945CBAcEF9339178",
            ...
            "0xd90e2f925DA726b50C4Ed8D0Fb90Ad053324F31b",
            "0x901bb9583b24d97e995513c6778dc6888ab6870e",
            "0x0E3A09dDA6B20aFbB34aC7cD4A6881493f3E7bf7"
        ]
    }
]
```

<b>API endpoint</b>: `/data/ofac_addresses_by_day`</br>
<b>Parameters</b>: Api key - key string for api, Date - date in dd-mm-yy format </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/ofac_addresses_by_day?api_key=123&date=18-02-23`</br>
<b>Response example</b>: 
```
[
    {
        "timestamp":1676709695,
        "addresses":[
            "0xf4B067dD14e95Bab89Be928c07Cb22E3c94E0DAA",
            "0xCC84179FFD19A1627E79F8648d09e095252Bc418",
            "0xA160cdAB225685dA1d56aa342Ad8841c3b53f291",
            ...
            "0x901bb9583b24d97e995513c6778dc6888ab6870e",
            "0x0E3A09dDA6B20aFbB34aC7cD4A6881493f3E7bf7"
        ]
    }
]
```

<b>API endpoint</b>: `/data/ofac_addresses_by_daterange`</br>
<b>Parameters</b>: Api key - key string for api, Start date - date in dd-mm-yy format, End date - date in dd-mm-yy format </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/ofac_addresses_by_daterange?api_key=123&start_date=18-02-23&end_date=20-02-23`</br>
<b>Response example</b>: 
```
[
    {
        "timestamp":1676709695,
        "addresses":[
            "0xf4B067dD14e95Bab89Be928c07Cb22E3c94E0DAA",
            "0xCC84179FFD19A1627E79F8648d09e095252Bc418",
            "0xA160cdAB225685dA1d56aa342Ad8841c3b53f291",
            ...
            "0x901bb9583b24d97e995513c6778dc6888ab6870e",
            "0x0E3A09dDA6B20aFbB34aC7cD4A6881493f3E7bf7"
        ]
    }
]
```

## &#128204; Team



| <img src = "https://sun7.userapi.com/sun7-9/s/v1/ig2/nlmpctb21vUqfPkpUrX8aRmqhhQMyfYAwDrsXrVlduxzPmvyI8SW3luH2SR4fsUpLHPZCKdH_-QXEYtT5E3DqFUc.jpg?size=810x1080&quality=96&type=album" height = "300px"> | <img src = "https://sun7.userapi.com/sun7-9/s/v1/ig2/dQ01qNaBz_9WlD49Xdas0Q5N-G8y4AlaWKXHcPVA39WQWgALU6KD7OOaIVI1L1jivaIwVUcH1fEYP7_53KzPEDrX.jpg?size=810x1080&quality=96&type=album" height = "300px"> | <img src = "https://sun7.userapi.com/sun7-14/s/v1/ig2/eP7ic4XAgFhfGJO5ccrKfn63OS_fGrHEk-zL3G2Cw11pAy1Bs5gkZ1kx23gzQTYnlOMVLw9uYp562-RfTNoS4AAR.jpg?size=810x1080&quality=96&type=album" height = "300px"> |
|:---:|:---:|:---:|
| [Mikhail Gurevich](https://github.com/mikgur) | [Petr Korchagin](https://github.com/PetrovitchSharp) | [Evgenii Bezmen](https://github.com/flashlight101) | 
| tg: [@gurev](https://t.me/gurev) | tg: [@petrovitch_sharp](https://t.me/petrovitch_sharp) | tg: [@flashlight101](https://t.me/flashlight101) |

## &#128204; Community 



## &#128204; Acknowledgments

- Folks from [DRPC.org](https://drpc.org/) were kind enough to give us access to their archive node, which has been a huge help for our project!

## License

 [The MIT License](https://opensource.org/licenses/mit-license.php)
 