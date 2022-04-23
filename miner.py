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
MINERS_MSG = None

# Condition Variable to maintain nubmer of transactions
# before mining
MINE_CV = threading.Condition()
BRODCAST_LOCK = threading.Lock()


logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# a thread that manages miners communications
# this is typically used for when a block is mined 
def miners_network():
    logging.debug("listining for miners...")
    address = config.LOCAL_MINER_INFO["host_ip"]
    port    = config.LOCAL_MINER_INFO["port"]
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((address, port))
        s.listen()
        while True:
            conn, addr = s.accept()
            data = conn.recv(1024)
            if not data:
                break

            # ACK client that transaction has been recived
            conn.sendall(b'ACK')
            BRODCAST_LOCK.acquire()
            MINERS_MSG = data.decode('utf-8')
            BRODCAST_LOCK.release()


def broadcast_to_all_miners(block):
    for miner in config.MINERS_INFO:
        # skip if
        if miner["id"] == config.LOCAL_MINER_ID:
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((miner["host_ip"], miner["port"]))
            s.sendall(str(block).encode('utf-8'))
            data = s.recv(1024) # wait for ack from server




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

                #  get nonce of the new mined block, if recived from other miners
                BRODCAST_LOCK.acquire()
                if MINERS_MSG is not None:
                    # get the nonce of mined block
                    new_nonce = int(MINERS_MSG.split("///")[-1])
                BRODCAST_LOCK.release()

                new_block.nonce = new_nonce
                block_hash = new_block.hashed_data().hexdigest()

            BLOCKCAHIN.addBlock(new_block)
            logging.debug("mined new block in {:.2f}s: {}".format(time.time() - start_time, BLOCKCAHIN.blocks[-1].hashed_data().hexdigest()))

            BRODCAST_LOCK.acquire()
            # if local miner 'solved' the hash, broadcast to others new block
            if MINERS_MSG is None:
                threading.Thread(target=broadcast_to_all_miners, args=(new_block,)).start()
            else: # recived the block from other miner
                MINERS_MSG = None
            BRODCAST_LOCK.release()


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

        # ACK client that transaction has been recived
        conn.sendall(b'ACK')

        MINE_CV.acquire()
        PENDING_TRANSACTIONS.append(data.decode('utf-8'))
        MINE_CV.notifyAll()
        MINE_CV.release()

    
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


    