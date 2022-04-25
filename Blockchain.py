import hashlib
import time
import config

class Blockchain:
    def __init__(self):
        self.blocks = []
        # create genisis block
        # it has non transactions whatsoever
        self.blocks.append(Block("0", time.time(), [], nonce=0))

    def addBlock(self, block):
        self.blocks.append(block)


class Block:
    def __init__(self, prev_hash, timestamp, transactions, nonce=None):
        self.prev_hash = prev_hash
        self.timestamp = timestamp

        if config.TRANSACTIONS_HASHING == "simple":
            self.transactions = transactions
        elif config.TRANSACTIONS_HASHING == "merkle":
            self.transactions = MerkleTree(transactions)
        else:
            print("error: config.TRANSACTIONS_HASHING")
            exit(1)

        self.nonce = nonce
    
    def hashed_data(self):  
        rtn = ""
        # hash the transactions
        # if simple, include every transaction
        # else only include the root hash of the merkle tree
        if config.TRANSACTIONS_HASHING == "simple":
            rtn += self.prev_hash + "-" + str(self.nonce) + "-".join(self.transactions)
        elif config.TRANSACTIONS_HASHING == "merkle":
            rtn += self.prev_hash + "-" + str(self.nonce) + "-" + self.transactions.mt_root_hash
        else:
            print("error: config.TRANSACTIONS_HASHING")
            exit(1)

        return hashlib.sha256(rtn.encode('utf-8'))

    def add_transaction(self, transaction):
        self.transactions.append(transaction)

    def __str__(self) -> str:
        return "{}///{}///{}///{}".format(self.prev_hash,\
                                    str(self.timestamp),\
                                    str(self.transactions),\
                                    self.nonce)

class Transaction:
    def __init__(self, sender, reciver, amount):
        self.sender = sender
        self.receiver = reciver
        self.amount = amount 

    def __str__(self) -> str:
        return "{}:{}:{}".format(self.sender, self.receiver, self.amount)
