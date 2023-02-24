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
![3](https://img.shields.io/github/stars/Deeploid-Meta/deeploid-mini-cli?color=ccf)

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

- Сensorship latency
- Сensorship latency adjusted by Lido censorship latency
- Validator’s compliant\Non compliant transactions share
- Validator’s compliant\Non compliant ratio
- Lido compliant\Non compliant ratio

Please find details in our [notion page](https://accidental-eyelash-d3a.notion.site/Transaction-analysis-and-metrics-calculation-991b4e30fbc146469398860073547016)

## &#128204; Installation

### __Data collection service__ and  __Analytics service__

- create __.env file__, example (you can use same MongoDB instance for both _db_collector_ and _db_analytics_):

        # MongoDB
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

- create poetry environment:

        poetry install

### __Backend__ and  __Frontend__

        HOW TO INSTALL

## &#128204; Quick start

### __Data collection service__ and  __Analytics service__

        poetry run python data_collector.py
        poetry run python censorship_analytics.py

### __Backend__ and  __Frontend__

        HOW TO RUN
## &#128204; Mongo DB metrics scheme 

## &#128204; Community 

## &#128204; Acknowledgments

- Folks from [DRPC.org](https://drpc.org/) were kind enough to give us access to their archive node, which has been a huge help for our project!

## License

 [The MIT License](https://opensource.org/licenses/mit-license.php)
 