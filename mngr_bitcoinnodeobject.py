import logging
import inspect
from SalletBasePackage.models import UtxoId
from SalletNodePackage.BitcoinNodeObject import Node

lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('mngr_bitcoinnodeobject.py'))

if __name__ == "__main__":
    # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50
    logging.basicConfig(filename="./log/mngr_bitcoinnodeobject.log", level=logging.NOTSET, filemode="w",
                        format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    lg.warning("START: {:>85} <<<".format('__name__ == "__main__" namespace: mngr_bitcoinnodeobject.py'))

    lg.warning("========================================================================================")
    lg.warning("=== mngr_bitcoinodeobject                                                            ===")
    lg.warning("========================================================================================")

    log_time = ""
    rootpath_all_config = ".."

    import bitcoinlib

    txid = "ef37b2b383025ddf87209dc4a64dfb48010a274eddc3f16434fe14366241e360"
    txid = "7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741"
    # coinbases
    # txid = "56f26b369c93ba1098afb14fdf213209018904bcef82114a8f019de069dc7a7b"
    # txid = "5029302f0c8c1c2ef856194ca8a7f78a7b6ba029b3a432466ba1d4ab2105aef5"
    # txid = "0b6dc7910ed25a79ab6ce12e6a0dcb991c44708580b18f223b00a4526fd10bbf"
    # txid = "9636a0d06128c89121b442ee56200a28b99350e658f4f0774db3ea64daad872a"
    # txid = "525c4eef55f597d0344345ce9439b1e7eeb72053d0682eb2c6910a4f4d695987"
    # txid = "611b40973fe68cc42b70ae5af365a449af458d76086415c6fa6c45364c36278e"
    txid = "7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741"

    txid = "ffb5307b8f3486e077f0df869332b128697ddbedeb51c55f181d84bc92961869"

    lg.warning("========================================================================================")
    lg.warning("=== nodeop_getconnectioncount                                                        ===")
    lg.warning("========================================================================================")
    node = Node(dotenv_path="./.env", is_rpc=True, alias="sziller", owner="sziller.eu")
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getconnectioncount'))
    try:
        lg.info(node.nodeop_getconnectioncount())
    except:
        lg.error("FAILED    : <nodeop_getconnectioncount>")

    lg.warning("========================================================================================")
    lg.warning("=== nodeop_getconnectioncount                                                        ===")
    lg.warning("========================================================================================")
    node = Node(dotenv_path="../.env", is_rpc=False, alias="sziller", owner="sziller.eu")
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getconnectioncount'))
    try:
        lg.info(node.nodeop_getconnectioncount())
    except:
        lg.error("FAILED    : <nodeop_getconnectioncount>")

    lg.warning("========================================================================================")
    lg.warning("=== SHOWING actual blockheight - real time:")
    lg.warning("========================================================================================")
    node = Node(dotenv_path="./.env", is_rpc=False, alias="sziller", owner="sziller.eu")
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getblockcount'))
    try:
        lg.info(node.nodeop_getblockcount())
    except:
        lg.error("FAILED    : <nodeop_getblockcount>")

    lg.warning("========================================================================================")
    lg.warning("=== TX request:  blockchain.info, raw, parsed by bitcoinlib:")
    lg.warning("========================================================================================")
    node = Node(dotenv_path="./.env", is_rpc=False, alias="sziller", owner="sziller.eu")
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=False)
        tx_data_parsed = bitcoinlib.transactions.Transaction.parse(tx_data)
        for k, v in tx_data_parsed.as_dict().items():
            lg.debug("{}: {}".format(k, v))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")

    lg.warning("========================================================================================")
    lg.warning("=== TX request:  local Node, raw, parsed by bitcoinlib:                              ===")
    lg.warning("========================================================================================")
    node = Node(dotenv_path="./.env", is_rpc=True, alias="sziller", owner="sziller.eu")
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=False)
        tx_data_parsed = bitcoinlib.transactions.Transaction.parse(tx_data)
        for k, v in tx_data_parsed.as_dict().items():
            lg.debug("{}: {}".format(k, v))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")

    lg.warning("========================================================================================")
    lg.warning("=== TX request:  blockchain.info, as dict, parsed by blockchain.info:                ===")
    lg.warning("========================================================================================")
    node = Node(dotenv_path="./.env", is_rpc=False, alias="sziller", owner="sziller.eu")
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=True)
        for k, v in tx_data.items():
            lg.debug("{}: {}".format(k, v))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")

    lg.warning("========================================================================================")
    lg.warning("=== TX request:  local Node, as dict, parsed by Node:                                ===")
    lg.warning("========================================================================================")
    node = Node(dotenv_path="./.env", is_rpc=True, alias="sziller", owner="sziller.eu")
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=True)
        for k, v in tx_data.items():
            lg.debug("{}: {}".format(k, v))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")

    lg.warning("========================================================================================")
    lg.warning("=== TX request:  local Node, raw,  not parsed:                                       ===")
    lg.warning("========================================================================================")
    node = Node(dotenv_path="./.env", is_rpc=True, alias="sziller", owner="sziller.eu")
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=False)
        for k, v in tx_data.items():
            lg.debug("{}: {}".format(k, v))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")
    # # ef37b2b383025ddf87209dc4a64dfb48010a274eddc3f16434fe14366241e360

    lg.warning("========================================================================================")
    lg.warning("=== nodeop_get_tx_outpoint_value                                                     ===")
    lg.warning("========================================================================================")
    node = Node(dotenv_path="./.env", is_rpc=False, alias="sziller", owner="sziller.eu")
    op_id = UtxoId.construct(
        {"txid": '7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741',
         "n": 0})  # creating matching outputs outpoint ID
    print(node.nodeop_get_tx_outpoint_value(tx_outpoint=op_id))

    lg.warning("========================================================================================")
    lg.warning("=== nodeop_get_utxo_id_set_with_address                                              ===")
    lg.warning("========================================================================================")
    node = Node(dotenv_path="./.env", is_rpc=True, alias="sziller", owner="sziller.eu")
    node.nodeop_get_utxo_id_set_with_address(address_list=["19zohsYZfQX6TG9FjCeD8FW21q3yHj6KWA", "18My7aToHGUhptu3CbrivFBw6GLgFoNJMQ"])
