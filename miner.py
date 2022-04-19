from multiprocessing import Process, Pipe
import miner_config as config
import _thread
import socket
import time
import Blockchain

# GLOBAL VARIABLES
PENDING_TRANSACTIONS = []
BLOCKCAHIN = Blockchain()

def miner(transactions):
    # TODO:
    # Create a new block and add transactions to the new block
    # perform proof of work
    # advertise to other miners 
    pass
    
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
        PENDING_TRANSACTIONS.append(data)
        if len(PENDING_TRANSACTIONS) >= 10:
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


    