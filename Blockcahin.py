import hashlib

class Blockcahin:
    def __init__(self):
        self.blocks = []

    def addBlock(self, block):
        self.blocks.append(block)


class Block:
    def __init__(self, prev_hash, transactions, nonce=None):
        self.prev_hash = prev_hash
        self.transactions = transactions
        self.nonce = nonce
    
    def hashed_data(self):  
        rtn = ""
        rtn += self.prev_hash + "-" + self.nonce + "-".join(self.transactions)
        return hashlib.sha256(rtn)

class Transaction:
    def __init__(self, sender, reciver, amount):
        self.sender = sender
        self.receiver = reciver
        self.amount = amount 

    def __str__(self) -> str:
        return "{}:{}:{}".format(self.sender, self.receiver, self.amount)