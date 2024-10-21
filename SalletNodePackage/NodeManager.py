""" 
Sallet univers' node manager
by Sziller
"""

import os
import inspect
import logging
from dotenv import load_dotenv
from sql_access import sql_interface as sqla
from sql_bases.sqlbase_node.sqlbase_node import Node as sqlNode
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from SalletNodePackage.BitcoinNodeObject import Node
lg = logging.getLogger(__name__)
lg.info("START     : {:>85} <<<".format('NodeManager.py'))

Base = declarative_base()

class NODEManager:
    """=== Classname: UTXOManager ======================================================================================
        Object manages custom made wallet's utxo related tasks, processes.
        ============================================================================================== by Sziller ==="""
    ccn = inspect.currentframe().f_code.co_name  # current class name

    def __init__(self,
                 dotenv_path="./.env",
                 row_obj: (Base, None) = None,
                 session_in: (Session, None) = None):
        lg.info("__init__  : {:>60}".format(self.ccn))
        self.dotenv_path: str               = dotenv_path
        load_dotenv(dotenv_path=dotenv_path)
        self.row_obj: (Base, None)          = row_obj
        self.session_in: (Session, None)    = session_in
        self.node_obj_dict: (dict, None)    = None  # {alias1: node_obj1, alias2: node_obj2}
        # ------------------------------------------------
        self.active_alias: (str, None)      = None
    
    def read_db(self):
        """=== Method name: read_db ====================================================================================
        Method reads in UTXO set from yaml file.
        ========================================================================================== by Sziller ==="""
        node_list = sqla.QUERY_entire_table(session=self.session_in,
                                            row_obj=self.row_obj,
                                            ordered_by="alias")
        return node_list
    
    @staticmethod
    def get_primary_key_column_name():
        """=== Instance method =========================================================================================
        ========================================================================================== by Sziller ==="""
        primary_keys = [key.name for key in sqlNode.__table__.columns if key.primary_key]
        return primary_keys[0]

    def get_key_guided_rowdict(self):
        """=== Instance method =========================================================================================
        
        ========================================================================================== by Sziller ==="""
        pk = self.get_primary_key_column_name()
        self.node_obj_dict =\
            dict(sorted({_[pk]: {k: v for k, v in _.items() if k != pk} for _ in self.read_db()}.items()))

    def return_next_node_instance(self):
        """=== Instance method =========================================================================================
        ========================================================================================== by Sziller ==="""
        valid = False
        while not valid:
            # Dynamically get the list of keys
            rpc_node_var = os.getenv("RPC_NODE_VARIABLE")
            api_node_var = os.getenv("API_NODE_VARIABLE")
            keys = list(self.node_obj_dict.keys())
            # Determine the current index based on the active_key
            if self.active_alias is None:
                # If it's the first call, start from the first key
                self.active_alias = keys[0]
            else:
                # Find the current index of active_key
                current_index = keys.index(self.active_alias)
                # Move to the next index, wrapping around
                self.active_alias = keys[(current_index + 1) % len(keys)]
            is_rpc = bool(self.node_obj_dict[self.active_alias]['is_rpc'])
            active_Node = Node(alias=self.active_alias, is_rpc=is_rpc)
            if is_rpc:
                active_Node.update_sensitive_data(
                    rpc_ip=os.getenv(rpc_node_var.format(self.active_alias.upper()) + "_IP"),
                    rpc_port=os.getenv(rpc_node_var.format(self.active_alias.upper()) + "_PORT"),
                    rpc_user=os.getenv(rpc_node_var.format(self.active_alias.upper()) + "_USER"),
                    rpc_password=os.getenv(rpc_node_var.format(self.active_alias.upper()) + "_PSSW"))
            else:
                active_Node.update_sensitive_data(
                    ext_node_url=os.getenv(api_node_var.format(self.active_alias.upper()) + "_URL"))
            if active_Node.is_valid():
                valid = True
        return active_Node
    
    
if __name__ == "__main__":
    load_dotenv()
    session_test = sqla.createSession(db_fullname="../{}".format(os.getenv("DB_PATH_VISOR")),
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
    
