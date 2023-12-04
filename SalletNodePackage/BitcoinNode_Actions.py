"""
Bitcoin Node related operations.
All actions here can either be:
- accessed over https calls to remote API (blockchain.info) or
- issued over RPC calls directly to your local FullNode
"""
import os
import logging
import inspect
import time

import requests as reqs
from SalletNodePackage import RPCHost
from dotenv import load_dotenv


lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('BitcoinNode_Actions.py'))


def rpc_url(dotenv_path: str) -> str:
    """=== Function name: rpc_url ======================================================================================
    Function creates the RPC address from the .env included data.
    :param dotenv_path: str - environmental variables location
    :return: str - of the address
    ============================================================================================== by Sziller ==="""
    cmn = inspect.currentframe().f_code.co_name  # current method name
    lg.debug("reading   : dotenv data - {:>60}".format(cmn))
    load_dotenv(dotenv_path=dotenv_path)
    # ATTENTION: local IP address MUST BE WHITELISTED on Bitcoin Node!
    rpcIP: str          = os.getenv("RPC_IP")
    rpcUser: str        = os.getenv("RPC_USER")
    rpcPassword: str    = os.getenv("RPC_PSSW")
    rpcPort: str        = str(os.getenv("RPC_PORT"))
    lg.debug("returning : serverURL - to access local the RPC server {:>31}".format(cmn))
    return 'http://' + rpcUser + ':' + rpcPassword + '@' + rpcIP + ':' + rpcPort


