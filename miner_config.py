TRANSACTIONS_PER_BLOCK = 10


# update this to the server's IP address and port number
HOST = "localhost"
PORT = 65432

# The intger represents the number of zeros
# that a hash has to have at the end to be
# to be considered a valid block
POW_DIFFICULTY = 4


# Start mining when the this number
# of transactions have reached
NUM_TRANSACTIONS = 10




# information of all miners


# THIS SHOULD BE DIFFERENT ACCROSS ALL MINERS!!!
LOCAL_MINER_ID = 0
LOCAL_MINER_INFO = {
		"id"	  : 0,
		"host_ip"    : "localhost",
		"port"    : 9000	
}

MINERS_INFO = [
	{
		"id"	  : 0,
		"host_ip"    : "localhost",
		"port"    : 9000	
	},
		{
		"id"	  : 1,
		"host_ip"    : "localhost",
		"port"    : 9001	
	},
		{
		"id" 	  : 2,
		"host_ip"    : "localhost",
		"port"    : 9002	
	},
		{
		"id"	  : 3,
		"host_ip"    : "localhost",
		"port"    : 9003	
	}

]