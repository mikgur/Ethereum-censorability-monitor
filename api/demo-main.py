from fastapi import FastAPI
import uvicorn
import pandas as pd 


app = FastAPI()

@app.get('/data/total_validators_share/{period}')
def get_total_validators_share(period: str):
    res = None 
    if period == 'last_week':
        res = [{
            'validator': 'CryptoPetrovitch',
            'ofac_share': 0.001 * 100,
            'non_ofac_share': 0.0025 * 100
        },
        {
            'validator': 'MishaEth.com',
            'ofac_share': 0.0021 * 100,
            'non_ofac_share': 0.001 * 100
        },
        {
            'validator': 'CyberJenya',
            'ofac_share': 0.0015 * 100,
            'non_ofac_share': 0.0015 * 100
        },
        {
            'validator': 'Random LIDO validator',
            'ofac_share': 0.0009 * 100,
            'non_ofac_share': 0.0008 * 100
        }]
    if period == 'last_month':
        res = [{
            'validator': 'CryptoPetrovitch',
            'ofac_share': 0.001 * 100,
            'non_ofac_share': 0.0025 * 100
        },
        {
            'validator': 'MishaEth.com',
            'ofac_share': 0.0021 * 100,
            'non_ofac_share': 0.001 * 100
        },
        {
            'validator': 'CyberJenya',
            'ofac_share': 0.0015 * 100,
            'non_ofac_share': 0.0015 * 100
        },
        {
            'validator': 'Random LIDO validator',
            'ofac_share': 0.0009 * 100,
            'non_ofac_share': 0.0008 * 100
        }]
        
    return res

@app.get("/data/lido_validators_share/{period}")
def get_lido_validators_share(period: str):
    res = None 
    if period == 'last_week':
        res = [{
            'validator': 'CryptoPetrovitch',
            'ofac_share': 0.001 * 25 * 100,
            'non_ofac_share': 0.0025 * 25 * 100
        },
        {
            'validator': 'MishaEth.com',
            'ofac_share': 0.0021 * 25 * 100,
            'non_ofac_share': 0.001 * 25 * 100
        },
        {
            'validator': 'CyberJenya',
            'ofac_share': 0.0015 * 25 * 100,
            'non_ofac_share': 0.0015 * 25 * 100
        },
        {
            'validator': 'Random LIDO validator',
            'ofac_share': 0.0009 * 25 * 100,
            'non_ofac_share': 0.0008 * 25 * 100
        }]
    if period == 'last_month':
            res = [{
            'validator': 'CryptoPetrovitch',
            'ofac_share': 0.001 * 25 * 100,
            'non_ofac_share': 0.0025 * 25 * 100
        },
        {
            'validator': 'MishaEth.com',
            'ofac_share': 0.0021 * 25 * 100,
            'non_ofac_share': 0.001 * 25 * 100
        },
        {
            'validator': 'CyberJenya',
            'ofac_share': 0.0015 * 25 * 100,
            'non_ofac_share': 0.0015 * 25 * 100
        },
        {
            'validator': 'Random LIDO validator',
            'ofac_share': 0.0009 * 25 * 100,
            'non_ofac_share': 0.0008 * 25 * 100
        }]
        
    return res

@app.get('/data/lido_validators_ratio/{period}')
def get_lido_validators_ratio(period: str):
    res = None 
    if period == 'last_week':
        res = [{
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
    if period == 'last_month':
        res = [{
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
        
    return res

@app.get('/data/total_validators_ratio/{period}')
def get_total_validators_ratio(period: str):
    res = None 
    if period == 'last_week':
        res = [{
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
    if period == 'last_month':
        res = [{
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
        
    return res

@app.get('/data/overall_ratios/{period}')
def get_overall_ratios(period: str):
    res = None 
    if period == 'last_week':
        res = [{
            'pool': 'Lido',
            'ratio': 0.001 / 0.0008
        },
        {
            'pool': 'RocketPool',
            'ratio': 0.0004 / 0.00036
        }]
    if period == 'last_month':
        res = [{
            'pool': 'Lido',
            'ratio': 0.0011 / 0.00085
        },
        {
            'pool': 'RocketPool',
            'ratio': 0.00044 / 0.00034
        }]
        
    return res

@app.get('/data/latency/{period}')
def get_mean_latency(period: str):
    res = None
    if period == 'last_week':
        res = {
            'mean_non_ofac_waiting': 9,
            'mean_ofac_latency': 31,
            'mean_ofac_latency_with_full_lido_censorship': 34,
            'mean_ofac_latency_without_lido_censorship': 28
        }
    if period == 'last_month':
        res = {
            'period': 'last_month',
            'mean_non_ofac_waiting': 8,
            'mean_ofac_latency': 30,
            'mean_ofac_latency_with_full_lido_censorship': 35,
            'mean_ofac_latency_without_lido_censorship': 26
        }
        
    return res
   
@app.get('/data/censorship_percentage/{period}')
def get_censorship_percentage(period: str):
    res = None
    if period == 'last_week':
        res = {
            'overall_censorship': 0.001,
            'ofac_censorship': 0.4187
        }
    if period == 'last_month':
        res =  {
            'overall_censorship': 0.0012,
            'ofac_censorship': 0.4411
        }
        
    return res
     
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
