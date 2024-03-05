""" 
Sallet univers' node manager
by Sziller
"""

import os
import inspect
import logging
from dotenv import load_dotenv
from SalletBasePackage import SQL_interface as sqla, models
from SalletNodePackage.BitcoinNodeObject import Node
lg = logging.getLogger(__name__)
lg.info("START     : {:>85} <<<".format('NodeManager.py'))


class NODEManager:
    """=== Classname: UTXOManager ======================================================================================
        Object manages custom made wallet's utxo related tasks, processes.
        ============================================================================================== by Sziller ==="""
    ccn = inspect.currentframe().f_code.co_name  # current class name

    def __init__(self, dotenv_path="./.env", session_in=False):
        lg.info("__init__  : {:>60}".format(self.ccn))
        self.dotenv_path: str       = dotenv_path
        load_dotenv(dotenv_path=dotenv_path)
        self.session_in             = session_in
        self.node_list: list        = []
        self.node_obj_dict: dict    = {}  # {alias1: node_obj1, alias2: node_obj2}
        
        self.read_db()
        self.extract_node_set_dict()
        
        print("!!!!!!!!!!!")
        for k, v in self.node_obj_dict.items():
            print("{}: {}".format(k, v))
        print("!!!!!!!!!!!")
    
    def read_db(self):
        """=== Method name: read_db ====================================================================================
        Method reads in UTXO set from yaml file.
        ========================================================================================== by Sziller ==="""
        self.node_list: list = []
        self.node_list = sqla.QUERY_entire_table(ordered_by="owner",
                                                 db_table=os.getenv("DB_ID_TABLE_NODE"),
                                                 session_in=self.session_in)
        
    def extract_node_set_dict(self):
        """=== Method name: extract_node_set_dict ======================================================================
        Once self.node_list is given, this script creates a dictionary from it.
        ========================================================================================== by Sziller ==="""
        self.node_obj_dict = {}
        for _ in self.node_list:
            print(_)
        for node in self.node_list:
            print(node)
            alias = node['alias']
            # print(node)
            self.node_obj_dict[alias] = Node.construct(node)
