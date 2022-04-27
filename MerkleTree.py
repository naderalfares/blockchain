
import hashlib
import merkletools


class MerkleTreeHash:
    def __init__(self, transactions):
        self.transactions = transactions
        self.mt = merkletools.MerkleTools()
        for trans in transactions:
            self.mt.add_leaf(str(trans), True)
        self.mt.make_tree()
        self.mt_root_hash = self.mt.get_merkle_root()



if __name__ == "__main__":
    
    mt = merkletools.MerkleTools()
    transactions = ["A" , "B", "C" , "D"]
    for trans in transactions:
        mt.add_leaf(trans, True)
    mt.make_tree()

    print(mt.get_merkle_root())
    exit()
    _hash = hashlib.sha256(transactions[0].encode('utf-8')).hexdigest()
    print(mt.validate_proof(_hash, mt.get_leaf(0), mt.get_merkle_root()))