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
  <a href=#-project-components> Project Components </a> |
  <a href=#-metrics> Metrics </a> |
  <a href=#-installation> Installation </a> |
  <a href=#-quick-start> Quick Start </a> |
  <a href=#-mongo-db-metrics-scheme> Mongo DB metrics scheme  </a> |
  <a href=#-open-dataset> Open Dataset  </a> |
  <a href=#-team> Team  </a> |
  <a href=#-acknowledgments> Acknowledgments </a>
</h4>

-----------------------------------------------
## &#128204; Problem

  The problem of censorship for non compliant transactions on the Ethereum blockchain is that certain transactions may be blocked or censored by node operators or validators who comply with OFAC sanctions list which contains 'forbidden' cryptowallet addresses.

## &#128204; LEGO grant

[Lido RFP Ethereum Censorability Monitor](https://research.lido.fi/t/rfp-ethereum-censorability-monitor/3330)

Our project meets the first grant criteria in the following ways:

- We propose several metrics for tracking service degradation for censorable transactions, please refer to section <a href=#-metrics> Metrics </a> for more info.

- Our platform tracks the impact of Lido and Lido’s node operators on service degradation. (e.g. <a href=#4-censorship-latency>Censorship Latency</a> and <a href=#5-censorship-latency-if-lido-was-completely-non-censoring>Censorship Latency if Lido was completely non-censoring</a>)

- We have developed an API to access our data, and we can provide an API key to it upon request, for more info please refer to <a href=#-api-reference> API Reference </a> section.

- Our project has been designed to be easily maintainable by a small team of developers (1-2 in total), with low complexity and cost.

- We compare impact of Lido and Lido’s node operators to other staking pools, where applicable. (e.g. <a href=#1-non-ofac-compliance-and-ofac-compliance-ratio-metrics>Non-OFAC Compliance and OFAC Compliance Ratio Metrics</a>, <a href=#2-censorship-resistance-index>Censorship Resistance Index</a>)

- Our project is open-source.

## &#128204; Project Components

  #### Project Components:

1. __Data collection service__ - includes _data_collector.py_ and _censorability_monitor_ module. This component collects data from the mempool and blockchain.
2. __Analytics service__ - includes _censorship_analytics.py_ and _censorability_monitor_ module. This component gathers data from various sources, evaluates censorship, and calculates metrics.
3. __Backend__ - serves as the bridge between the analytics module and the frontend. It exposes an API that the frontend can use to request data and metrics.
4. __Frontend__ - serves as dashboard with provided cenbsorship metrics.
5. __Monitoring__ - service module for monitoring the status of system components.

<p align="center">
  <img src="https://raw.githubusercontent.com/mikgur/Ethereum-censorability-monitor/feature/documentation/img/structure.png" align="middle"  width="600" />
</p>

## &#128204; Metrics

We proposed following metrics:

### <b>1) Non-OFAC Compliance and OFAC Compliance Ratio Metrics</b>

For each validator we calculate:

- The Non-OFAC Compliance Ratio is the percentage of transactions across the Ethereum blockchain that are not compliant with OFAC regulations and are included in blocks proposed by a validator.
- The OFAC Compliance Ratio is the percentage of transactions across the Ethereum blockchain that are compliant with OFAC regulations and are included in blocks proposed by a validator.

These metrics help us understand how likely a validator is to include transactions that violate OFAC regulations compared to those that comply with them.

_Example of metric calculation:_

Let's say that for the period, there were a total of 100,000 compliant transactions and 1,000 non-compliant transactions on the Ethereum network. Our validator included 500 compliant transactions and 2 non-compliant transactions in their blocks.

> Validator’s OFAC Compliance Ratio:  500 / 100,000 = 0.5%

> Validator’s Non-OFAC Compliance Ratio:  2 / 1,000 = 0.2%


### <b>2) Censorship Resistance Index</b>

The metric is the ratio of the share of non-OFAC compliant transactions included by a validator to the share of OFAC compliant transactions included by the same validator. This metric provides insight into whether a particular validator is more likely to include non-compliant transactions in blocks compared to compliant transactions.

The possible values of this index range from zero to infinity. An index of 1.0 means that the validator includes non-compliant and compliant transactions at the same rate. An index greater than 1.0 means that the validator includes non-compliant transactions more often than compliant transactions. Conversely, an index less than 1.0 indicates that the validator includes non-compliant transactions less frequently than compliant transactions. Overall, a low Censorship Resistance Index could be an indication of potential censorship by a validator.

_Example of metric calculation:_

> A = OFAC Compliance Ratio calculated for given Lido validator (for example 1%)
>
> B = NON-OFAC Compliance Ratio calculated for given Lido validator (for example 0.5%)
>
> Censorship resistance index for this validator = B / A = 0.5 / 1 = 0.5
> 
> Based on the obtained value we can assume that this validator censors transactions


### <b>3) Lido Censorship Resistance Index and Non-Lido validators Censorship Resistance Index</b>

Censorship Resistance Index is calculated for all Lido validators and compared to all other known liquid staking pools in total.

_Example of metric calculation:_

> A = OFAC Compliance Ratio calculated for all Lido validators in total (as if they are one big validator)
>
> B = NON-OFAC Compliance Ratio calculated for all Lido validators in total (as if they are one big validator)
>
> Lido metric = B / A

> C = OFAC Compliance Ratio calculated for all stakefish validators in total (as if they are one big validator)
>
> D = NON-OFAC Compliance Ratio calculated for all stakefish validators in total (as if they are one big validator)
>
> Stakefish validators metric = D / C


### <b>4) Average Censorship Latency</b>

The Average Censorship Latency metric measures the difference in average waiting time for transactions with similar features, except for their OFAC compliance status. We use a binary classifier with high accuracy to predict the number of blocks for which non-OFAC compliant transactions were not included due to censorship. This number is then multiplied by 12 to calculate the Censorship Latency metric.

_Example of metric calculation:_

> Suppose there are 3 transactions under the letters A-C and a list of blocks that they did not appear in due to censorship (the list can be empty, since not all transactions affecting addresses on the OFAC list are censored). For convenience, we present it in the form of a table.

| Transaction | Blocks in which the transaction has been censored | Validators who validated the blocks |
| --- | --- | --- |
| A | 1, 2, 3, 4 | Non-Lido validator, Non-Lido validator, Lido validator, Non-Lido validator |
| B | - | - |
| A | 1, 3, 4, 5 | Non-Lido validator, Lido validator, Non-Lido validator, Lido Validator |

> In total we have 8 censorship blocks for 3 transactions. Multiply the number of blocks by 12 and divide by the number of transactions.
>
> As a result, for these transactions, the Average Censorship Latency metric will have a value of 32 seconds.

### <b>5) Average Censorship Latency if Lido was completely non-censoring</b>

We also compute a modified version of the Average Censorship Latency metric by assuming that the Lido validators were completely non-censoring. This adjusted metric helps to understand the impact of censorship by other validators on the overall network.

_Example of metric calculation:_

> Using the previous table, assume that Lido validators were to include transactions in the blocks they validate.
>
> In total, we have only 3 censorship blocks for 3 transactions. Multiply by 12 and we get the value of Average Censorship Latency if Lido was completely non-censoring equal to 12 seconds.


Please find details in our [notion page](https://accidental-eyelash-d3a.notion.site/Transaction-analysis-and-metrics-calculation-991b4e30fbc146469398860073547016)

### <b>6) Average Censorship Latency for censored transactions</b>

The Average Censorship Latency for censored transactions differs from the previous metric in that it does not take into account those transactions involving addresses on OFAC's list that were not ultimately censored and entered the blockchain when they should have.

_Example of metric calculation:_

> Using the previous table, we will ignore transaction B since it has not been censored.
>
> As a result, we have 8 censorship blocks for 2 transactions. Multiply by 12 and we get the value of Average Censorship Latency for censored transactions equal to 48 seconds. 

### <b>7) Average Censorship Latency for censored transactions if Lido was completely non-censoring</b>

This metric is a modified version of theAverage Censorship Latency for censored transactions by assuming that the Lido validators were completely non-censoring. This adjusted metric helps to understand the impact of censorship by other validators on the overall network.

_Example of metric calculation:_

> Using the previous table, assume that Lido validators were to include transactions in the blocks they validate
>
> In total, we have only 3 censorship blocks for 2 transactions. Multiply by 12 and we get the value of Average Censorship Latency if Lido was completely non-censoring, equal to 18 seconds.

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

## &#128204; Open Dataset

Here is a [dataset of Ethereum transactions](https://www.kaggle.com/datasets/mgurevich/ethereum-transactions-with-first-seen-timestamp) that includes compliance statuses, validators (all the information we could gather), and the timestamp of when they were first seen in the mempool.

## &#128204; Team

| <img src = "https://sun7.userapi.com/sun7-9/s/v1/ig2/nlmpctb21vUqfPkpUrX8aRmqhhQMyfYAwDrsXrVlduxzPmvyI8SW3luH2SR4fsUpLHPZCKdH_-QXEYtT5E3DqFUc.jpg?size=810x1080&quality=96&type=album" height = "300px"> | <img src = "https://sun7.userapi.com/sun7-9/s/v1/ig2/dQ01qNaBz_9WlD49Xdas0Q5N-G8y4AlaWKXHcPVA39WQWgALU6KD7OOaIVI1L1jivaIwVUcH1fEYP7_53KzPEDrX.jpg?size=810x1080&quality=96&type=album" height = "300px"> | <img src = "https://sun7.userapi.com/sun7-14/s/v1/ig2/eP7ic4XAgFhfGJO5ccrKfn63OS_fGrHEk-zL3G2Cw11pAy1Bs5gkZ1kx23gzQTYnlOMVLw9uYp562-RfTNoS4AAR.jpg?size=810x1080&quality=96&type=album" height = "300px"> |
|:---:|:---:|:---:|
| [Mikhail Gurevich](https://github.com/mikgur) | [Petr Korchagin](https://github.com/PetrovitchSharp) | [Evgenii Bezmen](https://github.com/flashlight101) | 
| tg: [@gurev](https://t.me/gurev) | tg: [@petrovitch_sharp](https://t.me/petrovitch_sharp) | tg: [@flashlight101](https://t.me/flashlight101) |

## &#128204; Acknowledgments

- Folks from [DRPC.org](https://drpc.org/) were kind enough to give us access to their archive node, which has been a huge help for our project!
- Folks from [Blocknative](https://www.blocknative.com) provided us a historical mempool data

## License

 [The MIT License](https://opensource.org/licenses/mit-license.php)
 
