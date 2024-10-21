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
        [{"alias": 'pesz',              "owner": "MuranyiArpad",    "ip": "99.122.17.202",      "port": 8333,
          "features": "nope",           "desc": "pesz gepe",        "is_rpc": False},
         {"alias": 'main',          "owner": "sziller.eu",      "ip": "10.3.77.42",         "port": 8042,
          "features": "nope",           "desc": "sajat nodeom",     "is_rpc": True},
         {"alias": 'kraken',            "owner": "kraken.com",      "ip": "198.210.44.74",      "port": 8333,
          "features": "extra",          "desc": "nagy meno node",   "is_rpc": False},
         {"alias": 'side',      "owner": "jenoe",           "ip": "100.100.100.100",    "port": 4242,
          "features": "nope",           "desc": "jencie",           "is_rpc": False},
         {"alias": 'jenoe02',      "owner": "jenoe",           "ip": "100.100.100.103",    "port": 4242,
          "features": "nopoe",          "desc": "jenci cucca 2",    "is_rpc": False},
         {"alias": 'blockchain.info',   "owner": "bc",              "ip": "20.40.60.80",        "port": 0,
          "features": "extra",          "desc": "kulso infoforras", "is_rpc": False},
         ]

    session = SQLi.createSession(db_fullname=os.getenv("DB_PATH_VISOR"), style="SQLite", tables=[sqlNode.__table__])
    lg.info("session   : created")

    lg.info("function  : ADD_rows_to_table()")
    a = SQLi.ADD_rows_to_table(primary_key="alias", data_list=keys_to_add, row_obj=sqlNode, session=session)
    lg.info(a)
    print(type(a))

    a = SQLi.QUERY_entire_table(session=session, row_obj=sqlNode.__table__, ordered_by=None)
