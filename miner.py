from multiprocessing import Process, Pipe
import miner_config as config
import _thread
import socket
import time
import Blockchain
import random

# GLOBAL VARIABLES
PENDING_TRANSACTIONS = []
BLOCKCAHIN = Blockchain.Blockchain()

def miner(transactions):
    # TODO:
    # Create a new block and add transactions to the new block
    # perform proof of work
    # advertise to other miners
    global BLOCKCAHIN


    ## for logging
    miner_log = open("miner.log", "a+")


    prev_hash = BLOCKCAHIN.blocks[-1].hashed_data().hexdigest()
    timestamp = time.time()
    new_block = Blockchain.Block(prev_hash, timestamp, transactions)
    
    # perform proof of work
    #  by finding the nonce that give a number of zeros in the hash
    new_block.nonce = 0

    proof_of_work_diff = config.POW_DIFFICULTY
    block_hash = new_block.hashed_data().hexdigest()
    start_time = time.time()
    number_of_hashes = 0
    while block_hash[len(block_hash) - proof_of_work_diff:]!= "0"*proof_of_work_diff:
        number_of_hashes += 1
        current_nonce = new_block.nonce
        new_nonce = current_nonce + 1
        new_block.nonce = new_nonce
        block_hash = new_block.hashed_data().hexdigest()

    # time, number of hashes computed
    miner_log.write("{},{}".format(time.time() - start_time, number_of_hashes))

    BLOCKCAHIN.addBlock(new_block)
    print("mined new block: ", BLOCKCAHIN.blocks[-1].hashed_data().hexdigest())

    # Broadcast block
    # BLOCKCHAING.addBlock(new_block)


    
def transactions_listener(address, port):
    global PENDING_TRANSACTIONS
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((address, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            _thread.start_new_thread(handle_transaction, (conn, addr))

def handle_transaction(conn, addr):
    global PENDING_TRANSACTIONS
    while True:
        data = conn.recv(1024)
        if not data:
            break
        PENDING_TRANSACTIONS.append(data.decode('utf-8'))
        if len(PENDING_TRANSACTIONS) >= config.NUM_TRANSACTIONS:
            miner_process = Process(target=miner, args=([PENDING_TRANSACTIONS]))
            miner_process.start()
            PENDING_TRANSACTIONS = []
        conn.sendall(b'OK')

def clients(address, port):
    count = 12
    for _ in range(count):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((address, port))
            s.sendall(b"Hello, world")
            data = s.recv(1024)

        
if __name__ == "__main__":

    HOST = config.HOST
    PORT = config.PORT
    trans_process = Process(target=transactions_listener, args=(HOST, PORT))
    trans_process.start()
    time.sleep(2)
    clients_process = Process(target=clients, args=(HOST,PORT))
    clients_process.start()


    