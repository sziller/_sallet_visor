"""Basic Node manager."""

import os
import logging
from dotenv import load_dotenv
from sql_access import sql_interface as sqla
from sql_bases.sqlbase_node.sqlbase_node import Node as sqlNode

from SalletNodePackage.NodeManager import NODEManager

lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('mngr_nodemanager.py'))

load_dotenv()

if __name__ == "__main__":
    
    # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50
    if os.getenv("ENV") == "development":
        logging.basicConfig(filename="./log/mngr_nodemanager.log", level=logging.DEBUG, filemode="w",
                            format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    elif os.getenv("ENV") == "staging":
        logging.basicConfig(filename="./log/mngr_nodemanager.log", level=logging.INFO, filemode="w",
                            format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    elif os.getenv("ENV") == "production":
        logging.basicConfig(filename="./log/mngr_nodemanager.log", level=logging.WARNING, filemode="w",
                            format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    else:
        raise Exception("CRITICAL  : 'ENV={}' is not a valid ENV-ironment definition in .env file!"
                        "\nUse ENV='development' or ENV='staging' or ENV='production'!".format(os.getenv("ENV")))
    lg.warning("START: {:>85} <<<".format('__name__ == "__main__" namespace: mngr_nodemanager.py'))

    lg.info("========================================================================================")
    lg.info("=== mngr_nodemanager                                                                 ===")
    lg.info("========================================================================================")
    
    session_test = sqla.createSession(db_fullname="./{}".format(os.getenv("DB_PATH_VISOR")),
                                      style=os.getenv("DB_STYLE_VISOR"),
                                      tables=None)
    mngr = NODEManager(session_in=session_test, row_obj=sqlNode.__table__)
    print(mngr.read_db())
    mngr.get_key_guided_rowdict()
    print("---------------------------")
    for key, value in mngr.node_obj_dict.items():
        print(f"{key}: {value}")

    for n in range(10):
        print("-------------------------------------------------")
        _next = mngr.return_next_node_instance()
        print(_next.is_rpc)
        print(_next.alias)
        print(_next.rpc_ip)
        print(_next.rpc_port)
        print(_next.rpc_user)
        print(_next.rpc_password)
        print(_next.ext_node_url)
