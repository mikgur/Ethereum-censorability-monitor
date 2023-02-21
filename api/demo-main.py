from fastapi import FastAPI
import uvicorn
import pandas as pd
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


app = FastAPI()


@app.get("/metrics/lido_validators_share/{period}")
async def get_lido_validators_share(period: str) -> JSONResponse:
    metrics = [
        {
            "name": "SkillZ",
            "ofac_compliant_share": 6.804227869744307,
            "ofac_non_compliant_share": 16.666666666666668,
        },
        {
            "name": "Certus One",
            "ofac_compliant_share": 0.761638299525919,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "InfStones",
            "ofac_compliant_share": 3.4312582575580945,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "DSRV",
            "ofac_compliant_share": 4.472682054869045,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Chorus One",
            "ofac_compliant_share": 3.944198336830652,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Blockscape",
            "ofac_compliant_share": 5.669542239838346,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Figment",
            "ofac_compliant_share": 9.13188777492811,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "RockX",
            "ofac_compliant_share": 3.928654698064817,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Simply Staking",
            "ofac_compliant_share": 7.282194761793736,
            "ofac_non_compliant_share": 16.666666666666668,
        },
        {
            "name": "Stakely",
            "ofac_compliant_share": 2.4481231056190254,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Kukis Global",
            "ofac_compliant_share": 2.1061630527706536,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "P2P.ORG - P2P Validator",
            "ofac_compliant_share": 2.572472215745706,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Staking Facilities",
            "ofac_compliant_share": 2.681277687106552,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Blockdaemon",
            "ofac_compliant_share": 3.3651977928032952,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Anyblock Analytics",
            "ofac_compliant_share": 3.6799564778114555,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "ChainLayer",
            "ofac_compliant_share": 3.2097614051449446,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "stakefish",
            "ofac_compliant_share": 4.659205720059066,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "BridgeTower",
            "ofac_compliant_share": 4.659205720059066,
            "ofac_non_compliant_share": 33.333333333333336,
        },
        {
            "name": "Nethermind",
            "ofac_compliant_share": 1.7525452708479055,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "CryptoManufaktur",
            "ofac_compliant_share": 1.760317090230823,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Prysmatic Labs",
            "ofac_compliant_share": 1.0336519779280329,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "HashQuark",
            "ofac_compliant_share": 2.8056267972332325,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Stakin",
            "ofac_compliant_share": 2.036216678324396,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Sigma Prime",
            "ofac_compliant_share": 2.957177275200124,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "Allnodes",
            "ofac_compliant_share": 5.230434444703505,
            "ofac_non_compliant_share": 16.666666666666668,
        },
        {
            "name": "Everstake",
            "ofac_compliant_share": 3.5478355483018573,
            "ofac_non_compliant_share": 16.666666666666668,
        },
        {
            "name": "RockLogic GmbH",
            "ofac_compliant_share": 2.895002720136784,
            "ofac_non_compliant_share": 0.0,
        },
        {
            "name": "ConsenSys Codefi",
            "ofac_compliant_share": 1.1735447268205488,
            "ofac_non_compliant_share": 0.0,
        },
    ]

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/metrics/lido_validators_ratio/{period}")
async def get_lido_validators_ratio(period: str) -> JSONResponse:
    metrics = [
        {"name": "SkillZ", "ratio": 2.4494574528840665},
        {"name": "Certus One", "ratio": 0.0},
        {"name": "InfStones", "ratio": 0.0},
        {"name": "DSRV", "ratio": 0.0},
        {"name": "Chorus One", "ratio": 0.0},
        {"name": "Blockscape", "ratio": 0.0},
        {"name": "Figment", "ratio": 0.0},
        {"name": "RockX", "ratio": 0.0},
        {"name": "Simply Staking", "ratio": 2.2886872998932764},
        {"name": "Stakely", "ratio": 0.0},
        {"name": "Kukis Global", "ratio": 0.0},
        {"name": "P2P.ORG - P2P Validator", "ratio": 0.0},
        {"name": "Staking Facilities", "ratio": 0.0},
        {"name": "Blockdaemon", "ratio": 0.0},
        {"name": "Anyblock Analytics", "ratio": 0.0},
        {"name": "ChainLayer", "ratio": 0.0},
        {"name": "stakefish", "ratio": 0.0},
        {"name": "BridgeTower", "ratio": 7.154295246038366},
        {"name": "Nethermind", "ratio": 0.0},
        {"name": "CryptoManufaktur", "ratio": 0.0},
        {"name": "Prysmatic Labs", "ratio": 0.0},
        {"name": "HashQuark", "ratio": 0.0},
        {"name": "Stakin", "ratio": 0.0},
        {"name": "Sigma Prime", "ratio": 0.0},
        {"name": "Allnodes", "ratio": 3.186478454680535},
        {"name": "Everstake", "ratio": 4.697699890470975},
        {"name": "RockLogic GmbH", "ratio": 0.0},
        {"name": "ConsenSys Codefi", "ratio": 0.0},
    ]

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/metrics/lido_vs_rest_share/{period}")
async def get_total_validators_ratio(period: str) -> JSONResponse:
    metrics = [
        {"pool": "lido", "ratio": 2.192818838890184},
        {"pool": "other pools", "ratio": 0.47894281203849876},
    ]

    res = jsonable_encoder(metrics)
    return JSONResponse(res)


@app.get("/metrics/latency")
async def get_latencies() -> JSONResponse:
    metrics = [
        {
            "start_date": "13-02-23",
            "end_date": "19-02-23",
            "censorship_latency": 29.86046511627907,
            "censorship_latency_without_lido_censorship": 15.348837209302326,
        }
    ]
    res = jsonable_encoder(metrics)
    return JSONResponse(res)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
