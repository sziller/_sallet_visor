"""
MaNaGeR style script to enable manual testing of classes from __main__ scope

"""

import logging
import inspect
import os

from SalletVisorPackage.UtxoManager import UTXOManager as utxomngr
from SalletNodePackage.BitcoinNodeObject import Node as BtcNode

# Setting up logger                                         logger                      -   START   -
lg = logging.getLogger()
# Setting up logger                                         logger                      -   ENDED   -

lg.info("START: {:>85} <<<".format('mngr_utxomanager.py'))

if __name__ == "__main__":
    # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50
    logging.basicConfig(filename="./log/mngr_utxomanager.log", level=logging.NOTSET, filemode="w",
                        format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    lg.warning("START: {:>85} <<<".format('__name__ == "__main__" namespace: mngr_utxomanager.py'))

    lg.warning("========================================================================================")
    lg.warning("=== mngr_utxomanager                                                                 ===")
    lg.warning("========================================================================================")

    node = BtcNode(alias="sziller", is_rpc=True)
    mngr = utxomngr(node=node, dotenv_path="./.env")
    
    from dotenv import load_dotenv
    load_dotenv()
    addresslist = eval(os.getenv("ADDRESSES"))
    print(addresslist)
    print(type(addresslist))
    
    # -------------------------------------------------------------------------------------------------------
    # - Testing: UTXOManager                                                                    -   START   -
    # -------------------------------------------------------------------------------------------------------

    lg.info(mngr.task_return_utxo_set_by_addresslist(address_list=addresslist))
