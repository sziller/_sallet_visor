'''RPC_Host'''
import time
import inspect
import logging
import requests
import json

'''RPC_Host'''

# Set up a logger
lg = logging.getLogger(__name__)
lg.info("START: {:>83} <<<".format("RPCHost.py"))


class RPCHost(object):
    """=== Class name: RPCHost =========================================================================================
    Object translates calls into RPC commands to an address
        =============================================================================== by Sziller & internet ==="""
    ccn = inspect.currentframe().f_code.co_name  # current class name
    
    def __init__(self, url: str):
        lg.info("START: {:>85} <<<".format(self.ccn))
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}

    def call(self, rpc_method, *params):
        """=== Method name: call =======================================================================================
        Method performs the actual calling of the RPC
        ========================================================================================== by Sziller ==="""
        payload = json.dumps({"method": rpc_method, "params": list(params), "jsonrpc": "2.0"})
        tries = 100
        slp = 5
        hadconnectionfailures = False
        while True:
            try:
                response = self._session.post(self._url, headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
                hadfailedconnections = True
                msg_tmp = "Couldn't connect for remote procedure call! Will try again in {} seconds ({} more tries)"\
                    .format(slp, tries)
                lg.warning(msg_tmp)
                time.sleep(slp)
            else:
                if hadconnectionfailures:
                    msg_tmp = 'Connected for remote procedure call after retry.'
                    lg.warning(msg_tmp)
                break
        if response.status_code not in (200, 500):
            msg_tmp = 'RPC connection failure: ' + str(response.status_code) + ' ' + response.reason
            lg.critical(msg_tmp)
            raise Exception(msg_tmp)
        response_json = response.json()
        if 'error' in response_json and response_json['error'] is not None:
            msg_tmp = 'Error in RPC call:\n' + str(response_json['error'])
            lg.critical(msg_tmp)
            raise Exception(msg_tmp)
        return response_json['result']
