import logging
from typing import List

from web3.auto import Web3

logger = logging.getLogger(__name__)


class AddressDataCollector:
    def __init__(self, web3_type: str, web3_url: str):
        self.logger = logging.getLogger('AddressDataCollector')
        self.web3_type = web3_type
        self.web3_url = web3_url

    def get_web3_client(self):
        if self.web3_type == 'ipc':
            w3 = Web3(Web3.IPCProvider(self.web3_url))
            return w3
        elif self.web3_type == 'http':
            w3 = Web3(Web3.HTTPProvider(self.web3_url))
            return w3
        else:
            msg = f'Unexpected web3 connection type: {self.web3_type}'
            self.logger.error(msg)
            raise Exception(msg)

    def get_address_data(self, addresses: List[str], block_number: int):
        w3 = self.get_web3_client()
        result = {}
        for address in addresses:
            try:
                n_transactions = w3.eth.get_transaction_count(
                    address, block_number)
                eth_account = w3.eth.get_balance(
                    address, block_number) / 10 ** 18
                result[address] = {'n_txs': n_transactions % 10 ** 9,
                                   'eth': eth_account}
            except ValueError:
                pass
        return result