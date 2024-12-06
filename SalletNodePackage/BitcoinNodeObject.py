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
from typing import Optional
from bitcoinlib.transactions import Transaction as TXobj

import requests as reqs
from SalletNodePackage import RPCHost
from SalletBasePackage.models import UtxoId
from dotenv import load_dotenv


# Setting up logger                                         logger                      -   START   -
lg = logging.getLogger()
# Setting up logger                                         logger                      -   ENDED   -

lg.info("START: {:>85} <<<".format('BitcoinNodeObject.py'))


class Node(object):
    """=== Class name: Node ============================================================================================
    Data- and methodcollection of Nodes, your system is in contact with.
    Use an instance to handle all node related duties!
    :param alias: str - the unique name we refer to the Node in our environment. Note: it is Case INSENSITIVE:
                        so uniqueness must be kept regardless of casing.
    :param is_rpc: bool -   True:   if local RemoteProcedureCall is applied, thus LAN Fullnode is called
                                False:  if remote API is contacted
    ============================================================================================== by Sziller ==="""
    ccn = inspect.currentframe().f_code.co_name

    def __init__(self,
                 alias: str,  # think of it as the ID of the Node inside your system
                 is_rpc: bool):
        self.alias: str                         = alias
        self.is_rpc: bool                       = is_rpc
        self.owner: Optional[str]               = None
        self.features: Optional[dict]           = None
        self.desc: Optional[str]                = None
        # ------------------------------------------------------------------------------------------
        self.rpc_ip: Optional[str]              = None                # default: '127.0.0.1'
        self.rpc_port: Optional[int]            = None              # default: 8333
        self.rpc_user: Optional[str]            = None
        self.rpc_password: Optional[str]        = None
        self.ext_node_url: Optional[str]        = None
        # ------------------------------------------------------------------------------------------
        self._MAX_RETRIES: int                  = 5
        self._WAIT_TIME_SECONDS: int            = 2

        lg.debug("instant.ed:                                   < {:>20} > - ({})".format(self.alias, self.ccn))
    
    def reset_sensitive_data(self):
        """=== Instance method =========================================================================================
        Clear sensitive data to avoid retaining old credentials.
        :var self.rpc_ip: str - IP address of the node
        :var self.rpc_port: int - Port for RPC communication
        :var self.rpc_user: str - RPC username
        :var self.rpc_password: str - RPC password
        :var self.ext_node_url: str - External API URL for non-RPC nodes
        ========================================================================================== by Sziller ==="""
        self.rpc_ip                             = None
        self.rpc_port                           = None
        self.rpc_user                           = None
        self.rpc_password                       = None
        self.ext_node_url                       = None

    def update_sensitive_data(self,
                              rpc_ip: Optional[str] = None,
                              rpc_port: Optional[int] = None,
                              rpc_user: Optional[str] = None,
                              rpc_password: Optional[str] = None,
                              ext_node_url: Optional[str] = None):
        """=== Instance method =========================================================================================
        Update the sensitive data for the Node object. All of them at once!
        :param rpc_ip: str or None - IP address of the node
        :param rpc_port: int or None - Port for RPC communication
        :param rpc_user: str or None - RPC username
        :param rpc_password: str or None - RPC password
        :param ext_node_url: str or None - External API URL for non-RPC nodes
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
        Returns True if the Node object has valid configuration for either RPC or API connection.
        :return: bool - True if the node is valid, False otherwise
        ========================================================================================== by Sziller ==="""
        lg.info(f"validating: Node with alias:                  < {self.alias:>20} >")
        if self.is_rpc:
            # Check if all RPC-related variables are present
            if all([self.rpc_ip, self.rpc_user, self.rpc_password, self.rpc_port]):
                lg.debug(f"valid RPC : Node with alias:                  < {self.alias:>20} >")
                return True
            else:
                lg.warning(f"invalid   : Missing RPC data Node with alias: < {self.alias:>20} > - "
                           f"Skipping this node.")
                return False
        # If the node is not an RPC node, check for ext_node_url (API node)
        elif self.ext_node_url:
            lg.debug(f"valid API : Node with alias:                  < {self.alias:>20} >")
            return True
        else:
            lg.warning(f"invalid   : Missing API data Node with alias: < {self.alias:>20} > - "
                       f"Skipping this node.")
            return False
        
    @classmethod
    def construct(cls, d_in):
        """=== Classmethod =============================================================================================
        Instantiate a Node object using the provided dictionary.
        :param d_in: dict - Dictionary containing parameters for object instantiation
        :return: Node - Instance of the Node class
        ========================================================================================== by Sziller ==="""
        return cls(**d_in)

    @classmethod
    def construct_from_string(cls, str_in):
        """=== Classmethod =============================================================================================
        Input necessary class parameters to instantiate object of the class!
        @param str_in: str - format data to instantiate new object
        @return: an instance of the class
        ========================================================================================== by Sziller ==="""
        pass

    def rpc_url(self) -> str:
        """=== Instance method =========================================================================================
        Generates the RPC URL from the stored sensitive data.
        :var self.rpc_user: str - RPC username
        :var self.rpc_password: str - RPC password
        :var self.rpc_ip: str - IP address of the node
        :var self.rpc_port: int - Port for RPC communication
        :return: str - RPC URL formatted as 'http://<user>:<password>@<ip>:<port>'
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        # ATTENTION: local IP address MUST BE WHITELISTED on Bitcoin Node!
        if not all([self.rpc_ip, self.rpc_user, self.rpc_password, self.rpc_port]):
            msg = "Missing RPC configuration for the node."
            lg.critical("rpc call  : {} - says {}()".format(msg, cmn), exc_info=False)
            raise ValueError(msg)
        lg.debug("returning : RPC address - says {}()".format(cmn))
        return "http://{}:{}@{}:{}".format(self.rpc_user, self.rpc_password, self.rpc_ip, self.rpc_port)

    def _make_rpc_call(self, command: str, *params):
        """=== Internal utility method =================================================================================
        Makes an RPC call to the node using the stored RPC credentials.
        :param command: str - The RPC method to call
        :param params: tuple - Additional parameters for the RPC call
        :return: json - JSON response from the node
        ========================================================================================== by Sziller ==="""
        if not self.is_rpc:
            raise Exception("RPC is required for this operation.")
        OneReq = RPCHost.RPCHost(self.rpc_url())
        return OneReq.call(command, *params)

    def _make_external_api_call(self, endpoint: str, expect_json: bool = True):
        """=== Internal utility method =================================================================================
        Makes an API call to an external node (e.g., blockchain.info).
        :param endpoint: str - API endpoint to call
        :param expect_json: bool - Whether to expect a JSON response (default True)
        :return: json or str - JSON response or raw text depending on the request
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
        Validates that the external API URL is reachable.
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
        Retrieves the number of active connections to the node. Only available for RPC nodes.
        :return: int - Number of active connections
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
        Retrieves the block hash at a specific block height.
        :param sequence_nr: int - The block height (sequence number)
        :return: str - The block hash at the given height
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        command = "getblockhash"
        lg.debug("running   : {}".format(cmn))
        if self.is_rpc:
            resp = self._make_rpc_call(command, sequence_nr)
            lg.debug("returning : {:<30} - {:>20}: {:>8}".format(cmn, command, resp))
            lg.debug("exit      : {}".format(cmn))
            return resp
        else:
            msg = "Method only usable as RPC call - says {} at {}".format(cmn, self.ccn)
            lg.error(msg, exc_info=True)
            # endpoint = f"q/{command}/{sequence_nr}"
            # resp = self._make_external_api_call(endpoint)
            return False
        
    def nodeop_getblockcount(self):
        """=== Instance method =========================================================================================
        Retrieves the total number of blocks in the blockchain.
        :return: int - The current block count
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
        Retrieves detailed information about a specific block by its hash.
        :param block_hash: str - The block hash to retrieve
        :return: dict - Details of the block
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

    def nodeop_check_tx_confirmation(self, tx_hash: str, limit: int = 6) -> bool:
        """=== Instance method =========================================================================================
        Checks if a transaction has reached the required number of confirmations.
        :param tx_hash: str - The transaction hash
        :param limit: int - Minimum number of confirmations to be considered confirmed (default 6)
        :return: bool - True if the transaction is confirmed, False otherwise
        ========================================================================================== by Sziller ==="""
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
        Publishes a raw transaction to the network.
        :param tx_raw: str - The raw transaction in hexadecimal format
        :return: bool - True if the transaction was successfully published, False otherwise
        ========================================================================================== by Sziller ==="""
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
        Retrieves raw transaction details by transaction hash.
        :param tx_hash: str - The transaction hash (ID)
        :param verbose: bool - If True, returns detailed JSON; if False, returns raw hex (default False)
        :return: dict or str - Transaction details (JSON) or raw hex string
        ========================================================================================== by Sziller ==="""
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
        Retrieves the value of a specific transaction outpoint (UTXO).
        :param tx_outpoint: UtxoId - The UTXO outpoint to get the value for
        :return: int - The value of the UTXO
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
        Scans the UTXO set for all UTXOs associated with a list of addresses.
        :param address_list: list - List of addresses in Base58 format
        :return: dict - UTXO data for the provided addresses
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current method name
        if self.is_rpc:
            command = "scantxoutset"
            lg.info("starting  : UtxoSet processing - {} at {}".format(cmn, self.ccn))
            formatted_list = ['addr({})'.format(_) for _ in address_list]  # syntax used by BitcoinCore
            lg.debug("converted : list to BitcoinCore request format for command: '{}'".format(command))

            # Abort if a scan is already in progress, and cannot be stopped
            try:
                # Use the hidden static method to handle the retry logic
                self._retry_abort_scan(command)

                # Proceed with initiating a new scan
                lg.warning("Running: UTXO set scan might take several minutes... please be patient!")
            except Exception as e:
                lg.error(f"Error while managing UTXO scan: {e}")
                raise

            try:
                # Start the scan with the formatted address list
                resp = self._make_rpc_call(command, 'start', formatted_list)

                lg.info("returned  : UtxoSet scan result!")
                lg.debug("    {}".format(resp))
                return resp
            except Exception as e:
                lg.error(f"Failed to scan UTXO set: {e}", exc_info=True)
                raise Exception(f"Failed to complete UTXO scan: {e}")
        else:
            msg = "Method only usable as RPC call - says {} at {}".format(cmn, self.ccn)
            lg.error(msg, exc_info=True)
            raise Exception(msg)
    
    def nodeop_confirmations(self, tx_hash: str) -> int:
        """=== Instance method =========================================================================================
        Retrieves the number of confirmations for a specific transaction.
        :param tx_hash: str - The transaction hash (ID)
        :return: int - The number of confirmations
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

    def _retry_abort_scan(self, command):
        """
        A hidden static method to handle retries for aborting a UTXO scan.
        """
        retries = 0
        while mark := self._make_rpc_call(command, 'status'):
            print(f"mark: {mark}")
            if retries >= self._MAX_RETRIES:
                lg.error("Exceeded maximum retries to abort the UTXO set scan. Exiting...")
                raise RuntimeError("Unable to terminate the active UTXO set scan after retries.")

            # Attempt to abort the scan
            lg.warning(
                f"Retry {retries + 1}/{self._MAX_RETRIES}: UTXO set scan still active - attempting to abort.")
            self._make_rpc_call(command, 'abort')

            # Wait before the next retry
            lg.warning(f"Waiting: {self._WAIT_TIME_SECONDS} seconds before retrying...")
            for remaining in range(self._WAIT_TIME_SECONDS, 0, -1):
                time.sleep(1)
                print(f"Waiting: {remaining} seconds remaining.")
                lg.debug(f"Waiting: {remaining} seconds remaining.")

            retries += 1
        print(f"mark: {mark}")

        # Additional post-abort status validation
        lg.warning("Scan aborted. Verifying that the status has cleared...")
        for attempt in range(self._MAX_RETRIES):
            status = self._make_rpc_call(command, 'status')
            print(f"status: {status}")
            if not status:  # If the status is cleared, break the loop
                lg.info("Scan status successfully cleared.")
                break
            lg.debug(f"Status still not cleared. Attempt {attempt + 1}/{self._MAX_RETRIES}. Waiting...")
            time.sleep(self._WAIT_TIME_SECONDS)
        else:
            lg.error("Unable to verify that the scan status has cleared after abort.")
            raise RuntimeError("Node still reports an active scan even after abort attempts.")
        print(f"status: {status}")
