from fastapi import FastAPI
import uvicorn
import pandas as pd 


app = FastAPI()

@app.get('/data/total_validators_share')
def get_total_validators_share():
    return [{
        'validator': 'CryptoPetrovitch',
        'ofac_share': 0.001,
        'non_ofac_share': 0.0025
    },
    {
        'validator': 'MishaEth.com',
        'ofac_share': 0.0021,
        'non_ofac_share': 0.001
    },
    {
        'validator': 'CyberJenya',
        'ofac_share': 0.0015,
        'non_ofac_share': 0.0015
    },
    {
        'validator': 'Random LIDO validator',
        'ofac_share': 0.0009,
        'non_ofac_share': 0.0008
    }]

@app.get("/data/lido_validators_share")
def get_lido_validators_share():
    return [{
        'validator': 'CryptoPetrovitch',
        'ofac_share': 0.001 * 25,
        'non_ofac_share': 0.0025 * 25
    },
    {
        'validator': 'MishaEth.com',
        'ofac_share': 0.0021 * 25,
        'non_ofac_share': 0.001 * 25
    },
    {
        'validator': 'CyberJenya',
        'ofac_share': 0.0015 * 25,
        'non_ofac_share': 0.0015 * 25
    },
    {
        'validator': 'Random LIDO validator',
        'ofac_share': 0.0009 * 25,
        'non_ofac_share': 0.0008 * 25
    }]

@app.get('/data/lido_validators_ratio')
def get_lido_validators_ratio():
    return [{
        'validator': 'CryptoPetrovitch',
        'ratio': 0.001 / 0.0025
    },
    {
        'validator': 'MishaEth.com',
        'ratio': 0.0021 / 0.001,
    },
    {
        'validator': 'CyberJenya',
        'ratio': 0.0015 / 0.0015
    },
    {
        'validator': 'Random LIDO validator',
        'ratio': 0.0009 / 0.0008
    }]

@app.get('/data/total_validators_ratio')
def get_total_validators_ratio():
    return [{
        'validator': 'CryptoPetrovitch',
        'ratio': 0.001 / 0.0025
    },
    {
        'validator': 'MishaEth.com',
        'ratio': 0.0021 / 0.001,
    },
    {
        'validator': 'CyberJenya',
        'ratio': 0.0015 / 0.0015
    },
    {
        'validator': 'Random LIDO validator',
        'ratio': 0.0009 / 0.0008
    }]

@app.get('/data/overall_ratios')
def get_overall_ratios():
    return [{
        'pool': 'Lido',
        'ratio': 0.001 / 0.0008
    },
    {
        'pool': 'RocketPool',
        'ratio': 0.0004 / 0.00036
    }]

@app.get('/data/latency')
def get_mean_latency():
    return{
        'mean_latency': 31,
        'mean_latency_with_full_censorship': 34,
        'mean_latency_without_censorship': 28
    }
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    