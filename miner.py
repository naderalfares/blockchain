from multiprocessing import Process, Manager
import miner_config as config
import socket
import time
import Blockchain
import random
import logging
import threading
import copy


# @Public feel free to work on these and do a pull request
# stars representes importance of the TODO
# TODO:
#   1. * remove either LOCAL_MINER_ID or LOCAL_MINER_INFO, one can be derived from the other
#   2. *** check if recived block from other miners have been recived before (maybe using timestamp?) 
#   3. * servers commands to help new server to deployed mid operation


# GLOBAL VARIABLES
PENDING_TRANSACTIONS = []
BLOCKCAHIN = Blockchain.Blockchain()
MINERS_MSG = None

# Condition Variable to maintain nubmer of transactions
# before mining
MINE_CV = threading.Condition()
BROADCAST_LOCK = threading.Lock()


logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)


# a thread that manages miners communications
# this is typically used for when a block is mined 
def miners_network():
    global MINERS_MSG
    global BROADCAST_LOCK

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
            logging.debug("recived blocked from other miners")
            BROADCAST_LOCK.acquire()
            MINERS_MSG = data.decode('utf-8')
            BROADCAST_LOCK.release()

def broadcast_to_all_miners(block):
    for miner in config.MINERS_INFO:
        # skip if
        if miner["id"] == config.LOCAL_MINER_ID:
            continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((miner["host_ip"], miner["port"]))
            s.sendall(str(block).encode('utf-8'))
            data = s.recv(1024) # wait for ack from server


def hashing_worker(block, hashing_range, min_val, max_val, found_blocks):
    temp_block = copy.deepcopy(block)
    logging.debug("worker thread started {}, {}".format(min_val, max_val))
    for i in hashing_range:
        temp_block.nonce = i
        block_hash = temp_block.hashed_data().hexdigest()
        if len(found_blocks) > 0:
            logging.debug("other threads have mined the block")
            break
        elif block_hash[len(block_hash) - config.POW_DIFFICULTY:] == "0"*config.POW_DIFFICULTY:
            logging.debug("I have mined the block hash: {}".format(block_hash))
            found_blocks.append(temp_block)
            break


def miner_thread(host, clients_port):
    # TODO:
    # Create a new block and add transactions to the new block
    # perform proof of work
    # advertise to other miners
    global BLOCKCAHIN
    global PENDING_TRANSACTIONS
    global MINE_CV
    global MINERS_MSG
    global BROADCAST_LOCK


    logging.debug("Miner thread started...")

    # this is to listen to other miners
    # here we would know if a block has been mined by others
    deploy_miners_listener()

    deploy_clients_listener(host, clients_port)

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
            new_block = Blockchain.Block(prev_hash, timestamp, new_transactions, nonce = 0)
    
            # perform proof of work
            #  by finding the nonce that give a number of zeros in the hash
            manager = Manager()
            found_blocks = manager.list()
            start_nonce = 0
            start_time = time.time()
            while len(found_blocks) < 1:
                logging.debug("doing rounds for range {} to {}".format(start_nonce, start_nonce + (config.HASHING_INC * config.NUM_HASHING_WORKERS)))
                worker_procs = []
                for thread_id in range(config.NUM_HASHING_WORKERS):
                    worker_procs.append(Process(target= hashing_worker, args=(new_block, range(start_nonce, start_nonce + config.HASHING_INC), start_nonce, start_nonce + config.HASHING_INC, found_blocks)))
                    start_nonce += config.HASHING_INC

                for worker in worker_procs:
                    worker.start()

                for worker in worker_procs:
                    worker.join()

                #  get nonce of the new mined block, if recived from other miners
                BROADCAST_LOCK.acquire()
                if MINERS_MSG is not None:
                    # get the nonce of mined block
                    new_nonce = int(MINERS_MSG.split("///")[-1])
                    new_block.nonce = new_nonce
                    found_blocks.append(new_block)
                BROADCAST_LOCK.release()


            BLOCKCAHIN.addBlock(found_blocks[0])
            logging.debug("mined new block in {:.2f}s: {}".format(time.time() - start_time, BLOCKCAHIN.blocks[-1].hashed_data().hexdigest()))

            BROADCAST_LOCK.acquire()
            # if local miner 'solved' the hash, broadcast to others new block
            if MINERS_MSG is None:
                threading.Thread(target=broadcast_to_all_miners, args=(found_blocks[0],)).start()
            else: # recived the block from other miner
                MINERS_MSG = None
            BROADCAST_LOCK.release()


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


def deploy_server(local_id, local_info):

    # setup the local address for this process
    config.LOCAL_MINER_ID   = local_id
    config.LOCAL_MINER_INFO = local_info
    HOST = config.LOCAL_MINER_INFO["host_ip"]
    PORT = config.LOCAL_MINER_INFO["port"]
    CLIENT_PORT = config.LOCAL_MINER_INFO["client_port"]

    # Start Miner Thread
    local_miner_thread = threading.Thread(name='miner', target=miner_thread, args=(HOST, CLIENT_PORT))
    local_miner_thread.start()
    

def deploy_miners_listener():
    # Start miner network listener
    network_listener = threading.Thread(name="MinersListener", target=miners_network)
    network_listener.start()


def deploy_clients_listener(host, client_port):
    # Start listening to transactions from client
    server_listener = threading.Thread(name='ClientListener', target=transactions_listener, args=(host, client_port))
    server_listener.start()




def deploy_testing_clients():
    for _miner_info in config.MINERS_INFO:
        client_proc = Process(target=clients, args=(_miner_info["host_ip"], _miner_info["client_port"]))
        client_proc.start()

        
if __name__ == "__main__":

    '''
    The following script is to test the framework
        locally. To run a server, use the server.py script instead
    '''

    for _miner_info in config.MINERS_INFO:
        _proc = Process(target=deploy_server, args=(_miner_info["id"], _miner_info))
        _proc.start()

    # just to make sure that all servers are deployed
    # before deploying all clients
    # time.sleep(3)
    # _ = Process(target=deploy_testig_client, args=()).start()

    # test clients sending transactions
    time.sleep(2)
    deploy_testing_clients()
