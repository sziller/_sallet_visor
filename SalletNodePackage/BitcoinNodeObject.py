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
                 is_rpc: bool):
        self.alias: str                         = alias
        self.is_rpc: bool                       = is_rpc
        self.owner: (str, None)                 = None
        # ------------------------------------------------------------------------------------------
        self.rpc_ip: (str, None)                = None                # default: '127.0.0.1'
        self.rpc_port: (int, None)              = None              # default: 8333
        self.rpc_user: (str, None)              = None
        self.rpc_password: (str, None)          = None
        self.ext_node_url: (str, None)          = None
        # ------------------------------------------------------------------------------------------
        self.features: (dict, None)             = None
        self.desc: (str, None)                  = None

        lg.debug("instant.ed: {}".format(self.ccn))
    
    def reset_sensitive_data(self):
        """=== Instance method =========================================================================================
        Clear sensitive data to avoid retaining old credentials.
        ========================================================================================== by Sziller ==="""
        self.rpc_ip                             = None
        self.rpc_port                           = None
        self.rpc_user                           = None
        self.rpc_password                       = None
        self.ext_node_url                       = None
    
        # lg.debug("instant.ed: {} - alias {} at {}. Address: {}:{} - RPC: {})"
        #          .format(self.ccn, self.alias, self.owner, self.rpc_ip, self.rpc_port, self.is_rpc))

    def update_sensitive_data(self, rpc_ip=None, rpc_port=None, rpc_user=None, rpc_password=None, ext_node_url=None):
        """=== Instance method =========================================================================================
        Update the sensitive data for the Node object. All of them at once!
        ========================================================================================== by Sziller ==="""
        self.rpc_ip                             = rpc_ip
        self.rpc_port                           = rpc_port
        self.rpc_user                           = rpc_user
        self.rpc_password                       = rpc_password
        self.ext_node_url                       = ext_node_url

    def __repr__(self):
        return "{:>15}:{} - {} / {}".format(self.rpc_ip, self.rpc_port, self.alias, self.owner)

    def __str__(self):
        return "Node:{:<20} - RPC: {}".format(self.alias, self.is_rpc)
    
    def is_valid(self):
        """=== Instance method =========================================================================================
        Returning if object is possibly valid
        ========================================================================================== by Sziller ==="""
        if all([self.rpc_ip, self.rpc_user, self.rpc_password, self.rpc_port, self.is_rpc]):
            return True
        elif (self.is_rpc is False) and self.ext_node_url:
            return True
        else:
            return False
            
        
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
        Function generates the RPC address from the sensitive data included in the instance.
        :var self.rpc_user
        :var self.rpc_password
        :var self.rpc_ip
        :var self.rpc_port
        :return: str - of the address
        ============================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        # ATTENTION: local IP address MUST BE WHITELISTED on Bitcoin Node!
        if not all([self.rpc_ip, self.rpc_user, self.rpc_password, self.rpc_port]):
            msg = "Missing RPC configuration for the node."
            lg.critical("rpc call  : {} - says {}()".format(msg, cmn), exc_info=False)
            raise ValueError(msg)
        lg.debug("returning : RPC address - says {}()".format(cmn))
        return "http://{}:{}@{}:{}".format(self.rpc_user, self.rpc_password, self.rpc_ip, self.rpc_port)

    def _make_rpc_call(self, command: str, *params):
        """=== Instance method =========================================================================================
        Helper method to make API calls to blockchain.info or similar services.
        :param endpoint: str - the specific API endpoint to call
        :return: json response from the external API
        ========================================================================================== by Sziller ==="""
        if not self.is_rpc:
            raise Exception("RPC is required for this operation.")
        OneReq = RPCHost.RPCHost(self.rpc_url())
        return OneReq.call(command, *params)

    def _make_external_api_call(self, endpoint: str, expect_json: bool = True):
        """=== Instance method =========================================================================================
        Helper method to make API calls to blockchain.info or similar services.
        :param endpoint: str - the specific API endpoint to call
        :return: json response from the external API
        ========================================================================================== by Sziller ==="""
        url = f"{self.ext_node_url}/{endpoint}"
        try:
            resp = reqs.get(url)
            resp.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            # Check if we expect JSON or raw text (hex)
            if expect_json:
                return resp.json()  # Return the JSON response if expected
            else:
                return resp.text  # Return the raw text (e.g., hex) if JSON is not expected
        except reqs.exceptions.RequestException as e:
            lg.error(f"Failed API call to entered URL, error!", exc_info=True)
            raise Exception(f"API request failed: {e}")
    
    def validate_api_url(self):
        """=== Instance method =========================================================================================
        Check if the external API URL is reachable.
        Raises an exception if the API is not reachable.
        ========================================================================================== by Sziller ==="""

        # Use a known good endpoint for testing, like 'q/getblockcount'
        test_endpoint = f"{self.ext_node_url}/q/getblockcount"
        
        try:
            resp = reqs.get(test_endpoint, allow_redirects=True)
            resp.raise_for_status()  # Raises an exception for non-200 status codes
        except reqs.exceptions.RequestException as e:
            lg.critical(f"API URL validation failed!", exc_info=False)
            raise Exception(
                f"API URL '{self.ext_node_url}' is not reachable. Please check the URL or your connection.\n{e}")
    
    def nodeop_getconnectioncount(self):
        """=== Instance method =========================================================================================
        Method returns the number of active connections of your Node. Only viable over RPC.
        :return: number of active connections
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        if self.is_rpc:
            command = "getconnectioncount"
            lg.debug("running   : {}".format(cmn))
            resp = self._make_rpc_call(command)
            lg.debug("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, resp))
            lg.debug("exit      : {}".format(cmn))
            return resp
        else:
            msg = "Request only possible for local Node and when using RPC!\n - says: {} at {}".format(cmn, self.ccn)
            lg.error(msg, exc_info=False)
            raise Exception(msg)

    def nodeop_getblockhash(self, sequence_nr: int):
        """=== Instance method =========================================================================================
        Method retrieves the block hash at a specific sequence number (height).
        :param sequence_nr: int - the sequence number of the block
        :return: block hash at the given sequence number
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getblockhash"
        lg.debug("running   : {}".format(cmn))
        if self.is_rpc:
            resp = self._make_rpc_call(command, sequence_nr)
        else:
            endpoint = f"q/{command}/{sequence_nr}"
            resp = self._make_external_api_call(endpoint)
        lg.debug("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, resp))
        lg.debug("exit      : {}".format(cmn))
        return resp

    def nodeop_getblockcount(self):
        """=== Instance method =========================================================================================
        Node operation returns height of newest block available at current time.
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getblockcount"
        lg.debug("running   : {}".format(cmn))
        if self.is_rpc:
            resp = self._make_rpc_call(command)
        else:
            endpoint = f"q/{command}"
            resp = self._make_external_api_call(endpoint)
        lg.debug("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, resp))
        lg.debug("exiting   : {}".format(cmn))
        return resp
        
    def nodeop_getblock(self, block_hash: str):
        """=== Instance method =========================================================================================
        Method retrieves block information for a given block hash.
        :param block_hash: str - the block hash to retrieve
        :return: block details for the given hash
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getblock"
        lg.debug("running   : {}".format(cmn))
        if self.is_rpc:
            resp = self._make_rpc_call(command, block_hash)
        else:
            resp = self._make_external_api_call(f"rawblock/{block_hash}")
        lg.debug("returning : {:<30} - {:>20}:\n{}".format(cmn, command, block_hash))
        lg.debug("exiting   : {}".format(cmn))
        return resp

    def check_tx_confirmation(self, tx_hash: str, limit: int = 6) -> bool:
        """=== Instance method =========================================================================================
        Function checks if entered Transaction (by hash) had been confirmed according to limit entered.
        @param tx_hash: str - hxstr of the transaction's hash (or ID)
        @param limit: int - number of miniml confirmations necessary to be considered CONFIRMED by local system
        @return bool - True TX can be considered CONFIRMED (depth is arrived) False if TX not CONFIRMED yet.
        ============================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        try:
            count = self.nodeop_confirmations(tx_hash=tx_hash)
        except Exception as e:
            lg.error("nodeop_confirmations() threw an error:\n{}".format(e), exc_info=False)
            return False
        confirmed = count >= limit
        lg.debug("returning : {:<30} - {:>20}:\n--- {} ---".format(cmn, "confirmed", tx_hash))
        lg.debug("exiting   : {}".format(cmn))
        return confirmed

    def nodeop_publish_tx(self, tx_raw: str) -> bool:
        """=== Instance method =========================================================================================
        @param tx_raw: str - hxstr format of the serialized Bitcoin transaction.
        @return: bool - True TX was published False if not.
                        If False is returned, you should take action.
                        For RPC calls successfull broadcast returns the Transaction ID
        ============================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        lg.debug("Node requ.: {:>16} - publish attempt...".format({True: "OWN NODE",
                                                                  False: "blockchain.info"}[self.is_rpc]))
        if self.is_rpc:
            try:
                resp = self._make_rpc_call("sendrawtransaction", tx_raw)
                lg.warning("Node resp.: {:<30} - rpc publish:PUBLISHED {:>20}".format(cmn, resp))
                return True
            except Exception as e:
                lg.error("Node resp.: {:<30} - rpc publish:FAILED    {:>20}".format(cmn, 'Exception'), exc_info=False)
                return False
        else:
            endpoint = "pushtx"
            try:
                resp = reqs.post("{}/{}".format(self.ext_node_url, endpoint), data={"tx": tx_raw})
                lg.warning("Node resp.: {:<30} - ext publish:PUBLISHED {:>20}"
                           .format("blockchain.info", resp.status_code))
                return resp.status_code == 200
            except reqs.exceptions.RequestException as e:
                lg.error("Node resp.: {:<30} - ext publish:FAILED    {:>20}"
                         .format("blockchain.info", e), exc_info=False)

    def nodeop_getrawtransaction(self, tx_hash: str, verbose: bool = False):
        """=== Instance method =========================================================================================
        Method retrieves raw transaction details by TX hash.
        :param tx_hash: str - the transaction hash (ID)
        :param verbose: int - verbosity level (0 or 1)
        :return: transaction details or raw hex, depending on verbosity
        ============================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getrawtransaction"
        lg.debug("running   : {}".format(cmn))
        try:
            if self.is_rpc:
                resp = self._make_rpc_call(command, tx_hash, verbose)  # RPC path - pass verbosity to the RPC call
            else:
                endpoint = f"rawtx/{tx_hash}"
                if not verbose:
                    endpoint += "?format=hex"
                
                resp = self._make_external_api_call(endpoint, expect_json=verbose)

                # If verbosity is set, the response is in JSON format, otherwise it's raw hex.
                if not verbose:
                    lg.debug(f"returning : raw hex for TX {tx_hash}")
                    lg.debug("exiting   : {}".format(cmn))
                else:
                    lg.debug(f"returning : detailed JSON for TX {tx_hash}")
                    lg.debug("exiting   : {}".format(cmn))
                return resp
            lg.debug("returning : {:<30} - {:>20}:\n--- {} ---".format(cmn, command, tx_hash))
            lg.debug("exiting   : {}".format(cmn))
            return resp
        except Exception as e:
            lg.error(f"{cmn}: Failed to fetch raw transaction - 'Exception'", exc_info=True)
            return None

    def nodeop_get_tx_outpoint_value(self, tx_outpoint: UtxoId) -> int:
        """=== Instance method =========================================================================================
        Method retrieves the value of a specific TX outpoint (UTXO).
        :param tx_outpoint: UtxoId - the UTXO outpoint to get the value for
        :return: int - value of the UTXO
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        lg.debug("running   : {}".format(cmn))

        try:
            # Use nodeop_getrawtransaction to fetch the raw transaction data (handles both RPC and API)
            lg.debug(f"Fetching raw transaction data for TX: {tx_outpoint.txid}")
            raw_tx = self.nodeop_getrawtransaction(tx_outpoint.txid, verbose=True)  # Use verbose=1 to get detailed info
            if not raw_tx:
                msg = f"Transaction data for {tx_outpoint.txid} could not be retrieved."
                lg.critical(msg)
                raise Exception(msg)

            # Extract the output value from the transaction data
            if self.is_rpc:
                # If using RPC, raw_tx is likely a dictionary from the verbose call
                value = raw_tx["vout"][tx_outpoint.n]["value"]
            else:
                # If using the external API, the structure might differ
                # Adjust accordingly if the API response format differs
                value = raw_tx["out"][tx_outpoint.n]["value"]

            lg.debug(f"returning : UTXO value: {value} - says {cmn}")
            return value

        except Exception as e:
            msg = f"Failed to retrieve UTXO value for TX {tx_outpoint.txid} - {e}"
            lg.error(msg, exc_info=False)
            raise Exception(msg)

    def nodeop_get_utxo_set_by_addresslist(self, address_list) -> dict:
        """=== Instance method =========================================================================================
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

            # Abort if a scan is already in progress
            if self._make_rpc_call(command, 'status'):
                lg.warning("aborting  : UtxoSet scan still active - trying to shoot down")
                self._make_rpc_call(command, 'abort')

            lg.warning("running...: UtxoSet scan might take several minutes... be patient!")

            try:
                # Start the scan with the formatted address list
                resp = self._make_rpc_call(command, 'start', formatted_list)

                lg.info("returned  : UtxoSet scan result!")
                lg.debug("    {}".format(resp))
                return resp
            except Exception as e:
                lg.error(f"Failed to scan UTXO set: {e}", exc_info=True)
                raise Exception(f"Failed to complete UTXO scan: {e}")
            # serverURL = self.rpc_url()
            # OneReq = RPCHost.RPCHost(url=serverURL)
            # 
            # if OneReq.call(command, 'status'):
            #     lg.warning("aborting  : UtxoSet scan still active - trying to shoot down")
            #     OneReq.call(command, 'abort')
            #     
            # lg.warning("running...: UtxoSet scan might take several minutes... be patient!")
            # resp = OneReq.call(command, 'start', formatted_list)
            # lg.info("returned  : UtxoSet scan result!")
            # lg.info("    {}".format(resp))
            # return resp
        else:
            msg = "Method only usable as RPC call - says {} at {}".format(cmn, self.ccn)
            lg.error(msg, exc_info=True)
            raise Exception(msg)
    
    def nodeop_confirmations(self, tx_hash: str) -> int:
        """=== Instance method =========================================================================================
        Read and return number of blocks passed since Transaction was confirmed.
        @param tx_hash: str - hxstr format of the transaction ID
        @return: int - number of confirmations
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "confirmations"
        lg.debug("running   : {}".format(cmn))
        
        try:
            tx_data = self.nodeop_getrawtransaction(tx_hash, verbose=True)
            if self.is_rpc:
                confirmations = tx_data.get("confirmations", 0)
            else:
                actual_blockcount = self.nodeop_getblockcount()
                lg.debug("using     : {:<30} - {:>20}: {:>8}".format("", "actual blockcount", actual_blockcount))
                tx_blockindex = tx_data.get("block_height", 0)
                lg.debug("using     : {:<30} - {:>20}: {:>8}".format("", "tx_blockindex", tx_blockindex))
                confirmations = max(0, actual_blockcount - tx_blockindex + 1)
            lg.debug("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, confirmations))
            lg.debug("exiting   : {}".format(cmn))
            return confirmations
        
        except Exception as e:
            lg.error(f"{cmn}: Failed to get confirmations - {e}", exc_info=False)
            return 0


if __name__ == "__main__":
    # instead of locally testing behaviour manually, we use the mngr_* files for manual testing in order to keep
    # namespace in root directory.
    # Refer to: mngr_bitcoinnodeobject.py
    pass

    
