# This Script will try to connect to the APIs and include the credentials
# credentials can be public, will be shut down after use and is only on the testnet

from bitcoinrpc.authproxy import AuthServiceProxy

#credentials
rpcuser = "phil"
rpcpassword = "Homework"
rpcport = "18443"
rpchost = "192.168.2.143"

#connection string
rpc_url = f"http://{rpcuser}:{rpcpassword}@{rpchost}:{rpcport}"
rpc_connection = AuthServiceProxy(rpc_url)

def get_block_height():
    """current block height"""
    block_height = rpc_connection.getblockcount()
    print(f"blockheigt: {block_height}")


if __name__ == "__main__":
    get_block_height()