def nodeop_getconnectioncount(dotenv_path: str = "../.env"):
    """=== Fuction name: nodeop_getconnectioncount =====================================================================
    ============================================================================================== by Sziller ==="""
    cmn = inspect.currentframe().f_code.co_name  # current method name
    command = "getconnectioncount"
    lg.debug("running   : {}".format(cmn))
    serverURL = rpc_url(dotenv_path=dotenv_path)
    OneReq = RPCHost.RPCHost(serverURL)
    resp = OneReq.call(command)
    lg.info("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, resp))
    lg.debug("exiting   : {}".format(cmn))
    return resp


def nodeop_getblockcount(is_rpc: bool = True, dotenv_path: str = "../.env"):
    """=== Fuction name: get_blockheight ===============================================================================
    ============================================================================================== by Sziller ==="""
    cmn = inspect.currentframe().f_code.co_name  # current method name
    command = "getblockcount"
    lg.debug("running   : {}".format(cmn))
    serverURL = rpc_url(dotenv_path=dotenv_path)
    OneReq = RPCHost.RPCHost(serverURL)
    resp = OneReq.call(command)
    lg.info("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, resp))
    lg.debug("exiting   : {}".format(cmn))
    return resp


def check_tx_confirmation(tx_hash: str, limit: int = 6, is_rpc: bool = True, dotenv_path: str = "../.env") -> bool:
    """=== Function name: check_tx_confirmation ========================================================================
    Function checks if entered Transaction (by hash) had been confirmed according to limit entered.
    @param tx_hash: str - hxstr of the transaction's hash (or ID)
    @param limit: int - number of miniml confirmations necessary to be considered CONFIRMED by local system
    @param is_rpc: bool -   True:   if local RemoteProcedureCall is applied, thus LAN Fullnode is called
                            False:  if remote API is contacted
    @param dotenv_path: str - path to your .env file
    @return bool - True TX can be considered CONFIRMED (depth is arrived) False if TX not CONFIRMED yet.
    ============================================================================================== by Sziller ==="""
    cmn = inspect.currentframe().f_code.co_name  # current method name
    try:
        count = nodeop_confirmations(tx_hash=tx_hash, is_rpc=is_rpc, dotenv_path=dotenv_path)
    except:
        lg.critical("nodeop_confirmations() threw an error!!!")
        count = 0
    if count >= limit:
        return True
    return False


def publish_tx(tx_raw: str, is_rpc: bool = True, dotenv_path: str = "./.env") -> bool:
    """=== Function name: publish_tx ===================================================================================
    @param tx_raw: str - hxstr format of the serialized Bitcoin transaction.
    @param is_rpc: bool -   True:   if local RemoteProcedureCall is applied, thus LAN Fullnode is called
                            False:  if remote API is contacted
    @param dotenv_path: str - path to your .env file
    @return: bool - True TX was published False if not.
                    If False is returned, you should take action.
                    For RPC calls successfull broadcast returns the Transaction ID
    ============================================================================================== by Sziller ==="""
    cmn = inspect.currentframe().f_code.co_name  # current method name
    lg.info("Node requ.: {:>16} - publish attempt...".format({True: "OWN NODE",
                                                              False: "blockchain.info"}[is_rpc]))
    if is_rpc:
        serverURL = rpc_url(dotenv_path=dotenv_path)
        try:
            OneReq = RPCHost.RPCHost(url=serverURL)
            resp = OneReq.call("sendrawtransaction", tx_raw)
        except:
            lg.warning("Node resp.:{:>16} - status code:{:>4}".format("blockchain.info", False))
            return False
        return resp
    else:
        resp = reqs.post("https://blockchain.info/pushtx", data={"tx": tx_raw})
        lg.warning("Node resp.:{:>16} - status code:{:>4}".format("blockchain.info", resp.status_code))
        return resp.status_code == 200


def nodeop_getrawtransaction(tx_hash: str, verbose: int = 0, is_rpc: bool = True, dotenv_path: str = ""):
    """=== Function name: nodeop_getrawtransaction =====================================================================
    ============================================================================================== by Sziller ==="""
    cmn = inspect.currentframe().f_code.co_name  # current method name
    command = "getrawtransaction"
    lg.debug("running   : {}".format(cmn))
    if is_rpc:
        serverURL = rpc_url(dotenv_path=dotenv_path)
        OneReq = RPCHost.RPCHost(url=serverURL)
        resp = OneReq.call("getrawtransaction", tx_hash, verbose)
    else:
        resp = False
    lg.info("returning : {:<30} - {:>20}:\n{}".format(cmn, command, resp))
    lg.debug("exiting   : {}".format(cmn))
    return resp


def nodeop_confirmations(tx_hash: str, is_rpc: bool = False, dotenv_path: str = "") -> int:
    """=== Function name: nodeop_confirmations =========================================================================
    Read and return number of blocks passed since Transaction was confirmed.
    @param tx_hash: str - hxstr format of the transaction ID
    @param is_rpc: bool - True uses RPC, False contacts blockchain.info
    @param dotenv_path: str - the path to you .env file
    @return: int - number of confirmations
    ============================================================================================== by Sziller ==="""
    cmn = inspect.currentframe().f_code.co_name  # current method name
    command = "confirmations"
    lg.debug("running   : {}".format(cmn))
    
    if is_rpc:
        serverURL = rpc_url(dotenv_path=dotenv_path)
        OneReq = RPCHost.RPCHost(url=serverURL)
        resp = OneReq.call("getrawtransaction", tx_hash, 1)
        if resp and "confirmations" in resp:
            confirmed = resp["confirmations"]
        else:
            confirmed = 0
    else:
        cmd = "getblockcount"
        # command: getblockcount
        actual_blockcount: int = 0
        actual_tx_data: dict = {}
        ping_times = 0
        ping_limit = 16

        while not actual_blockcount or not actual_tx_data:

            resp = reqs.get('https://blockchain.info/q/{}'.format(cmd))
            try:
                actual_blockcount: int = resp.json()
                lg.info("BITCOIN   : current blockheight:{:>10}".format(actual_blockcount))
            except:
                actual_blockcount = 0
                lg.critical("({:>2}) blockchain.info answer FAILED: https://blockchain.info/q/".format(ping_times))
                time.sleep(0.1)

            request_txt = "https://blockchain.info/rawtx/{}".format(tx_hash)
            resp = reqs.get(request_txt)
            try:
                actual_tx_data: dict = resp.json()
                lg.info("BITCOIN   : blockchain.info about current TX:\n{}".format(actual_tx_data))
            except:
                actual_tx_data = {}
                lg.critical("({:>2}) blockchain.info answer FAILED:\n{}".format(ping_times, request_txt))
                lg.critical("returned  : {}".format(resp))
                time.sleep(0.1)
            if ping_times >= ping_limit:
                lg.critical("({:>2}) / ({:>2}) couldn't get answer from blockchain.info. Request timed out!"
                            .format(ping_times, ping_limit))
                break
            ping_times += 1
        try:
            tx_blockindex = actual_tx_data['block_height']
            if tx_blockindex is not None:
                confirmed = 1 + actual_blockcount - tx_blockindex
            else:
                confirmed = 0
        except KeyError:
            confirmed = 0
    lg.info("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, confirmed))
    lg.debug("exiting   : {}".format(cmn))
    return confirmed

    # 'getblockhash', nr


if __name__ == "__main__":
    txid = "ef37b2b383025ddf87209dc4a64dfb48010a274eddc3f16434fe14366241e360"
    print(nodeop_getblockcount())
    print(check_tx_confirmation(tx_hash=txid,
                                is_rpc=True))
    print(nodeop_getconnectioncount())
    tx_data = nodeop_getrawtransaction(tx_hash=txid, verbose=1)
    for _ in tx_data['vout']:
        print(_)
    
    print(tx_data['vout'][1])
    
    # ef37b2b383025ddf87209dc4a64dfb48010a274eddc3f16434fe14366241e360
