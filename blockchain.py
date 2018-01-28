"""
区块链
"""

import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request
from urllib.parse import urlparse


class Blockchain(object):
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
        self.current_transactions = []
        self.nodes = set()
        self.new_block(proof=100, previous_hash=1)  # 创建创世块

    def register_node(self, address):
        """
        注册节点
        :param address: Address of node, Eg. 'http://192.168.1.5'
        :return: None
        """

        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc)

    @staticmethod
    def valid_chain(outer_chain):
        """
        验证区块链
        :param outer_chain: 待验证的链
        :return: 验证结果
        """
        last_block = outer_chain[0]
        current_index = 1
        while current_index < len(outer_chain):
            block = outer_chain[current_index]
            previous_hash = block['previous_hash']

            if previous_hash != Blockchain.hash(last_block):  # Hash值验证
                return False

            previous_proof = last_block['proof']
            proof = block['proof']

            if not Blockchain.valid_proof(previous_proof, proof):  # 工作量验证
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        共识算法解决冲突，使用最长的链
        :return: <bool> True 如果链被取代，否则为False
        """
        neighbors = self.nodes
        max_length = len(self.chain)
        new_chain = None

        for node in neighbors:
            # 获取其他节点的链
            response = request.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                other_chain = response.json()['chain']

                # 如果其他节点的链长度大于本节点的链，并且通过验证，则更新当前最大链
                if length > max_length and Blockchain.valid_chain(other_chain):
                    max_length = length
                    new_chain = other_chain

        if new_chain is not None:
            self.chain = new_chain
            return True

        return False

        if selected_chain != self.chain:
            self.chain = selected_chain
            return True

        return False

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
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        self.current_transactions = []  # Reset the current list of transections
        self.chain.append(block)

        return block

    def new_transaction(self, sender, recipient, amount):
        """
        生成新的交易并添加到下一个待挖的区块中。
        :param sender: <str> Address of the Sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return : <int> The index of the Block that will hold this trasection.
        """
        self.current_transactions.append({
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

    def proof_of_work(self, previous_proof):
        """
        工作量（挖矿）
        :param previous_proof: <int> 前一个区块的工作量证明
        :return: <int> 工作量证明结果
        """
        proof = 0
        while Blockchain.valid_proof(previous_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(previous_proof, proof):
        """
        工作量验证
        :param previous_proof: 上一个区块的工作量证明
        :param proof: 当前区块的证明
        :return: <bool> 验证结果
        """
        guess = f'{previous_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'
    

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route("/", methods=['GET'])
def main():
    return "This is Blockchain Sample"


@app.route('/mine', methods=['GET'])
def mine():
    """mine a new Block
    """

    # 1. 完成工作量证明(解决一个数学难题)
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # 2. 给自己一个币，创建一个transaction
    blockchain.new_transaction(sender=0, recipient=node_identifier, amount=1)

    # 3. 创建新区块
    block = blockchain.new_block(proof, None)

    response = {
        "message": "new block Forget",
        "index": block['index'],
        "transaction": block['transactions'],
        "timestamp": block['timestamp'],
        "proof": block['proof'],
        "previous_hash": block['previous_hash']
    }

    return jsonify(response), 200


@app.route("/transection", methods=['POST'])
def new_transaction():
    """create a new Transection
    """
    params = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in params for k in required):
        return "Missing valus", 400
        
    # Create a new Transection    
    index = blockchain.new_transaction(params['sender'], params['recipient'], params['amount'])
    return jsonify({'message': f'your Transection will be added to Block {index}'}), 201


@app.route("/chain", methods=['GET'])
def chain():
    """get Block Chain
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route("/node/register", methods=['POST'])
def register_nodes():
    nodes = request.get_json()

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.nodes.add(node)

    response = {
        "message": "New nodes have been added",
        "total_nodes": len(blockchain.nodes)
    }

    return jsonify(response), 201


@app.route("/node/resolve", methods=["GET"])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            "message": "Our chain was replaced",
            "new_chain": blockchain.chain
        }
    else:
        response = {
            "message": "Our chain is authoritative",
            "chain": blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run('0.0.0.0', port)