import logging
import os
from dotenv import load_dotenv
from SalletBasePackage.models import UtxoId
from SalletNodePackage.BitcoinNodeObject import Node

lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('mngr_bitcoinnodeobject.py'))

load_dotenv()

if __name__ == "__main__":
    
    # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50
    if os.getenv("ENV") == "development":
        logging.basicConfig(filename="./log/mngr_bitcoinnodeobject.log", level=logging.DEBUG, filemode="w",
                            format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    elif os.getenv("ENV") == "staging":
        logging.basicConfig(filename="./log/mngr_bitcoinnodeobject.log", level=logging.INFO, filemode="w",
                            format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    elif os.getenv("ENV") == "production":
        logging.basicConfig(filename="./log/mngr_bitcoinnodeobject.log", level=logging.WARNING, filemode="w",
                            format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    else:
        raise Exception("CRITICAL  : 'ENV={}' is not a valid ENV-ironment definition in .env file!"
                        "\nUse ENV='development' or ENV='staging' or ENV='production'!".format(os.getenv("ENV")))
    lg.warning("START: {:>85} <<<".format('__name__ == "__main__" namespace: mngr_bitcoinnodeobject.py'))

    lg.info("========================================================================================")
    lg.info("=== mngr_bitcoinodeobject                                                            ===")
    lg.info("========================================================================================")
    
    node = Node(is_rpc=True, alias="sziller")
    node.update_sensitive_data(rpc_ip=os.getenv("RPC_BC_MAIN_IP"),
                               rpc_port=os.getenv("RPC_BC_MAIN_PORT"),
                               rpc_user=os.getenv("RPC_BC_MAIN_USER"),
                               rpc_password=os.getenv("RPC_BC_MAIN_PSSW"))

    node = Node(is_rpc=False, alias="blockchain.info")
    node.update_sensitive_data(ext_node_url=os.getenv("API_BC_BLOCKCHAIN.INFO_URL"))
        
    node.validate_api_url()

    log_time = ""
    rootpath_all_config = ".."

    import bitcoinlib

    # txid = "ef37b2b383025ddf87209dc4a64dfb48010a274eddc3f16434fe14366241e360"
    # txid = "7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741"
    # coinbases
    # txid = "56f26b369c93ba1098afb14fdf213209018904bcef82114a8f019de069dc7a7b"
    # txid = "5029302f0c8c1c2ef856194ca8a7f78a7b6ba029b3a432466ba1d4ab2105aef5"
    # txid = "0b6dc7910ed25a79ab6ce12e6a0dcb991c44708580b18f223b00a4526fd10bbf"
    # txid = "9636a0d06128c89121b442ee56200a28b99350e658f4f0774db3ea64daad872a"
    # txid = "525c4eef55f597d0344345ce9439b1e7eeb72053d0682eb2c6910a4f4d695987"
    # txid = "611b40973fe68cc42b70ae5af365a449af458d76086415c6fa6c45364c36278e"
    # txid = "7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741"

    txid = "ffb5307b8f3486e077f0df869332b128697ddbedeb51c55f181d84bc92961869"

    lg.info("==========================================================================================")
    lg.info("=== nodeop_getconnectioncount - RPC                                                    ===")
    lg.info("==========================================================================================")
    node = Node(is_rpc=True, alias="sziller")
    node.update_sensitive_data(rpc_ip=os.getenv("RPC_BC_MAIN_IP"),
                               rpc_port=os.getenv("RPC_BC_MAIN_PORT"),
                               rpc_user=os.getenv("RPC_BC_MAIN_USER"),
                               rpc_password=os.getenv("RPC_BC_MAIN_PSSW"))
    
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getconnectioncount'))
    try:
        lg.info("ANSWER    : {:>80}".format(node.nodeop_getconnectioncount()))
    except:
        lg.error("FAILED    : <nodeop_getconnectioncount>")

    lg.info("==========================================================================================")
    lg.info("=== nodeop_getconnectioncount - API                                                    ===")
    lg.info("==========================================================================================")
    node = Node(is_rpc=False, alias="sziller")
    node.update_sensitive_data(ext_node_url=os.getenv("API_BC_BLOCKCHAIN.INFO_URL"))
    
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getconnectioncount'))
    try:
        lg.info("ANSWER    : {:>80}".format(node.nodeop_getconnectioncount()))
    except:
        lg.error("FAILED    : <nodeop_getconnectioncount>")

    lg.info("==========================================================================================")
    lg.info("=== showing actual BLOCKHEIGHT - RPC - real time:                                      ===")
    lg.info("==========================================================================================")
    node = Node(is_rpc=True, alias="sziller")
    node.update_sensitive_data(rpc_ip=os.getenv("RPC_BC_MAIN_IP"),
                               rpc_port=os.getenv("RPC_BC_MAIN_PORT"),
                               rpc_user=os.getenv("RPC_BC_MAIN_USER"),
                               rpc_password=os.getenv("RPC_BC_MAIN_PSSW"))

    lg.info("TESTING   : {:>80} <<<".format('nodeop_getblockcount'))
    try:
        lg.info("ANSWER    : {:>80}".format(node.nodeop_getblockcount()))
    except:
        lg.error("FAILED    : <nodeop_getblockcount>")

    lg.info("==========================================================================================")
    lg.info("=== showing actual BLOCKHEIGHT - API - real time:                                      ===")
    lg.info("==========================================================================================")
    node = Node(is_rpc=False, alias="sziller")
    node.update_sensitive_data(ext_node_url=os.getenv("API_BC_BLOCKCHAIN.INFO_URL"))
    
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getblockcount'))
    try:
        lg.info("ANSWER    : {:>80}".format(node.nodeop_getblockcount()))
    except:
        lg.error("FAILED    : <nodeop_getblockcount>")

    lg.info("========================================================================================")
    lg.info("=== nodeop_getrawtransaction - RPC, hex, unparsed                                    ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=True, alias="sziller")
    node.update_sensitive_data(rpc_ip=os.getenv("RPC_BC_MAIN_IP"),
                               rpc_port=os.getenv("RPC_BC_MAIN_PORT"),
                               rpc_user=os.getenv("RPC_BC_MAIN_USER"),
                               rpc_password=os.getenv("RPC_BC_MAIN_PSSW"))

    lg.info("TESTING   : {:>80} <<<".format('nodeop_getrawtransaction'))
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=False)
        lg.info("ANSWER    : {}".format(tx_data))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")

    lg.info("========================================================================================")
    lg.info("=== nodeop_getrawtransaction - API, hex, unparsed                                    ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=False, alias="sziller")
    node.update_sensitive_data(ext_node_url=os.getenv("API_BC_BLOCKCHAIN.INFO_URL"))
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getrawtransaction'))
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=False)
        lg.info("ANSWER    : {}".format(tx_data))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")

    lg.info("========================================================================================")
    lg.info("=== nodeop_getrawtransaction - RPC, hex, parsed by bitcoinlib:                       ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=True, alias="sziller")
    node.update_sensitive_data(rpc_ip=os.getenv("RPC_BC_MAIN_IP"),
                               rpc_port=os.getenv("RPC_BC_MAIN_PORT"),
                               rpc_user=os.getenv("RPC_BC_MAIN_USER"),
                               rpc_password=os.getenv("RPC_BC_MAIN_PSSW"))
    # -------------------------------------------------------------------------------------------------
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getrawtransaction'))
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=False)
        tx_data_parsed = bitcoinlib.transactions.Transaction.parse(tx_data)
        lg.info("ANSWER    :")
        for k, v in tx_data_parsed.as_dict().items():
            lg.info(" - {}: {}".format(k, v))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")
    
    lg.info("========================================================================================")
    lg.info("=== nodeop_getrawtransaction - API, hex, parsed by bitcoinlib:")
    lg.info("========================================================================================")
    node = Node(is_rpc=False, alias="sziller")
    node.update_sensitive_data(ext_node_url=os.getenv("API_BC_BLOCKCHAIN.INFO_URL"))
    # -------------------------------------------------------------------------------------------------
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getrawtransaction'))
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=False)
        tx_data_parsed = bitcoinlib.transactions.Transaction.parse(tx_data)
        for k, v in tx_data_parsed.as_dict().items():
            lg.info(" - {}: {}".format(k, v))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")

    lg.info("========================================================================================")
    lg.info("=== nodeop_getrawtransaction - RCP, dict, parsed by Node                             ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=True, alias="sziller")
    node.update_sensitive_data(rpc_ip=os.getenv("RPC_BC_MAIN_IP"),
                               rpc_port=os.getenv("RPC_BC_MAIN_PORT"),
                               rpc_user=os.getenv("RPC_BC_MAIN_USER"),
                               rpc_password=os.getenv("RPC_BC_MAIN_PSSW"))
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getrawtransaction'))
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=True)
        lg.info("ANSWER    :")
        for k, v in tx_data.items():
            lg.info(" - {}: {}".format(k, v))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")

    lg.info("========================================================================================")
    lg.info("=== nodeop_getrawtransaction - API, dict, parsed by blockchain.info:                ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=False, alias="sziller")
    node.update_sensitive_data(ext_node_url=os.getenv("API_BC_BLOCKCHAIN.INFO_URL"))
    # -------------------------------------------------------------------------------------------------
    lg.info("TESTING   : {:>80} <<<".format('nodeop_getrawtransaction'))
    try:
        tx_data = node.nodeop_getrawtransaction(tx_hash=txid, verbose=True)
        lg.info("ANSWER    :")
        for k, v in tx_data.items():
            lg.info(" - {}: {}".format(k, v))
    except:
        lg.error("FAILED    : <nodeop_getrawtransaction>")

    lg.info("========================================================================================")
    lg.info("=== nodeop_get_tx_outpoint_value - RPC                                               ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=True, alias="sziller")
    node.update_sensitive_data(rpc_ip=os.getenv("RPC_BC_MAIN_IP"),
                               rpc_port=os.getenv("RPC_BC_MAIN_PORT"),
                               rpc_user=os.getenv("RPC_BC_MAIN_USER"),
                               rpc_password=os.getenv("RPC_BC_MAIN_PSSW"))

    op_id = UtxoId.construct(
        {"txid": '7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741',
         "n": 0})  # creating matching outputs outpoint ID
    
    lg.info("TESTING   : {:>80} <<<".format('nodeop_get_tx_outpoint_value'))
    try:
        value = node.nodeop_get_tx_outpoint_value(tx_outpoint=op_id)
        lg.info("ANSWER    : {:>80}".format(value))
    except:
        lg.error("FAILED    : <nodeop_get_tx_outpoint_value>")

    lg.info("========================================================================================")
    lg.info("=== nodeop_get_tx_outpoint_value - API                                               ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=False, alias="sziller")
    node.update_sensitive_data(ext_node_url=os.getenv("API_BC_BLOCKCHAIN.INFO_URL"))

    op_id = UtxoId.construct(
        {"txid": '7c22da907dbf509b5f60c8b60c8baa68423b9023b99cd5701dfb1a592ffa5741',
         "n": 0})  # creating matching outputs outpoint ID
    lg.info("TESTING   : {:>80} <<<".format('nodeop_get_tx_outpoint_value'))
    try:
        value = node.nodeop_get_tx_outpoint_value(tx_outpoint=op_id)
        lg.info("ANSWER    : {:>80}".format(value))
    except:
        lg.error("FAILED    : <nodeop_get_tx_outpoint_value>")

    lg.info("========================================================================================")
    lg.info("=== nodeop_confirmations - RPC                                                       ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=True, alias="sziller")
    node.update_sensitive_data(rpc_ip=os.getenv("RPC_BC_MAIN_IP"),
                               rpc_port=os.getenv("RPC_BC_MAIN_PORT"),
                               rpc_user=os.getenv("RPC_BC_MAIN_USER"),
                               rpc_password=os.getenv("RPC_BC_MAIN_PSSW"))

    lg.info("TESTING   : {:>80} <<<".format('nodeop_confirmations'))
    try:
        value = node.nodeop_confirmations(tx_hash=txid)
        lg.info("ANSWER    : {:>80}".format(value))
    except:
        lg.error("FAILED    : <nodeop_get_tx_outpoint_value>")

    lg.info("========================================================================================")
    lg.info("=== nodeop_confirmations - API                                                       ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=False, alias="sziller")
    node.update_sensitive_data(ext_node_url=os.getenv("API_BC_BLOCKCHAIN.INFO_URL"))

    lg.info("TESTING   : {:>80} <<<".format('nodeop_confirmations'))
    try:
        value = node.nodeop_confirmations(tx_hash=txid)
        lg.info("ANSWER    : {:>80}".format(value))
    except:
        lg.error("FAILED    : <nodeop_get_tx_outpoint_value>")

    lg.info("========================================================================================")
    lg.info("=== nodeop_get_utxo_set_by_addresslist - API (not allowed)                           ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=False, alias="sziller")
    node.update_sensitive_data(ext_node_url=os.getenv("API_BC_BLOCKCHAIN.INFO_URL"))

    lg.info("TESTING   : {:>80} <<<".format('nodeop_get_utxo_set_by_addresslist'))
    addresslist = eval(os.getenv("ADDRESSES"))
    try:
        ans = node.nodeop_get_utxo_set_by_addresslist(address_list=addresslist)
        print("ANSWER    : {:>80}".format(ans))
    except:
        lg.error("FAILED    : <nodeop_get_utxo_set_by_addresslist>")
    
    lg.info("========================================================================================")
    lg.info("=== nodeop_get_utxo_set_by_addresslist - RPC (only)                                  ===")
    lg.info("========================================================================================")
    node = Node(is_rpc=True, alias="sziller")
    node.update_sensitive_data(rpc_ip=os.getenv("RPC_BC_MAIN_IP"),
                               rpc_port=os.getenv("RPC_BC_MAIN_PORT"),
                               rpc_user=os.getenv("RPC_BC_MAIN_USER"),
                               rpc_password=os.getenv("RPC_BC_MAIN_PSSW"))

    lg.info("TESTING   : {:>80} <<<".format('nodeop_get_utxo_set_by_addresslist'))
    addresslist = eval(os.getenv("ADDRESSES"))
    try:
        ans = node.nodeop_get_utxo_set_by_addresslist(address_list=addresslist)
        print("ANSWER    : {:>80}".format(ans))
    except:
        lg.error("FAILED    : <nodeop_get_utxo_set_by_addresslist>")
