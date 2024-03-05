"""Basic DB actions. Mostly one-time processes."""

import os
from SalletBasePackage import SQL_interface as sql
from dotenv import load_dotenv

if __name__ == "__main__":
    keys_to_add = \
        [{"alias": 'pesz',              "owner": "MuranyiArpad",    'ip': "99.122.17.202",      "port": 8333,
          "features": "", "desc": "pesz gepe", "is_rpc": False},
         {"alias": 'mainNode',          "owner": "sziller.eu",      'ip': "10.3.77.42",         "port": 8042,
          "features": "", "desc": "sajat nodeom", "is_rpc": True},
         {"alias": 'kraken',            "owner": "kraken.com",      'ip': "198.210.44.74",      "port": 8333,
          "features": "", "desc": "nagy meno node", "is_rpc": False},
         {"alias": 'blockchain.info',   "owner": "",                'ip': "100.100.100.100",    "port": 0,
          "features": "", "desc": "kulso infoforras", "is_rpc": False}]

    # keys_to_del = ['01aa', '07aa', '08aa', '09aa', '10aa', '11aa', '12aa', '13aa', '14aa', '15aa', '16aa', '17aa', '18aa', '19aa']

    load_dotenv()
    session = sql.createSession(db_path=os.getenv("DB_PATH_VISOR"), style=os.getenv("DB_STYLE_VISOR"))
    
    # sql.db_delete_multiple_rows_by_filterkey(filterkey="hxstr",
    #                                          filtervalue_list=keys_to_del,
    #                                          db_table=os.getenv("DB_ID_TABLE_MD_PRVKEYS"),
    #                                          session_in=session)

    sql.ADD_rows_to_table(primary_key="alias", data_list=keys_to_add, db_table=os.getenv("DB_ID_TABLE_NODE"),
                          session_in=session)
    
