from fastapi import FastAPI
import uvicorn
import pandas as pd 


app = FastAPI()

tr_data = pd.read_csv('../data/merged_221220_221231_with_contracts.csv')
lido_tx = tr_data[tr_data['validator_type'] == 'Lido']
lido_validators_total_tx = lido_tx.groupby(['validator_name', 'is_ofac']).agg({'tx_hash': 'count'}).reset_index()

lido_validators_total_tx['is_ofac'] = lido_validators_total_tx['is_ofac'].apply(lambda x: 'OFAC' if x else 'NON OFAC')

total_tx = len(tr_data)
total_ofac_tx = len(tr_data[tr_data['is_ofac']])

lido_validators_total_tx.loc[lido_validators_total_tx['is_ofac'] == 'OFAC', 'tx_hash'] /= total_ofac_tx
lido_validators_total_tx.loc[lido_validators_total_tx['is_ofac'] =='NON OFAC', 'tx_hash'] /= (total_tx - total_ofac_tx)

lido_validators_total_tx = lido_validators_total_tx[['is_ofac','tx_hash', 'validator_name']]



@app.get("/data")
def get_validators_data():
    return lido_validators_total_tx.to_json()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)