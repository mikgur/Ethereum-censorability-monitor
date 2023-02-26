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
  <a href=#-project_components> Project Components: </a> |
  <a href=#-metrics> Metrics </a> |
  <a href=#-installation> Installation </a> |
  <a href=#-quick-start> Quick Start </a> |
  <a href=#-mongo_db_metrics_scheme> Mongo DB metrics scheme  </a> |
  <a href=#-community> Community </a>
  <a href=#-acknowledgments> Acknowledgments </a>
</h4>

-----------------------------------------------
## &#128204; Problem

  The problem of censorship for non compliant transactions on the Ethereum blockchain is that certain transactions may be blocked or censored by node operators or validators who comply with some lists of forbidden addresses.

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
<b>Parameters</b>: None </br>
<b>Query example</b>: `http://<your_domain>:<your_port>/data/validators`</br>
<b>Response example</b>: 
```

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
 