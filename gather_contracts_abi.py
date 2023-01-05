import json
import pickle
import time

import pandas as pd
import requests
import tqdm


def main():
    contracts_df = pd.read_csv('contracts_221220_221231.csv')
    contracts_abi = {}
    try:
        with open('contracts_abi.pickle', 'rb') as f:
            contracts_abi = pickle.load(f)
    except Exception:
        print(f'contracts_abi.pickle not loaded!')
    etherscan_apikey = '4756JYW3FR59XPESIE4KTRX24WG46GVY6M'
    url = 'https://api.etherscan.io/api'

    for i, contract_address in tqdm.tqdm(enumerate(contracts_df['contract'].values), total=len(contracts_df)):  # noqa E501
        if contract_address in contracts_abi:
            continue

        payload = {'module': 'contract',
                   'action': 'getabi',
                   'address': contract_address,
                   'apikey': etherscan_apikey}
        r = requests.get(f'{url}', params=payload)
        try:
            if r.json()['result'] == 'Contract source code not verified':
                contracts_abi[contract_address] = 'Contract source code not verified' # noqa E501
            else:
                abi = json.loads(r.json()['result'])
                contracts_abi[contract_address] = abi
        except json.decoder.JSONDecodeError:
            contracts_abi[contract_address] = 'JSONDecodeError'
            print(f'JSONDecodeError: {contract_address} {r.text}')
        if (i + 1) % 5 == 0:
            time.sleep(5)
        if (i + 1) % 5 == 0:
            with open('contracts_abi.pickle', 'wb') as f:
                pickle.dump(contracts_abi, f)
            print(f'Checkpoint saved: {i + 1}')


if __name__ == '__main__':
    main()
