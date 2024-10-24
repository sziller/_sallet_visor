"""
Sallet univers' node manager
by Sziller
"""

import os
import inspect
import logging
from typing import Optional
from dotenv import load_dotenv
from sql_access import sql_interface as sqla
from sql_bases.sqlbase_node.sqlbase_node import Node as sqlNode
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from SalletNodePackage.BitcoinNodeObject import Node

Base = declarative_base()

# Setting up logger                                         logger                      -   START   -
lg = logging.getLogger()
# Setting up logger                                         logger                      -   ENDED   -

lg.info("START     : {:>85} <<<".format('NodeManager.py'))


class NODEManager:
    """=== Classname: UTXOManager ======================================================================================
    Object manages custom made wallet's utxo related tasks, processes.
    :param dotenv_path: str - Path to the .env file used to load environmental variables.
    :param row_obj: Optional[Base] - Optional SQLAlchemy row object for database interaction.
    :param session_in: Optional[Session] - Optional SQLAlchemy session for database interaction.
    ============================================================================================== by Sziller ==="""
    ccn = inspect.currentframe().f_code.co_name  # current class name

    def __init__(self,
                 dotenv_path="./.env",
                 row_obj: Optional[Base] = None,
                 session_in: Optional[Session] = None):
        lg.info("__init__  : {:>60}".format(self.ccn))
        self.dotenv_path: str                   = dotenv_path
        self.row_obj: Optional[Base]            = row_obj
        self.session_in: Optional[Session]      = session_in
        # -------------------------------------------------------------------
        self.node_obj_dict: Optional[dict]      = None
        self.active_alias: Optional[str]        = None
        # -------------------------------------------------------------------
        try:
            load_dotenv(dotenv_path=dotenv_path)
        except Exception as e:
            lg.error(f"dotenv    : Error loading .env file:\n{e}")
            raise
    
    def read_db(self) -> list:
        """=== Instance method =========================================================================================
        Method reads in UTXO set from the database using SQLAlchemy.
        :return: list - A list of UTXO rows from the database, ordered by 'alias'.
        ========================================================================================== by Sziller ==="""
        node_list = sqla.QUERY_entire_table(session=self.session_in,
                                            row_obj=self.row_obj,
                                            ordered_by="alias")
        return node_list
    
    @staticmethod
    def get_primary_key_column_name() -> str:
        """=== Static method ===========================================================================================
        Retrieves the primary key column name from the `sqlNode` table.
        :return: str - The name of the primary key column.
        ========================================================================================== by Sziller ==="""
        primary_keys = [key.name for key in sqlNode.__table__.columns if key.primary_key]
        return primary_keys[0]

    def get_key_guided_rowdict(self):
        """=== Instance method =========================================================================================
        Creates and sorts a dictionary based on the primary key of the UTXO rows.
        The primary key is used as the key, and the row data (excluding the primary key) is stored as the value.
        ========================================================================================== by Sziller ==="""
        pk = self.get_primary_key_column_name()
        self.node_obj_dict =\
            dict(sorted({_[pk]: {k: v for k, v in _.items() if k != pk} for _ in self.read_db()}.items()))

    def return_next_node_instance(self):
        """=== Instance method =========================================================================================
        Iterates through the list of nodes and returns the next valid Node instance.
        This method checks if the node is RPC or API-based and loads the sensitive data accordingly.
        :return: Node - The next valid Node instance.
        ========================================================================================== by Sziller ==="""
        active_Node = None
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
                active_Node.features   = self.node_obj_dict[self.active_alias]['features']
                active_Node.owner      = self.node_obj_dict[self.active_alias]['owner']
                active_Node.desc       = self.node_obj_dict[self.active_alias]['desc']
                valid = True
        return active_Node
    
