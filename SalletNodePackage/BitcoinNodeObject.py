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
from bitcoinlib.transactions import Transaction as TXobj

import requests as reqs
from SalletNodePackage import RPCHost
from SalletBasePackage.models import UtxoId
from dotenv import load_dotenv


# Setting up logger                                         logger                      -   START   -
lg = logging.getLogger()
# Setting up logger                                         logger                      -   ENDED   -

lg.debug("START: {:>85} <<<".format('BitcoinNodeObject.py'))


class Node(object):
    """=== Class name: Node ============================================================================================
    Data- and methodcollection of Nodes, your system is in contact with.
    Use an instance to handle all node related duties!
    :param dotenv_path: str - path to your .env file
    :param is_rpc: bool -   True:   if local RemoteProcedureCall is applied, thus LAN Fullnode is called
                                False:  if remote API is contacted
    ============================================================================================== by Sziller ==="""
    ccn = inspect.currentframe().f_code.co_name

    def __init__(self,
                 alias: str,  # think of it as the ID of the Node inside your system
                 is_rpc: bool,
                 owner: (str, None) = "N/A",
                 ip: (str, None) = None,
                 port: (int, None) = 0,
                 features: (dict, None) = None,
                 desc: str = "",
                 dotenv_path: str = "./.env"):
        self.dotenv_path: str                   = dotenv_path
        self.alias: str                         = alias
        self.owner: str                         = owner
        self.ip: (str, None)                    = ip                # default: '127.0.0.1'
        self.port: (int, None)                  = port              # default: 8333
        self.features: dict or None             = features
        self.desc: str                          = desc
        self.is_rpc: bool                       = is_rpc
        self.rpc_user: (str, None)              = None
        self.rpc_password: (str, None)          = None
        load_dotenv()
        if self.is_rpc:
            self.apply_dotenv_rpc_data()
        lg.debug("instant.ed: {} - alias {} at {}. Address: {}:{} - RPC: {})"
                 .format(self.ccn, self.alias, self.owner, self.ip, self.port, self.is_rpc))

    def __repr__(self):
        return "{:>15}:{} - {} / {}".format(self.ip, self.port, self.alias, self.owner, )

    def __str__(self):
        return self.__repr__()
    
    def apply_dotenv_rpc_data(self):
        """=== Method name: apply_dotenv_rpc_data ======================================================================
        Whenever <self.is_rpc> is set to False, class assumes .env to have the necessary connection ans user data,
        and overwrites data entered (if at all) with .env content.
        ========================================================================================== by Sziller ==="""
        self.ip: str            = os.getenv("RPC_IP")
        self.port: int          = int(os.getenv("RPC_PORT"))
        self.rpc_user: str      = os.getenv("RPC_USER")
        self.rpc_password: str  = os.getenv("RPC_PSSW")
        
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
        rpcIP: str          = self.ip  # os.getenv("RPC_IP")
        rpcUser: str        = self.rpc_user  # os.getenv("RPC_USER")
        rpcPassword: str    = self.rpc_password  # os.getenv("RPC_PSSW")
        rpcPort: str        = self.port  # str(os.getenv("RPC_PORT"))
        lg.debug("returning : serverURL - to access local the RPC server {:>31}".format(cmn))
        return "http://{}:{}@{}:{}".format(rpcUser, rpcPassword, rpcIP, rpcPort)
        # return 'http://' + rpcUser + ':' + rpcPassword + '@' + rpcIP + ':' + rpcPort
    
    def nodeop_getconnectioncount(self):
        """=== Fuction name: nodeop_getconnectioncount =================================================================
        Method returns the number of actice connections of your Node. Only viable over RPC!
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        if self.is_rpc:
            command = "getconnectioncount"
            lg.debug("running   : {}".format(cmn))
            serverURL = self.rpc_url()
            OneReq = RPCHost.RPCHost(serverURL)
            resp = OneReq.call(command)
            lg.debug("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, resp))
            lg.debug("exit      : {}".format(cmn))
            return resp
        else:
            msg = "Request only possible for local Node and when using RPC!\n - says: {} at {}".format(cmn, self.ccn)
            lg.critical(msg)
            raise Exception(msg)

    def nodeop_getblockhash(self, sequence_nr: int):
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getblockhash"
        lg.debug("running   : {}".format(cmn))
        if self.is_rpc:
            serverURL = self.rpc_url()
            OneReq = RPCHost.RPCHost(serverURL)
            blockhash = OneReq.call(command, sequence_nr)
        else:
            resp = reqs.get('https://blockchain.info/q/{}'.format(command))
            blockhash = False
        return blockhash

    def nodeop_getblockcount(self):
        """=== Fuction name: get_blockheight ===========================================================================
        Node operation returns height of newest block available at current time.
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getblockcount"
        lg.debug("running   : {}".format(cmn))
        if self.is_rpc:
            OneReq = RPCHost.RPCHost(self.rpc_url())
            actual_blockcount = OneReq.call(command)
        else:
            resp = reqs.get('https://blockchain.info/q/{}'.format(command))
            try:
                actual_blockcount: int = resp.json()
                lg.info("BITCOIN   : current blockheight:{:>10}".format(actual_blockcount))
            except:
                actual_blockcount = 0
                lg.critical("({:>2}) blockchain.info answer FAILED: https://blockchain.info/q/".format(""))
                time.sleep(0.1)
        lg.debug("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, actual_blockcount))
        lg.debug("exiting   : {}".format(cmn))
        return actual_blockcount
        
    def nodeop_getblock(self, block_hash: str):
        """=== Fuction name: nodeop_getblock ===========================================================================
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getblock"
        lg.debug("running   : {}".format(cmn))
        if self.is_rpc:
            serverURL = self.rpc_url()
            OneReq = RPCHost.RPCHost(serverURL)
            resp = OneReq.call(command, block_hash)
            lg.debug("returning : {:<30} - {:>20}:\n{}".format(cmn, command, block_hash))
            lg.debug("exiting   : {}".format(cmn))
            return resp
        else:
            resp = reqs.get("https://blockchain.info/rawblock/{}".format(block_hash))
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
        lg.debug("Node requ.: {:>16} - publish attempt...".format({True: "OWN NODE",
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
            method_response = OneReq.call("getrawtransaction", tx_hash, verbose)
        else:
            if verbose:
                request_txt = "https://blockchain.info/rawtx/{}{}".format(tx_hash, "")  # verbose response
                resp = reqs.get(request_txt)
                try:
                    method_response = resp.json()
                    # lg.debug("BITCOIN   : blockchain.info about current TX:\n{}".format(method_response))
                except:
                    method_response = {}
                    lg.critical("({:>2}) blockchain.info answer FAILED:\n{}".format("", request_txt))
                    lg.critical("returned  : {}".format(resp))
                    time.sleep(0.1)
            else:
                request_txt = "https://blockchain.info/rawtx/{}{}".format(tx_hash, "?format=hex")  # verbose response
                resp = reqs.get(request_txt)
                try:
                    method_response = resp.text
                    # lg.debug("BITCOIN   : blockchain.info about current TX:\n{}".format(method_response))
                except:
                    method_response  = ""
                    lg.critical("({:>2}) blockchain.info answer FAILED:\n{}".format("", request_txt))
                    lg.critical("returned  : {}".format(resp))
                    time.sleep(0.1)
        lg.debug("returning : {:<30} - {:>20}:\n--- {} ---".format(cmn, command, tx_hash))
        lg.debug("exiting   : {}".format(cmn))
        return method_response
    
    def nodeop_get_tx_outpoint_value(self, tx_outpoint: UtxoId) -> int:
        """=== Method name: nodeop_get_tx_outpoint =====================================================================
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        if self.is_rpc:
            serverURL = self.rpc_url()
            OneReq = RPCHost.RPCHost(url=serverURL)
            hxstr = OneReq.call("getrawtransaction", tx_outpoint.txid, False)
        else:
            try:
                request_txt = "https://blockchain.info/rawtx/{}{}".format(tx_outpoint.txid, "?format=hex")
                resp = reqs.get(request_txt)
                hxstr = resp.text
            except:
                msg = "failed    : issue with request from blockchain.info - says {}.{}()".format(self.ccn, cmn)
                lg.critical(msg)
                raise Exception(msg)
        tx = TXobj.parse(hxstr)
        return tx.outputs[tx_outpoint.n].value
            
    def nodeop_get_utxo_set_by_addresslist(self, address_list) -> dict:
        """=== Method name: nodeop_get_utxo_set_by_addresslist =========================================================
        Method searches through local UtxoSet and returns those Utxo-s, referring to addresses shown in <address_list>.
        Data is returned as answered by the Node
        :param address_list: list - or addresses in Base58 format
        :return: dict - of Utxo data referring to addresses in question
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        if self.is_rpc:
            command = "scantxoutset"
            lg.info("starting  : UtxoSet processing - {} at {}".format(cmn, self.ccn))
            formatted_list = ['addr({})'.format(_) for _ in address_list]  # syntax used by BitcoinCore
            lg.debug("converted : list to BitcoinCore request format for command: '{}'".format(command))
            serverURL = self.rpc_url()
            OneReq = RPCHost.RPCHost(url=serverURL)
            if OneReq.call(command, 'status'):
                lg.warning("aborting  : UtxoSet scan still active - trying to shoot down")
                OneReq.call(command, 'abort')
            lg.warning("running...: UtxoSet scan might take several minutes... be patient!")
            resp = OneReq.call(command, 'start', formatted_list)
            lg.info("returned  : UtxoSet scan result!")
            lg.debug("    {}".format(resp))
            return resp
        else:
            msg = "Method only usable as RPC call".format(cmn, self.ccn)
            lg.critical(msg)
            raise Exception(msg)
    
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
                    lg.debug("BITCOIN   : current blockheight:{:>10}".format(actual_blockcount))
                except:
                    actual_blockcount = 0
                    lg.critical("({:>2}) blockchain.info answer FAILED: https://blockchain.info/q/".format(ping_times))
                    time.sleep(0.1)
    
                request_txt = "https://blockchain.info/rawtx/{}".format(tx_hash)
                resp = reqs.get(request_txt)
                try:
                    actual_tx_data: dict = resp.json()
                    # lg.debug("BITCOIN   : blockchain.info about current TX:\n{}".format(actual_tx_data))
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
        lg.debug("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, confirmed))
        lg.debug("exiting   : {}".format(cmn))
        return confirmed

    # 'getblockhash', nr


if __name__ == "__main__":
    # instead of locally testing behaviour manually, we use the mngr_* files for manual testing in order to keep
    # namespace in root directory.
    # Refer to: mngr_bitcoinnodeobject.py
    pass
