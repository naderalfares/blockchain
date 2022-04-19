import hashlib
import time

class Blockchain:
    def __init__(self):
        self.blocks = []
        # create genisis block
        # it has non transactions whatsoever
        self.blocks.append(Block("0", time.time(), [], nonce="0"))

    def addBlock(self, block):
        self.blocks.append(block)


class Block:
    def __init__(self, prev_hash, timestamp, transactions, nonce=None):
        self.prev_hash = prev_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
    
    def hashed_data(self):  
        rtn = ""
        rtn += self.prev_hash + "-" + self.nonce + "-".join(self.transactions)
        return hashlib.sha256(rtn)

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

class Transaction:
    def __init__(self, sender, reciver, amount):
        self.sender = sender
        self.receiver = reciver
        self.amount = amount 

    def __str__(self) -> str:
        return "{}:{}:{}".format(self.sender, self.receiver, self.amount)