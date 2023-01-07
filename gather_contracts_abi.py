import asyncio
import json
import logging
import logging.config
import pickle
import time

import aiohttp
import pandas as pd
import yaml

with open('logging.yaml', 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


async def main():
    contracts_df = pd.read_csv('contracts_221220_221231.csv')
    contracts_abi = {}
    try:
        with open('contracts_abi.pickle', 'rb') as f:
            contracts_abi = pickle.load(f)
    except Exception as e:
        logger.info(f'contracts_abi.pickle not loaded! {e}')
    etherscan_apikey = ''
    url = 'https://api.etherscan.io/api'

    contract_addresses = contracts_df['contract'].values
    i = 0

    while i < len(contract_addresses):
        async with aiohttp.ClientSession() as client:
            logger.info(f'i = {i}')
            t1 = time.time()

            # Пропускаем все контракты, для которых уже есть ABI
            batch = []
            while i < len(contract_addresses) and len(batch) < 5:
                if contract_addresses[i] not in contracts_abi:
                    batch.append(contract_addresses[i])
                i += 1

            # Создаем запросы
            tasks = []
            for contract_address in batch:
                task_url = f'{url}?module=contract&action=getabi&address={contract_address}&apikey={etherscan_apikey}'  # noqa E501
                tasks.append(asyncio.create_task(client.get(task_url)))
            original_result = []

            # Пытаемся выполнить запросы 5 раз
            attempt = 0
            while len(original_result) == 0 and attempt < 5:
                try:
                    t2 = time.time()
                    original_result = await asyncio.gather(*tasks)
                    logger.info(f'Gather time: {time.time() - t2:0.2f}')
                except Exception as e:
                    original_result = []
                    logger.info(f'Error i = {i}: {e}')
                finally:
                    attempt += 1
            if len(batch) != len(original_result):
                logger.info(f'Batch size: {len(batch)} responses: {len(original_result)}') # noqa E501

            # Обрабатываем ответы
            for j, r in enumerate(original_result):
                if r.status != 200:
                    print(f'r.status = {r.status}')
                    continue
                content = await r.content.read()
                json_content = json.loads(content)
                result = json_content['result']
                try:
                    if result == 'Contract source code not verified':
                        contracts_abi[batch[j]] = 'Contract source code not verified' # noqa E501
                    else:
                        abi = json.loads(result)
                        contracts_abi[batch[j]] = abi
                except json.decoder.JSONDecodeError:
                    contracts_abi[batch[j]] = 'JSONDecodeError'
                    logger.info(f'JSONkDecodeErr: {contract_address} {result}')
            # у Etherscan есть ограничение на 5 запросов в секунду
            if time.time() - t1 < 1:
                await asyncio.sleep(1)
            # Сохраняем промежуточный результат
            with open('contracts_abi.pickle', 'wb') as f:
                pickle.dump(contracts_abi, f)
        if attempt == 5:
            logger.info('Fetching from etherscan failed')
            await asyncio.sleep(5)
        logger.info(f'Checkpoint saved: {i} time: {time.time() - t1:0.2f}')
    return


if __name__ == '__main__':
    asyncio.run(main())
