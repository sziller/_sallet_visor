"""Basic DB actions. Mostly one-time processes."""

import logging
from SalletSqlPackage import SQL_interface as SQLi
from SalletSqlPackage import SQL_bases as SQLb
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
         {"alias": 'mainNode',          "owner": "sziller.eu",      "ip": "10.3.77.42",         "port": 8042,
          "features": "nope",           "desc": "sajat nodeom",     "is_rpc": True},
         {"alias": 'kraken',            "owner": "kraken.com",      "ip": "198.210.44.74",      "port": 8333,
          "features": "extra",          "desc": "nagy meno node",   "is_rpc": False},
         {"alias": 'jenoe01.info',      "owner": "jenoe",           "ip": "100.100.100.100",    "port": 4242,
          "features": "nope",           "desc": "jencie",           "is_rpc": False},
         {"alias": 'jenoe02.info',      "owner": "jenoe",           "ip": "100.100.100.103",    "port": 4242,
          "features": "nopoe",          "desc": "jenci cucca 2",    "is_rpc": False},
         {"alias": 'blockchain.info',   "owner": "bc",              "ip": "20.40.60.80",        "port": 0,
          "features": "extra",          "desc": "kulso infoforras", "is_rpc": False},
         ]

    session = SQLi.createSession(db_path="/home/sziller/test.db", style="SQLite", tables=[SQLb.Node.__table__])
    lg.info("session   : created")

    lg.info("function  : ADD_rows_to_table()")
    a = SQLi.ADD_rows_to_table(primary_key="alias", data_list=keys_to_add, row_obj=SQLb.Node, session=session)
    lg.info(a)
    print(type(a))

    lg.info("function  : ADD_rows_to_table()")
    # SQLi.DELETE_multiple_rows_by_filterkey(filterkey="port",
    #                                           filtervalue_list=['0', '8333'],
    #                                           row_obj=SQLb.Node,
    #                                           session=session)
    
    # a = SQLi.QUERY_entire_table(ordered_by="alias", row_obj=SQLb.Node, session=session)
    # print(a)
    # print(type(a))
    # 
    # SQLi.MODIFY_multiple_rows_by_column_to_value(filterkey="port", filtervalue_list=[8333, 8042],
    #                                              target_key='ip', target_value="x",
    #                                              row_obj=SQLb.Node, session=session)

    a = SQLi.QUERY_rows_by_column_filtervalue_list_ordered(filterkey="port", filtervalue_list=[4242, 8042],
                                                           ordered_by='alias', row_obj=SQLb.Node,
                                                           session=session)
    for _ in a:
        lg.info(_)
    print(type(a))

    SQLi.MODIFY_multiple_rows_by_column_by_dict(filterkey="owner", mod_dict={'jenoe': {'ip': "---", 'port': 10000},
                                                                             'sziller.eu': {'desc': 'yuhoooo'}},
                                                row_obj=SQLb.Node, session=session)
