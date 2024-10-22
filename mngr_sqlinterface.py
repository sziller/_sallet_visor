"""Basic DB actions. Mostly one-time processes."""

import logging
import os

from sql_access import sql_interface as SQLi
from sql_bases.sqlbase_node.sqlbase_node import Node as sqlNode
from dotenv import load_dotenv

lg = logging.getLogger(__name__)
lg.info("START: {:>85} <<<".format('mngr_sqlinterface.py'))

if __name__ == "__main__":
    logging.basicConfig(filename="./log/mngr_sqlinterface.log", level=logging.NOTSET, filemode="w",
                        format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    lg.warning("START: {:>85} <<<".format('__name__ == "__main__" namespace: mngr_sqlinterface.py'))
    
    load_dotenv()
    keys_to_add = \
        [{"alias": 'main', "owner": "sziller.eu", "features": "nope", "is_rpc": True,
          'ip': '0.0.0.0', 'port': 0, "desc": "sajat nodeom"},
         {"alias": 'backup', "owner": "sziller.eu", "features": "nope", "is_rpc": True,
          'ip': '0.0.0.0', 'port': 0, "desc": "masodlagos node"},
         {"alias": 'xxx.info', "owner": "xxx.com", "features": "extra", "is_rpc": False,
          'ip': '0.0.0.0', 'port': 0, "desc": "kulso infoforras masik"},
         {"alias": 'blockchain.info', "owner": "blockchain.com", "features": "extra", "is_rpc": False,
          'ip': '0.0.0.0', 'port': 0, "desc": "kulso infoforras"},
         ]

    session = SQLi.createSession(db_fullname=os.getenv("DB_PATH_VISOR"), style="SQLite", tables=[sqlNode.__table__])
    lg.info("session   : created")

    lg.info("function  : ADD_rows_to_table()")
    a = SQLi.ADD_rows_to_table(primary_key="alias", data_list=keys_to_add, row_obj=sqlNode, session=session)
    lg.info(a)
    a = SQLi.QUERY_entire_table(session=session, row_obj=sqlNode.__table__, ordered_by=None)
