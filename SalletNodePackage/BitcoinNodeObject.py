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
from SalletBasePackage.models import UtxoId
from dotenv import load_dotenv



lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('BitcoinNodeObject.py'))


class Node(object):
    """=== Class name: Node ============================================================================================
    Data- and methodcollection of Nodes, your system is in contact with.
    :param dotenv_path: str - path to your .env file
    :param is_rpc: bool -   True:   if local RemoteProcedureCall is applied, thus LAN Fullnode is called
                                False:  if remote API is contacted
    ============================================================================================== by Sziller ==="""
    ccn = inspect.currentframe().f_code.co_name

    def __init__(self,
                 alias: str = "N/A",
                 owner: str = "N/A",
                 ip: str = '127.0.0.1',
                 port: int = 8333,
                 features: dict = {},
                 desc: str = "",
                 dotenv_path: str = "./.env",
                 is_rpc: bool = True):
        self.alias: str = alias
        self.owner: str = owner
        self.ip: str = ip
        self.port: int = port
        self.features: dict = features
        self.desc: str = desc
        self.is_rpc: bool = is_rpc
        self.dotenv_path: str = dotenv_path
        
    def __repr__(self):
        return "{:>15}:{} - {} / {}".format(self.ip, self.port, self.alias, self.owner, )

    @classmethod
    def construct(cls, d_in):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param d_in: dict - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        return cls(**d_in)

    @classmethod
    def construct_from_string(cls, str_in):
        """=== Classmethod: construct ==================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param str_in: str - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        pass

    def rpc_url(self) -> str:
        """=== Function name: rpc_url ==================================================================================
        Function creates the RPC address from the .env included data.
        :var self.dotenv_path: str - environmental variables location
        :return: str - of the address
        ============================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        lg.debug("reading   : dotenv data - {:>60}".format(cmn))
        load_dotenv(dotenv_path=self.dotenv_path)
        # ATTENTION: local IP address MUST BE WHITELISTED on Bitcoin Node!
        rpcIP: str          = os.getenv("RPC_IP")
        rpcUser: str        = os.getenv("RPC_USER")
        rpcPassword: str    = os.getenv("RPC_PSSW")
        rpcPort: str        = str(os.getenv("RPC_PORT"))
        lg.debug("returning : serverURL - to access local the RPC server {:>31}".format(cmn))
        return 'http://' + rpcUser + ':' + rpcPassword + '@' + rpcIP + ':' + rpcPort
    
    def nodeop_getconnectioncount(self):
        """=== Fuction name: nodeop_getconnectioncount =====================================================================
        ============================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getconnectioncount"
        lg.debug("running   : {}".format(cmn))
        serverURL = self.rpc_url()
        OneReq = RPCHost.RPCHost(serverURL)
        resp = OneReq.call(command)
        lg.info("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, resp))
        lg.debug("exiting   : {}".format(cmn))
        return resp

    def nodeop_getblockcount(self):
        """=== Fuction name: get_blockheight ===========================================================================
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getblockcount"
        lg.debug("running   : {}".format(cmn))
        serverURL = self.rpc_url()
        OneReq = RPCHost.RPCHost(serverURL)
        resp = OneReq.call(command)
        lg.info("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, resp))
        lg.debug("exiting   : {}".format(cmn))
        return resp
    
    def nodeop_getblock(self, block_hash: str):
        """=== Fuction name: nodeop_getblock ===========================================================================
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getblock"
        lg.debug("running   : {}".format(cmn))
        serverURL = self.rpc_url()
        OneReq = RPCHost.RPCHost(serverURL)
        resp = OneReq.call(command, block_hash)
        lg.info("returning : {:<30} - {:>20}:\n{}".format(cmn, command, resp))
        lg.debug("exiting   : {}".format(cmn))
        return resp

    def check_tx_confirmation(self, tx_hash: str, limit: int = 6) -> bool:
        """=== Function name: check_tx_confirmation ========================================================================
        Function checks if entered Transaction (by hash) had been confirmed according to limit entered.
        @param tx_hash: str - hxstr of the transaction's hash (or ID)
        @param limit: int - number of miniml confirmations necessary to be considered CONFIRMED by local system
        @return bool - True TX can be considered CONFIRMED (depth is arrived) False if TX not CONFIRMED yet.
        ============================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        try:
            count = self.nodeop_confirmations(tx_hash=tx_hash)
        except:
            lg.critical("nodeop_confirmations() threw an error!!!")
            count = 0
        if count >= limit:
            return True
        return False

    def publish_tx(self, tx_raw: str) -> bool:
        """=== Method name: publish_tx =================================================================================
        @param tx_raw: str - hxstr format of the serialized Bitcoin transaction.
        @return: bool - True TX was published False if not.
                        If False is returned, you should take action.
                        For RPC calls successfull broadcast returns the Transaction ID
        ============================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        lg.info("Node requ.: {:>16} - publish attempt...".format({True: "OWN NODE",
                                                                  False: "blockchain.info"}[self.is_rpc]))
        if self.is_rpc:
            serverURL = self.rpc_url()
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

    def nodeop_getrawtransaction(self, tx_hash: str, verbose: int = 0):
        """=== Method name: nodeop_getrawtransaction ===================================================================
        ============================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getrawtransaction"
        lg.debug("running   : {}".format(cmn))
        if self.is_rpc:
            serverURL = self.rpc_url()
            OneReq = RPCHost.RPCHost(url=serverURL)
            resp = OneReq.call("getrawtransaction", tx_hash, verbose)
        else:
            resp = False
        lg.info("returning : {:<30} - {:>20}:\n--- {} ---".format(cmn, command, tx_hash))
        lg.debug("exiting   : {}".format(cmn))
        return resp
    
    def nodeop_get_tx_outpoint(self, tx_outpoint: UtxoId):
        cmn = inspect.currentframe().f_code.co_name  # current method name
        if self.is_rpc:
            serverURL = self.rpc_url()
            OneReq = RPCHost.RPCHost(url=serverURL)
            resp = OneReq.call("getrawtransaction", tx_outpoint.txid, True)
            return resp["vout"][tx_outpoint.n]
            
    def nodeop_confirmations(self, tx_hash: str) -> int:
        """=== Method name: nodeop_confirmations =======================================================================
        Read and return number of blocks passed since Transaction was confirmed.
        @param tx_hash: str - hxstr format of the transaction ID
        @return: int - number of confirmations
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "confirmations"
        lg.debug("running   : {}".format(cmn))
        
        if self.is_rpc:
            serverURL = self.rpc_url()
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
    txid = "7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741"
    # coinbases
    txid = "56f26b369c93ba1098afb14fdf213209018904bcef82114a8f019de069dc7a7b"
    txid = "5029302f0c8c1c2ef856194ca8a7f78a7b6ba029b3a432466ba1d4ab2105aef5"
    txid = "0b6dc7910ed25a79ab6ce12e6a0dcb991c44708580b18f223b00a4526fd10bbf"
    txid = "9636a0d06128c89121b442ee56200a28b99350e658f4f0774db3ea64daad872a"
    txid = "525c4eef55f597d0344345ce9439b1e7eeb72053d0682eb2c6910a4f4d695987"
    node = Node(dotenv_path="../.env")
    print(node.nodeop_getblockcount())
    print(node.check_tx_confirmation(tx_hash=txid))
    print(node.nodeop_getconnectioncount())
    print("========================================================================================")
    tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=1)
    
    for k, v in tx_data.items():
        print(k, v)
    
    # print(tx_data['vout'][0])
    
    # ef37b2b383025ddf87209dc4a64dfb48010a274eddc3f16434fe14366241e360
