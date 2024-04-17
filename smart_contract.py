from web3 import Web3
import logging

from constants import CONTRACT_ADDRESS, SENDER_ADDRESS


class SmartContract:
    abi = [
        {'inputs': [],
         'stateMutability': 'nonpayable',
         'type': 'constructor'
         },
        {
            'inputs': [
                {'internalType': 'string', 'name': 'clientName', 'type': 'string'},
                {'internalType': 'string', 'name': 'reKey', 'type': 'string'}
            ],
            'name': 'addReKey',
            'outputs': [],
            'stateMutability': 'nonpayable',
            'type': 'function'
        },
        {
            'inputs': [
                {'internalType': 'string', 'name': 'clientName', 'type': 'string'}
            ],
            'name': 'getReKey',
            'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
            'stateMutability': 'view',
            'type': 'function'
        },
        {
            'inputs': [],
            'name': 'owner',
            'outputs': [
                {'internalType': 'address', 'name': '', 'type': 'address'}
            ],
            'stateMutability': 'view', 'type': 'function'
        }
    ]

    def __init__(self, blockchain_addr, contract_addr):
        self.web3 = Web3(Web3.HTTPProvider(blockchain_addr))

        contract_address = CONTRACT_ADDRESS  # TODO get from args
        self.contract = self.web3.eth.contract(address=contract_address, abi=SmartContract.abi)

    def addReKey(self, clientName, reKey):
        logging.info("Add rekey for %s", clientName)
        tx_hash = self.contract.functions.addReKey(clientName, reKey).transact({
            'from': SENDER_ADDRESS,
            'gas': 2000000,
        })

        self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def getReKey(self, clientName):
        logging.info("Get rekey for client: %s", clientName)
        rekey_str = self.contract.functions.getReKey(clientName).call()

        return rekey_str


contract = SmartContract("http://127.0.0.1:8545", "")  # TODO fix args
