from fastapi import FastAPI
import uvicorn
import pandas as pd 


app = FastAPI()

tr_data = pd.read_csv('../data/merged_221220_221231_with_contracts.csv')

@app.get('/data/total_validators_share')
def get_total_validators_share():
    lido_tx = tr_data[tr_data['validator_type'] == 'Lido']
    lido_validators_total_tx = lido_tx.groupby(['validator_name', 'is_ofac']).agg({'tx_hash': 'count'}).reset_index()

    total_tx = len(tr_data)
    total_ofac_tx = len(tr_data[tr_data['is_ofac']])

    lido_validators_total_tx.loc[lido_validators_total_tx['is_ofac'] == 'OFAC', 'tx_hash'] /= total_ofac_tx
    lido_validators_total_tx.loc[lido_validators_total_tx['is_ofac'] =='NON OFAC', 'tx_hash'] /= (total_tx - total_ofac_tx)

    lido_validators_total_tx = lido_validators_total_tx[['is_ofac','tx_hash', 'validator_name']]
    
    validators_list = lido_validators_total_tx.validator_name.unique()
    
    records = []
    
    for val in validators_list:
        rec = lido_validators_total_tx.query(f'validator_name == "{val}"')
        try:
            non_ofac_share = rec[~rec.is_ofac].tx_hash.values[0]
        except: 
            non_ofac_share = 0
        
        try:
            ofac_share = rec[rec.is_ofac].tx_hash.values[0]
        except:
            ofac_share = 0
            
        records.append({
            'validator': val,
            'ofac_share': ofac_share,
            'non_ofac_share': non_ofac_share
        })
        
    return records

@app.get("/data/lido_validators_share")
def get_lido_validators_share():
    lido_tx = tr_data[tr_data['validator_type'] == 'Lido']
    lido_validators_total_tx = lido_tx.groupby(['validator_name', 'is_ofac']).agg({'tx_hash': 'count'}).reset_index()
    
    lido_validators_total_tx.loc[lido_validators_total_tx['is_ofac'], 'tx_hash'] /= lido_validators_total_tx[lido_validators_total_tx['is_ofac']]['tx_hash'].sum()
    lido_validators_total_tx.loc[~lido_validators_total_tx['is_ofac'], 'tx_hash'] /= lido_validators_total_tx[~lido_validators_total_tx['is_ofac']]['tx_hash'].sum()
    
    lido_validators_total_tx = lido_validators_total_tx[['is_ofac','tx_hash', 'validator_name']]
    
    validators_list = lido_validators_total_tx.validator_name.unique()
    
    records = []
    
    for val in validators_list:
        rec = lido_validators_total_tx.query(f'validator_name == "{val}"')
        try:
            non_ofac_share = rec[~rec.is_ofac].tx_hash.values[0]
        except: 
            non_ofac_share = 0
        
        try:
            ofac_share = rec[rec.is_ofac].tx_hash.values[0]
        except:
            ofac_share = 0
            
        records.append({
            'validator': val,
            'ofac_share': ofac_share,
            'non_ofac_share': non_ofac_share
        })
        
    return records

@app.get('/data/lido_validators_ratio')
def get_lido_validators_ratio():
    lido_tx = tr_data[tr_data['validator_type'] == 'Lido']
    lido_validators_total_tx = lido_tx.groupby(['validator_name', 'is_ofac']).agg({'tx_hash': 'count'}).reset_index()
    
    lido_validators_total_tx.loc[lido_validators_total_tx['is_ofac'], 'tx_hash'] /= lido_validators_total_tx[lido_validators_total_tx['is_ofac']]['tx_hash'].sum()
    lido_validators_total_tx.loc[~lido_validators_total_tx['is_ofac'], 'tx_hash'] /= lido_validators_total_tx[~lido_validators_total_tx['is_ofac']]['tx_hash'].sum()
    
    lido_validators_total_tx = lido_validators_total_tx[['is_ofac','tx_hash', 'validator_name']]
    
    validators_list = lido_validators_total_tx.validator_name.unique()
    
    records = []
    
    for val in validators_list:
        rec = lido_validators_total_tx.query(f'validator_name == "{val}"')
        try:
            non_ofac_share = rec[~rec.is_ofac].tx_hash.values[0]
        except: 
            non_ofac_share = 0
        
        try:
            ofac_share = rec[rec.is_ofac].tx_hash.values[0]
        except:
            ofac_share = 0.5
            
        records.append({
            'validator': val,
            'ratio': ofac_share / non_ofac_share
        })
        
    return records

@app.get('/data/total_validators_ratio')
def get_total_validators_ratio():
    lido_tx = tr_data[tr_data['validator_type'] == 'Lido']
    lido_validators_total_tx = lido_tx.groupby(['validator_name', 'is_ofac']).agg({'tx_hash': 'count'}).reset_index()
    
    lido_validators_total_tx.loc[lido_validators_total_tx['is_ofac'], 'tx_hash'] /= lido_validators_total_tx[lido_validators_total_tx['is_ofac']]['tx_hash'].sum()
    lido_validators_total_tx.loc[~lido_validators_total_tx['is_ofac'], 'tx_hash'] /= lido_validators_total_tx[~lido_validators_total_tx['is_ofac']]['tx_hash'].sum()
    
    lido_validators_total_tx = lido_validators_total_tx[['is_ofac','tx_hash', 'validator_name']]
    
    validators_list = lido_validators_total_tx.validator_name.unique()
    
    records = []
    
    for val in validators_list:
        rec = lido_validators_total_tx.query(f'validator_name == "{val}"')
        try:
            non_ofac_share = rec[~rec.is_ofac].tx_hash.values[0]
        except: 
            non_ofac_share = 0
        
        try:
            ofac_share = rec[rec.is_ofac].tx_hash.values[0]
        except:
            ofac_share = 0
            
        records.append({
            'validator': val,
            'ratio': ofac_share / non_ofac_share
        })
        
    lido_tx = tr_data[tr_data['validator_type'] == 'Lido']
    lido_validators_total_tx = lido_tx\
        .groupby(['validator_name', 'is_ofac'])\
            .agg({'tx_hash': 'count'})\
                .groupby('is_ofac')\
                    .agg({'tx_hash': 'sum'})\
                        .reset_index()
    
    lido_validators_total_tx.loc[lido_validators_total_tx['is_ofac'], 'tx_hash'] /= lido_validators_total_tx[lido_validators_total_tx['is_ofac']]['tx_hash'].sum()
    lido_validators_total_tx.loc[~lido_validators_total_tx['is_ofac'], 'tx_hash'] /= lido_validators_total_tx[~lido_validators_total_tx['is_ofac']]['tx_hash'].sum()
        
    overall_non_ofac_share = lido_validators_total_tx[~lido_validators_total_tx.is_ofac].tx_hash.values[0]
    overall_ofac_share = lido_validators_total_tx[lido_validators_total_tx.is_ofac].tx_hash.values[0]
    
    records.append({
        'validator': 'LIDO overall',
        'ratio': overall_non_ofac_share / overall_ofac_share
    })    
    
    return records


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
    
