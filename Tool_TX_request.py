#!/usr/bin/env python3

"""Quick app to read TX data
by Sziller"""
import logging
from SalletNodePackage import BitcoinNodeObject as BNOb
from DataVisualizer.data2str import rdf
import sys

# Setting up logger                                         logger                      -   START   -
lg = logging.getLogger()
# Setting up logger                                         logger                      -   ENDED   -
# NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50


def tool_node_tx_request():
    """=== App name: app_tx_request ====================================================================================
    Quick script to receive a Transactions dictionary representation.
    This app contacts your own node.
    
    Use: from the termial
    ============================================================================================== by Sziller ==="""
    node = BNOb.Node(alias="sziller_node", is_rpc=True)
    tx_hash = str(input("Enter tx ID: "))
    
    tx_data = node.nodeop_getrawtransaction(tx_hash=tx_hash, verbose=True)
    data_as_displayed = rdf(data=tx_data)
    lg.info("Transaction: \n" + data_as_displayed)
    print(data_as_displayed)


if __name__ == "__main__":
    logging.basicConfig(filename="./log/tool_tx_request.log",
                        level=logging.NOTSET,
                        filemode="w",
                        format="%(asctime)s [%(levelname)8s]: %(message)s",
                        datefmt='%y%m%d %H:%M:%S')

    lg.warning("START: {:>85} <<<".format('Tool_TX_request.py'))
    
    try:
        # When starting from icon:
        testdata = sys.argv[0]
        print("--- Initiated by ICONCLICK ---")
        # ------------------------------------------------------
    except IndexError:
        # When starting from IDLE:
        testdata = False
        print("--- Initiated over IDLE ---")
        # ------------------------------------------------------
    tool_node_tx_request()
    lg.warning("ENDED: {:>85} <<<".format('Tool_TX_request.py'))
