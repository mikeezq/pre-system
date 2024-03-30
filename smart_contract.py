from web3 import Web3
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import logging

CONTRACT_ADDRESS = "0x7Dc0fa574F7cb11FE3E86CcD1e39AC4b7e17d658" # TODO DELETE


def convert_to_string(pub_key: EllipticCurvePublicKey) -> str:
    pub_key = pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return pub_key.decode('utf-8')


def convert_to_ec(pub_key: str):
    public_key = serialization.load_pem_public_key(pub_key.encode('utf-8'), backend=default_backend())

    return public_key


class SmartContract:
    abi = [
        {'inputs': [],
         'stateMutability': 'nonpayable',
         'type': 'constructor'
         },
        {
            'inputs': [
                {'internalType': 'string', 'name': 'clientName', 'type': 'string'},
                {'internalType': 'string', 'name': 'pubKey', 'type': 'string'}
            ],
            'name': 'addPublicKey',
            'outputs': [],
            'stateMutability': 'nonpayable',
            'type': 'function'
        },
        {
            'inputs': [
                {'internalType': 'string', 'name': 'clientName', 'type': 'string'}
            ],
            'name': 'getPublicKey',
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

    def addPublicKey(self, sender_address, clientName, pubKey):
        sender_address = '0x3eB4d8dF7D9B9E3Df03A294467df0666429FbEA7'

        pubKey = convert_to_string(pubKey)

        logging.info("Add public key for %s", clientName)
        tx_hash = self.contract.functions.addPublicKey(clientName, pubKey).transact({
            'from': sender_address,
            'gas': 2000000,
        })

        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def getPublicKey(self, clientName):
        logging.info("Get public key for client: %s", clientName)
        pub_key = self.contract.functions.getPublicKey(clientName).call()

        return pub_key


contract = SmartContract("http://127.0.0.1:8545", "")  # TODO fix args
