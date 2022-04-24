#
# BLOCKCHAIN CONFIG FILE
#


# The intger represents the number of zeros
# that a hash has to have at the end to be
# to be considered a valid block
POW_DIFFICULTY = 4



# Start mining when the this number
# of transactions have reached
NUM_TRANSACTIONS = 10

# Parallelism
# these run in parallel
NUM_HASHING_WORKERS = 4
# the range of nonce value to try in every 
# epoch of workers running in parallel
HASHING_INC         = 1000


# information of all miners
# THIS SHOULD BE DIFFERENT ACCROSS ALL MINERS!!!
LOCAL_MINER_ID = 0
LOCAL_MINER_INFO = {
		"id"	  : 0,
		"host_ip"    : "localhost",
		"port"    : 9000,	
        "client_port" : 65432
}


# SINGLE MINER 
MINERS_INFO = [

 	{
 		"id"	  : 0,
 		"host_ip"    : "localhost",
 		"port"    : 9000,
        "client_port" : 65432
 	}

]


# MULTIPLE MINERS EXAMPLE

# MINERS_INFO = [
# 	{
# 		"id"	  : 0,
# 		"host_ip"    : "localhost",
# 		"port"    : 9000	
# 	},
# 		{
# 		"id"	  : 1,
# 		"host_ip"    : "localhost",
# 		"port"    : 9001	
# 	},
# 		{
# 		"id" 	  : 2,
# 		"host_ip"    : "localhost",
# 		"port"    : 9002	
# 	},
# 		{
# 		"id"	  : 3,
# 		"host_ip"    : "localhost",
# 		"port"    : 9003	
# 	}
# 
# ]
