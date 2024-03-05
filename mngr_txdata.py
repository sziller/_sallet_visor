import logging
import inspect
from SalletBasePackage.models import UtxoId
from SalletNodePackage.BitcoinNodeObject import Node


lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('mngr_txdata.py'))


if __name__ == "__main__":
    # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50
    logging.basicConfig(filename="./log/mngr_txdata-test.log", level=logging.NOTSET, filemode="w",
                        format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    lg.warning("START: {:>85} <<<".format('__name__ == "__main__" namespace: mngr_txdata.py'))
    
    lg.warning("========================================================================================")
    lg.warning("=== mngr_txdata test RPC                                                             ===")
    lg.warning("========================================================================================")
    nodeloc = Node(alias="sziller", is_rpc=True)
    nodeglb = Node(alias="block", is_rpc=False)

    txh = "ef37b2b383025ddf87209dc4a64dfb48010a274eddc3f16434fe14366241e360"
    txh = "7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741"
    
    lg.info(res_loc := nodeloc.nodeop_getrawtransaction(tx_hash=txh, verbose=False))
    lg.info(res_glb := nodeglb.nodeop_getrawtransaction(tx_hash=txh, verbose=False))
    
    import bitcoinlib
    
    print(res_glb == res_loc)
    
    tr_loc = bitcoinlib.transactions.Transaction.parse(rawtx=res_loc)
    
    for k, v in tr_loc.as_dict().items():
        print(k, v)
