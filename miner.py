from multiprocessing import Process
import miner_config as config
import socket
import time
import Blockchain
import random
import logging
import threading
import copy

# GLOBAL VARIABLES
PENDING_TRANSACTIONS = []
BLOCKCAHIN = Blockchain.Blockchain()

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# Condition Variable to maintain nubmer of transactions
# before mining
MINE_CV = threading.Condition()
def miner():
    # TODO:
    # Create a new block and add transactions to the new block
    # perform proof of work
    # advertise to other miners
    global BLOCKCAHIN
    global PENDING_TRANSACTIONS
    global MINE_CV


    logging.debug("Miner thread started...")

    with MINE_CV:
        while True:
            MINE_CV.acquire()
            while len(PENDING_TRANSACTIONS) < config.NUM_TRANSACTIONS:
                logging.debug('miner sleeping since less than {} transactions'.format(config.NUM_TRANSACTIONS))
                MINE_CV.wait()
            logging.debug('consume {} transactions, mine block'.format(config.NUM_TRANSACTIONS))
            new_transactions = copy.deepcopy(PENDING_TRANSACTIONS[:10])
            del PENDING_TRANSACTIONS[:10]
            MINE_CV.release()
            logging.debug("mining {}".format(new_transactions))

            # Creating a new block
            prev_hash = BLOCKCAHIN.blocks[-1].hashed_data().hexdigest()
            timestamp = time.time()
            new_block = Blockchain.Block(prev_hash, timestamp, new_transactions)
    
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

            BLOCKCAHIN.addBlock(new_block)
            logging.debug("mined new block in {:.2f}s: {}".format(time.time() - start_time, BLOCKCAHIN.blocks[-1].hashed_data().hexdigest()))

            # TODO: Broadcast block


def transactions_listener(address, port):
    logging.debug("Listener thread started...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((address, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            logging.debug("accepted connection...")
            threading.Thread(name = "transactions handler", target=handle_transaction, args=(conn, addr)).start()

def handle_transaction(conn, addr):
    global PENDING_TRANSACTIONS
    global MINE_CV
    logging.debug("handle transaction..")
    while True:
        data = conn.recv(1024)
        if not data:
            break

        conn.sendall(b'ACK')

        MINE_CV.acquire()
        PENDING_TRANSACTIONS.append(data.decode('utf-8'))
        MINE_CV.notifyAll()
        MINE_CV.release()

        # ACK client that transaction has been recived


def clients(address, port):
    logging.debug("client process started...")
    count = 20
    for _ in range(count):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((address, port))
            transactions = Blockchain.Transaction("Ann", "Bob", random.random() * 100)
            s.sendall("{}".format(str(transactions)).encode('utf-8'))
            data = s.recv(1024)

        
if __name__ == "__main__":

    HOST = "localhost"
    PORT = config.PORT

    # Start Miner Thread
    miner_thread = threading.Thread(name='Miner', target=miner, args=())
    miner_thread.start()

    server_listener = threading.Thread(name='Listener', target=transactions_listener, args=(HOST, PORT))
    server_listener.start()


    # test clients sending transactions
    time.sleep(2)
    clients_process = Process(target=clients, args=(HOST,PORT))
    clients_process.start()


    