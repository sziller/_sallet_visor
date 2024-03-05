""" 
Sallet univers' utxo manager
by Sziller
"""

import os
import yaml
import logging
import inspect
from dotenv import load_dotenv
from SalletBasePackage import SQL_interface as sqla, models
from SalletBasePackage import units
from SalletNodePackage import BitcoinNodeObject as BtcNode


# Setting up logger                                         logger                      -   START   -
lg = logging.getLogger()
# Setting up logger                                         logger                      -   ENDED   -

lg.info("START     : {:>85} <<<".format('UtxoManager.py'))


class UTXOManager:
    """=== Classname: UTXOManager ======================================================================================
    Object manages custom made wallet's utxo related tasks, processes.
    ============================================================================================== by Sziller ==="""
    # current class name
    ccn = inspect.currentframe().f_code.co_name  # current class name
    
    def __init__(self, dotenv_path: str ="./.env", session_in: bool=False, from_yaml: bool = False):
        lg.info("__init__  : {:>60}".format(self.ccn))
        self.dotenv_path: str               = dotenv_path
        load_dotenv(dotenv_path=dotenv_path)
        self.from_yaml: bool                = from_yaml
        self.balance_total: float           = 0
        self.address_set: set               = set()
        self.sums_per_address_dict: dict    = {}
        self.utxo_set: list                 = []  # list of all utxo data
        self.utxo_set_dict: dict            = {}  # set of utxo_id's
        if not session_in:
            self.session_in = sqla.createSession(db_path=os.getenv("DB_PATH_UTXO"), style=os.getenv("DB_STYLE_UTXO"))
        else:
            self.session_in = session_in
        
        self.path_map: dict     = {"utxo": "UTXO_SET_YAML_PATH",    "utxo_id": "utxo_set_dict_YAML_PATH"}
        self.assign_map: dict   = {"utxo": "utxo_set",              "utxo_id": "utxo_set_dict"}
        
        if self.from_yaml:
            self.read_yaml()
        else:
            self.read_db()
        
        self.extract_uxto_set_dict()
        self.extract_total_balance()
        self.export_utxoset_to_db()
        
    def sync_with_blockchain(self):
        """=== Method name: sync_with_blockchain =======================================================================
        Method syncronizes local UTXO set with Blockchain instance
        ========================================================================================== by Sziller ==="""
        pass
    
    def read_yaml(self, mode: str = "utxo"):
        """=== Method name: read_yaml ==================================================================================
        Method reads in data from yaml file.
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current class name
        
        if mode in list(self.path_map.keys()):
            yaml_path = os.getenv(self.path_map[mode])
            with open(yaml_path, 'r') as stream:
                try:
                    read_in_yaml = yaml.safe_load(stream)
                    lg.info("read in   : {}-set from {}\n - says {}".format(mode, yaml_path, self.ccn))
                except yaml.YAMLError as exc:
                    msg = "read in   : failed from {}\n - says {}".format(yaml_path, self.ccn)
                    lg.critical(exc)
                    lg.critical(msg)
                    raise Exception(msg)
            setattr(self, self.assign_map[mode], read_in_yaml)
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(read_in_yaml)
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        else:
            msg = "<mode> = '{}' unrecognized! - says {}.{}".format(mode, self.ccn, cmn)
            lg.critical(msg)
            raise Exception(msg)
        
    def write_yaml(self, mode: str = "utxo"):
        """=== Method name: write_yaml =================================================================================
        Method writes data to yaml file.
        ========================================================================================== by Sziller ==="""
        cmn = inspect.currentframe().f_code.co_name  # current class name

        if mode not in list(self.path_map.keys()):
            lg.critical("<mode> = '{}' unrecognized! - says {}.{}".format(mode, self.ccn, cmn))
        yaml_path = os.getenv(self.path_map[mode])
        with open(yaml_path, 'w') as outfile:
            yaml.dump(getattr(self, self.assign_map[mode]), outfile, default_flow_style=False)
        
    def export_utxoset_to_db(self, export_session = ""):
        export_session = sqla.createSession(db_path=os.getenv("DB_PATH_VISOR"), style=os.getenv("DB_STYLE_VISOR"))
        print("IN")
        for _ in self.utxo_set:
            print(_)
        sqla.ADD_rows_to_table(primary_key="utxo_id",
                               data_list=self.utxo_set,
                               db_table="utxoset",
                               session_in=export_session)

    def read_db(self):
        """=== Method name: read_db ====================================================================================
        Method reads in UTXO set from yaml file.
        ========================================================================================== by Sziller ==="""
        self.utxo_set = sqla.QUERY_entire_table(ordered_by="addresses",
                                                db_table=os.getenv("DB_ID_TABLE_UTXO"),
                                                session_in=self.session_in)

    def extract_uxto_set_dict(self):
        """=== Method name: extract_uxto_id_set ========================================================================
        Once self.utxo_set is given, this script extracts the UtxoId's from it:
        ========================================================================================== by Sziller ==="""
        self.utxo_set_dict = {}
        for utxo in self.utxo_set:
            utxo_id = models.UtxoId(utxo["txid"], utxo["n"])
            self.utxo_set_dict["{}".format(utxo_id)] = utxo
    
    def extraxt_address_set(self):
        address_list = [_["address"] for _ in self.utxo_set]
        self.address_set = set(address_list)
        
    def extract_total_balance(self):
        value_in_btc = sum([_["value"] for _ in self.utxo_set])
        self.balance_total = units.bitcoin_unit_converter(value=value_in_btc,
                                                          unit_in="btc",
                                                          unit_out=os.getenv("UNIT_BASE"))
        
    def extract_utxototal_balance_by_utxo_set_dict(self):
        """=== Method name: extract_total_balance_by_utxo_set_dict =======================================================
        ========================================================================================== by Sziller ==="""
        pass
        
    def filter_balance_per_address(self):
        self.sums_per_address_dict = {addr: 0 for addr in self.address_set}
        for utxo in self.utxo_set:
            self.sums_per_address_dict[utxo["address"]] += utxo["sat_value"]
        
    def evaluate(self):
        print("===============================================")
        for k, v in self.sums_per_address_dict.items():
            print("{}: {:8>.8}".format(k, v))
    
    def bc_query_utxoset_by_utxoidset(self):
        """=== Method name: bc_query_utxoset_by_utxoidset ==============================================================
        Using Local Node, method fills in self.utxo_set variable based on self.utxo_set_dict
        ========================================================================================== by Sziller ==="""
        self.utxo_set = []
        for utxoid in self.utxo_set_dict:
            utxo_id_obj = models.UtxoId.construct_from_string(utxoid)
            node_used = BtcNode.Node(is_rpc=True, dotenv_path=self.dotenv_path)
            tx_data = node_used.nodeop_getrawtransaction(tx_hash=utxo_id_obj.txid,
                                                         verbose=1)
            current_bc_utxo = tx_data['vout'][utxo_id_obj.n]
            current_bc_utxo["utxo_id"] = "{}".format(utxo_id_obj)
            current_bc_utxo["txid"] = "{}".format(utxo_id_obj.txid)
            self.utxo_set.append(current_bc_utxo)


if __name__ == "__main__":
    # NOTSET=0, DEBUG=10, INFO=20, WARN=30, ERROR=40, CRITICAL=50
    logging.basicConfig(filename="../log/UtxoManager.log", level=logging.NOTSET, filemode="w",
                        format="%(asctime)s [%(levelname)8s]: %(message)s", datefmt='%y%m%d %H:%M:%S')
    lg.warning("START: {:>85} <<<".format('__name__ == "__main__" namespace: UtxoManager.py'))
    bnc = UTXOManager()
    pass
    
    
    

    

    # summarize(UTXO)

    # uncomment:
    # from btc_sziller_Class_package import BaseClasses as BC
    #
    # counter_spec = 0
    # counter_all = 0
    # act_addr = "19zohsYZfQX6TG9FjCeD8FW21q3yHj6KWA"
    # for _ in UTXO:
    #     counter_all += 1
    #     if _['address'] == act_addr: counter_spec += 1
    #
    # amount_list_spec = [_["sat_value"] for _ in UTXO if _["address"] == act_addr]
    # amount_list_all = [_["sat_value"] for _ in UTXO]
    # amount_spec = sum(amount_list_spec)
    # amount_all = sum(amount_list_all)
    # print("Nr of UTXO for address {:>40} - {}".format(act_addr, counter_spec))
    # print("Nr of UTXO in set      {:>40} - {}".format(" ", counter_all))
    # print("Balance of address     {:>40} - {}".format(act_addr, int(BC.bitcoin_unit_converter(value=amount_spec, unit_in='btc', unit_out="sat"))))
    # print("Balance of UTXOset     {:>40} - {}".format(" ", int(BC.bitcoin_unit_converter(value=amount_all, unit_in='btc', unit_out="sat"))))
