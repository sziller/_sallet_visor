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
    
    is_rpc = True
    active_Node = BtcNode(alias="sziller", is_rpc=is_rpc)
    if is_rpc:
        active_Node.update_sensitive_data(
            rpc_ip="10.3.77.37",
            rpc_port=8332,
            rpc_user="sziller",
            rpc_password="lwslabsffts")
    else:
        pass
        # active_Node.update_sensitive_data(
        #     ext_node_url=os.getenv(api_node_var.format(self.active_alias.upper()) + "_URL"))
    
    mngr = utxomngr(node=active_Node, dotenv_path="./.env")
    
    from dotenv import load_dotenv
    load_dotenv()
    addresslist = eval(os.getenv("ADDRESSES"))
    
    # -------------------------------------------------------------------------------------------------------
    # - Testing: UTXOManager                                                                    -   START   -
    # -------------------------------------------------------------------------------------------------------

    # lg.info(mngr.task_return_utxo_set_by_addresslist(address_list=addresslist))
    # print(mngr.task_update_int_utxo_set_by_db(unit_src="sat"))
    mngr.task_update_int_utxo_set_by_db(unit_src="btc")
    detailed_balance = mngr.return_balance_by_addresslist(addresses=addresslist)
    full_balance = mngr.return_total_balance()
    for addr, balance in detailed_balance.items():
        lg.info(f"{addr}: {balance}")
    lg.warning(f"TOTAL     : {full_balance}")
