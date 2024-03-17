import logging
import inspect
from SalletVisorPackage.UtxoManager import UTXOManager as utxomngr
from SalletNodePackage.BitcoinNodeObject import Node as BtcNode

lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('mngr_utxomanager.py'))

if __name__ == "__main__":
    # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50
    logging.basicConfig(filename="./log/mngr_utxomanager-test.log", level=logging.NOTSET, filemode="w",
                        format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    lg.warning("START: {:>85} <<<".format('__name__ == "__main__" namespace: mngr_utxomanager.py'))

    lg.warning("========================================================================================")
    lg.warning("=== mngr_utxomanager                                                                 ===")
    lg.warning("========================================================================================")

    node = BtcNode(alias="sziller", is_rpc=True)
    mngr = utxomngr(node=node, dotenv_path="./.env")

    # -------------------------------------------------------------------------------------------------------
    # - Testing: UTXOManager                                                                    -   START   -
    # -------------------------------------------------------------------------------------------------------

    mngr.task_update_int_utxo_set_by_utxo_set_flat_yaml(unit_src="btc")
    lg.info(mngr.return_balance_by_addresslist(addresses=
                                               # {'1Ett9x7n37pth8yXZ2RW3EfprrWe6MPqsj'}
                                               None))
    lg.info(mngr.return_total_balance())
    for k, obj in mngr.utxo_obj_dict.items():
        lg.debug("{}: {}".format(k.__repr__(), obj.__repr__()))
    lg.info(mngr.task_export_int_utxo_to_yaml(unit_trg="sat", mode="utxo_set_flat", fullfilename="./T.yaml"))
