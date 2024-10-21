"""RPC_Host"""

import time
import inspect
import logging
import requests
import json
from requests.exceptions import Timeout, HTTPError, RequestException

# Set up a logger
lg = logging.getLogger(__name__)
lg.info("START: {:>83} <<<".format("RPCHost.py"))


class RPCHost(object):
    """=== Class name: RPCHost =========================================================================================
    Object translates calls into RPC commands to an address
    ========================================================================= by Sziller & internet & ChatGPT ==="""
    ccn = inspect.currentframe().f_code.co_name  # current class name
    
    def __init__(self, url: str, retries: int = 10, sleep_time: float = 0.5, timeout: int = 10):
        lg.debug("START: {:>85} <<<".format(self.ccn))
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}
        # --- custom made parameters ---
        self.retries: int                   = retries
        self.sleep_time: float              = sleep_time
        self.timeout: (int, None)           = timeout

    def call(self, rpc_method, *params, timeout: (int, None) = None):
        """=== Instance method =========================================================================================
        Method performs the actual calling of the RPC
        ========================================================================================== by Sziller ==="""
        payload = json.dumps({"method": rpc_method, "params": list(params), "jsonrpc": "2.0"})
        hadconnectionfailures = False
        timeout = timeout or self.timeout
        nr_retry = self.retries
        slp = self.sleep_time
        while True:
            try:
                response = self._session.post(self._url, headers=self._headers, data=payload, timeout=timeout)
            except (ConnectionError, Timeout) as e:
                nr_retry -= 1
                hadconnectionfailures = True
                if nr_retry == 0:
                    msg_final = 'RPC connection failed: \n{}'.format(e)
                    lg.critical(msg_final)
                    raise Exception(msg_final)
                msg_tmp = "Couldn't connect to RPC! Will try again in {} seconds ({} more tries)".format(slp, nr_retry)
                lg.warning(msg_tmp)
                time.sleep(slp)
            except RequestException as e:
                msg_final = "An unexpected error occurred - Failed RPC call:\n{}".format(e)
                lg.critical(msg_final)
                raise Exception(msg_final)
            else:
                if hadconnectionfailures:
                    msg_tmp = 'Connected for remote procedure call after retry.'
                    lg.warning(msg_tmp)
                    hadconnectionfailures = False
                break
        if response.status_code not in (200, 500):
            msg_tmp = 'RPC connection failure: ' + str(response.status_code) + ' ' + response.reason
            lg.critical(msg_tmp)
            raise Exception(msg_tmp)
        try:
            response_json = response.json()
        except json.JSONDecodeError as e:
            msg_final = 'Failed to decode JSON response: ' + str(e)
            lg.critical(msg_final, exc_info=True)
            raise Exception(msg_final)
        if 'error' in response_json and response_json['error'] is not None:
            msg_tmp = 'Error in RPC call:\n' + str(response_json['error'])
            lg.critical(msg_tmp)
            raise Exception(msg_tmp)
        return response_json['result']
