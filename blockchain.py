"""
区块链
"""

import hashlib
import json
from time import time

class BlockChain(object):
    """block chain
    用来管理交易，存储链条，加入新块等。
    一个区块包含：索引(index)、Unix时间戳(timestamp)、交易列表(transactions)、工作量证明(proof)
    以及前一个区块的hash。

    block = {
        'index': 1,
        'timestamp': 1506057125.900785,
        'transactions': [
            {
                'sender': "8527147fe1f5426f9dd545de4b27ee00",
                'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
                'amount': 5,
            }
        ],
        'proof': 324984774000,
        'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    }
    """

    def __init__(self):
        self.chain = []
        self.current_transections = []
        self.new_block(proof=100, previous_hash=1)  # 创建创世块

    def new_block(self, proof, previous_hash):
        """
        create new block
        :param proof: <int> 工作量证明
        :param previous_hash: <str> 前一个区块的hash
        
        :return block: 新增的区块
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transections,
            'proof': proof,
            'provious_hash': previous_hash or self.hash(self.chain[-1])
        }

        self.current_transections = []  # Reset the current list of transections
        self.chain.append(block)

        return block


    def new_transection(self, sender, recipient, amount):
        """
        生成新的交易并添加到下一个待挖的区块中。
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return : <int> The index of the Block that will hold this trasection.
        """
        self.current_transections.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1   # 取当前最后一个区块(last_block)的index属性值，加1并返回。

    @staticmethod
    def hash(block):
        """
        Hashs a block
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self):
        """
        return the last block in the chain
        """
        return self.chain[-1]

    def proof_of_work(self, provious_proof):
        """
        工作量（挖矿）
        :param provious_proof: <int> 前一个区块的工作量证明
        :return: <int> 工作量证明结果
        """
        proof = 0
        while BlockChain.valid_proof(provious_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(provious_proof, proof):
        """
        工作量验证
        :param provious_proof: 上一个区块的工作量证明
        :param proof: 当前区块的证明
        :return: <bool> 验证结果
        """
        guess = f'{provious_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'